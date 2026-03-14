# USB Interface Protocol

**Purpose:** Specify the AERIS-10 USB communication protocol completely enough that an engineer can implement a new host-side client without reading the FPGA Verilog or STM32 C++ source code. Covers all three communication paths: FPGA radar data (FT601 USB 3.0), STM32 telemetry (USB CDC), and host commands (USB CDC).

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Pipeline](01_fpga_pipeline.md) -- signal processing chain producing USB output data

---

## 1. Protocol Overview

The AERIS-10 radar system uses three independent USB communication paths between the embedded hardware and the host PC:

| Path | Direction | Transport | Controller | Data |
|------|-----------|-----------|------------|------|
| Radar data | FPGA -> Host | USB 3.0 bulk transfer | FT601 | Range profile, Doppler I/Q, CFAR detection |
| GPS/telemetry | STM32 -> Host | USB CDC (virtual COM) | STM32F4 USB-FS | GPS position, pitch, altitude, system status |
| Commands | Host -> STM32 | USB CDC (virtual COM) | STM32F4 USB-FS | Start/stop flag, radar settings |

The FT601 path carries high-bandwidth radar data at the chirp repetition rate. The STM32 CDC path carries low-bandwidth control and telemetry. These two paths are electrically and logically independent -- the FPGA connects to the host via the FT601 USB 3.0 bridge IC, while the STM32 connects via its built-in USB Full-Speed peripheral.

---

## 2. FT601 Physical Layer

### 2.1 FT601 Slave FIFO Interface

The FT601 USB 3.0 bridge IC operates in **Slave FIFO mode**, where the FPGA acts as the bus master controlling data transfers to/from the host PC.

| Parameter | Value | Source |
|-----------|-------|--------|
| Data bus width | 32 bits | `ft601_data[31:0]` in `usb_data_interface.v` |
| Clock source | `ft601_clk_in` (100 MHz) | FT601 on-board oscillator |
| Clock relationship | Asynchronous to FPGA system 100 MHz | Separate oscillator (see [FPGA Board](../02_hardware/05_fpga_board.md)) |
| Max burst size | 512 bytes | `FT601_BURST_SIZE` parameter |
| USB vendor ID | `0x0403` | FTDI standard VID |
| USB product ID | `0x6030` (FT601) or `0x6031` (FT601Q) | Per FT601 datasheet |

### 2.2 Signal Descriptions

| Signal | Direction | Active | Description |
|--------|-----------|--------|-------------|
| `ft601_data[31:0]` | Bidirectional | -- | 32-bit data bus with tri-state control (`ft601_data_oe`) |
| `ft601_be[1:0]` | FPGA -> FT601 | -- | Byte enable: `2'b01` = lower byte only, `2'b11` = full 32-bit word |
| `ft601_wr_n` | FPGA -> FT601 | Low | Write strobe -- asserted to push data into FT601 TX FIFO |
| `ft601_rd_n` | FPGA -> FT601 | Low | Read strobe -- asserted to pull data from FT601 RX FIFO |
| `ft601_oe_n` | FPGA -> FT601 | Low | Output enable for FT601 data bus direction |
| `ft601_txe` | FT601 -> FPGA | High | TX FIFO empty flag -- when low, FIFO has space for writes |
| `ft601_rxf` | FT601 -> FPGA | High | RX FIFO full flag -- when low, data available for reads |
| `ft601_siwu_n` | FPGA -> FT601 | Low | Send Immediate / Wake Up signal |
| `ft601_clk_in` | FT601 -> FPGA | -- | Reference clock from FT601 (100 MHz) |
| `ft601_clk_out` | FPGA -> FT601 | -- | Optional clock output (system clock / 2) |

### 2.3 Data Bus Direction Control

The 32-bit data bus is bidirectional with tri-state control:

```
ft601_data = ft601_data_oe ? ft601_data_out : 32'hzzzz_zzzz
```

The FPGA drives the bus (`ft601_data_oe = 1`) only during active write states. In IDLE and WAIT_ACK states, the bus is released to high-impedance.

---

## 3. FPGA-to-Host Packet Format

### 3.1 State Machine

The FPGA transmits radar data packets using a seven-state machine clocked on `ft601_clk_in` (from `usb_data_interface.v`):

```
IDLE -> SEND_HEADER -> SEND_RANGE_DATA -> SEND_DOPPLER_DATA ->
        SEND_DETECTION_DATA -> SEND_FOOTER -> WAIT_ACK -> IDLE
```

**Trigger condition:** The state machine exits IDLE when any of `range_valid`, `doppler_valid`, or `cfar_valid` is asserted. All subsequent states wait for `ft601_txe` to be low (FT601 TX FIFO has space) before writing.

### 3.2 Packet Structure

Each radar data packet contains the following fields, transmitted sequentially:

| Field | Transfers | Byte Enable | Content | Total Bits |
|-------|-----------|-------------|---------|------------|
| Header | 1 | `BE=01` | `{24'b0, 0xAA}` -- constant header marker | 8 valid |
| Range profile | 4 | `BE=11` | 32-bit range bin magnitudes, shifted across 4 transfers | 4 x 32 = 128 |
| Doppler I/Q | 4 | `BE=11` | Packed `{doppler_real[15:0], doppler_imag[15:0]}`, shifted across 4 transfers | 4 x 32 = 128 |
| Detection flag | 1 | `BE=01` | `{24'b0, 7'b0, cfar_detection}` -- single-bit CFAR result | 1 valid |
| Footer | 1 | `BE=01` | `{24'b0, 0x55}` -- constant footer marker | 8 valid |

**Total transfers per packet:** 11 (1 header + 4 range + 4 Doppler + 1 detection + 1 footer)

### 3.3 Header (0xAA)

The header byte `0xAA` marks the start of every radar data packet. It is transmitted as the least-significant byte of the 32-bit data bus with `BE=01` (only lower byte valid). A host parser should scan for this byte to synchronize to the packet boundary.

```verilog
ft601_data_out <= {24'b0, 8'hAA};   // Header = 0xAA
ft601_be <= 2'b01;                    // Lower byte valid
```

### 3.4 Range Profile Data

The 32-bit `range_profile` input is transmitted across four 32-bit transfers with shifting:

| Transfer | Data | Description |
|----------|------|-------------|
| 0 | `range_profile[31:0]` | Full 32-bit word, unshifted |
| 1 | `{range_profile[23:0], 8'h00}` | Shifted left 8 bits |
| 2 | `{range_profile[15:0], 16'h0000}` | Shifted left 16 bits |
| 3 | `{range_profile[7:0], 24'h000000}` | Shifted left 24 bits |

All four transfers use `BE=11` (full 32-bit word valid).

### 3.5 Doppler I/Q Data

Doppler data packs real (I) and imaginary (Q) components, each 16-bit signed integers, across four 32-bit transfers:

| Transfer | Data | Description |
|----------|------|-------------|
| 0 | `{doppler_real[15:0], doppler_imag[15:0]}` | I in upper half, Q in lower half |
| 1 | `{doppler_imag[15:0], doppler_real[15:8], 8'h00}` | Cross-boundary packing |
| 2 | `{doppler_real[7:0], doppler_imag[15:8], 16'h0000}` | Cross-boundary packing |
| 3 | `{doppler_imag[7:0], 24'h000000}` | Final byte |

Doppler transfers are gated by `doppler_valid` in addition to `ft601_txe`. All four transfers use `BE=11`.

### 3.6 Detection Flag

A single-byte field containing the CFAR detection result:

```verilog
ft601_data_out <= {24'b0, 7'b0, cfar_detection};   // Bit 0 = detection
ft601_be <= 2'b01;                                   // Lower byte valid
```

- `cfar_detection = 1`: Target detected in the current range-Doppler cell
- `cfar_detection = 0`: No detection

This field is gated by `cfar_valid` -- the state machine waits for `cfar_valid` before proceeding.

> **Note:** The current FPGA implementation uses a simple magnitude threshold (`|I|+|Q| > 10000`) rather than a true CA-CFAR algorithm. See [FPGA Pipeline](01_fpga_pipeline.md) for details.

### 3.7 Footer (0x55)

The footer byte `0x55` marks the end of the packet. A host parser should verify this byte to confirm packet integrity. After the footer, the state machine transitions to WAIT_ACK (one clock cycle of bus release) and then returns to IDLE.

```verilog
ft601_data_out <= {24'b0, 8'h55};   // Footer = 0x55
ft601_be <= 2'b01;                    // Lower byte valid
```

### 3.8 Packet Validation (Analyzer Module)

The companion `usb_packet_analyzer.v` module provides an independent verification path for received packets. It checks:

1. Header byte matches `0xAA` (in `usb_data[31:24]` or `usb_data[7:0]` depending on byte position)
2. Footer byte matches `0x55`
3. Maintains `error_count` register for mismatched footers
4. Asserts `packet_valid` for one clock cycle on successful packet reception

This module is intended for FPGA-side loopback testing and is not part of the host-facing protocol.

---

## 4. STM32-to-Host Protocol (GPS/Telemetry)

The STM32 communicates with the host PC over USB CDC (virtual COM port) using the STM32F4 USB Full-Speed peripheral. The firmware uses the STM32 HAL CDC class (`usbd_cdc_if.h`) for USB communication.

### 4.1 GPS Binary Packet Format

The `GPS_SendBinaryToGUI()` function (in `gps_handler.cpp`) transmits the platform's GPS position and pitch angle to the host in a 30-byte binary packet:

| Offset | Size | Type | Byte Order | Content |
|--------|------|------|------------|---------|
| 0 | 4 | char[4] | -- | Header: `"GPSB"` (ASCII `0x47 0x50 0x53 0x42`) |
| 4 | 8 | double | Big-endian | Latitude (decimal degrees, `GPS_Data_t.latitude`) |
| 12 | 8 | double | Big-endian | Longitude (decimal degrees, `GPS_Data_t.longitude`) |
| 20 | 4 | float | Big-endian | Altitude (meters, `GPS_Data_t.altitude`) |
| 24 | 4 | float | Big-endian | Pitch angle (degrees, `GPS_Data_t.pitch`) |
| 28 | 2 | uint16 | Big-endian | Checksum: sum of bytes [0..27] |

**Total packet size:** 30 bytes

The `GPS_Data_t` structure (defined in `gps_handler.h`) contains:

```c
typedef struct {
    double latitude;     // Decimal degrees
    double longitude;    // Decimal degrees
    float altitude;      // Meters
    float pitch;         // Degrees
    uint32_t timestamp;  // HAL_GetTick() value (milliseconds since boot)
} GPS_Data_t;
```

> **Note:** The `timestamp` field from `GPS_Data_t` is not transmitted in the binary packet; only latitude, longitude, altitude, and pitch are sent.

### 4.2 System Status Messages

The STM32 also sends ASCII status strings to the host via `CDC_Transmit_FS()`. The `getSystemStatusForGUI()` function formats a human-readable status string covering system initialization state, sensor readings, and error conditions.

### 4.3 GPS Text Protocol (Alternative)

The `GPS_SendToGUI()` function provides an alternative ASCII format:

```
GPS:lat,lon,alt\r\n
```

This is a simpler format used for debugging. The binary protocol (`GPS_SendBinaryToGUI`) is preferred for production use due to its fixed-length structure and checksum.

---

## 5. Host-to-STM32 Commands

The host PC sends commands to the STM32 over the same USB CDC interface. The `USBHandler` class (in `USBHandler.h`) manages incoming USB data with a three-state protocol:

### 5.1 USBHandler State Machine

```
WAITING_FOR_START -> RECEIVING_SETTINGS -> READY_FOR_DATA
```

| State | Description | Transition |
|-------|-------------|------------|
| `WAITING_FOR_START` | Idle, waiting for start flag from host | Start flag received -> `RECEIVING_SETTINGS` |
| `RECEIVING_SETTINGS` | Parsing `RadarSettings` from USB data | Settings parsed and valid -> `READY_FOR_DATA` |
| `READY_FOR_DATA` | Settings applied, radar operation begins | `reset()` called -> `WAITING_FOR_START` |

Incoming USB data is routed through the STM32 HAL CDC receive callback:

```c
void CDC_Receive_FS(uint8_t* Buf, uint32_t *Len) {
    usbHandler.processUSBData(Buf, *Len);
    USBD_CDC_SetRxBuffer(&hUsbDeviceFS, &usb_rx_buffer[0]);
    USBD_CDC_ReceivePacket(&hUsbDeviceFS);
}
```

### 5.2 Start/Stop Protocol

The host sends a start flag to initiate radar operation. The firmware waits in a blocking loop:

```c
do {
    if (usbHandler.isStartFlagReceived() &&
        usbHandler.getState() == USBHandler::USBState::READY_FOR_DATA) {
        const RadarSettings& settings = usbHandler.getSettings();
        // Configure radar with received settings
    }
} while(!usbHandler.isStartFlagReceived());
```

The start flag must be sent before the radar begins its power-up and scanning sequence. Once received, the STM32 proceeds with RF power amplifier sequencing and radar loop execution.

### 5.3 RadarSettings Structure

The `RadarSettings` class (in `RadarSettings.h`) contains all configurable radar parameters sent from the host GUI to the STM32:

| Field | Type | Default | Standard Symbol | Description |
|-------|------|---------|----------------|-------------|
| `system_frequency` | `double` | -- | $f_c$ | Center frequency (Hz) |
| `chirp_duration_1` | `double` | -- | $T_{c,1}$ | Long chirp duration (s) |
| `chirp_duration_2` | `double` | -- | $T_{c,2}$ | Short chirp duration (s) |
| `chirps_per_position` | `uint32_t` | -- | $M$ | Chirps per beam position |
| `freq_min` | `double` | -- | -- | Minimum frequency (Hz) |
| `freq_max` | `double` | -- | -- | Maximum frequency (Hz) |
| `prf1` | `double` | -- | -- | Display update rate, long chirp (Hz) |
| `prf2` | `double` | -- | -- | Display update rate, short chirp (Hz) |
| `max_distance` | `double` | -- | $R_\text{max}$ | Maximum display range (m) |
| `map_size` | `double` | -- | -- | Map display size (m) |

The `parseFromUSB()` method deserializes binary USB data into this structure using `extractDouble()` and `extractUint32()` helper methods. After parsing, `validateSettings()` checks that all values are within acceptable bounds before the handler transitions to `READY_FOR_DATA`.

The USB receive buffer is 256 bytes (`MAX_BUFFER_SIZE` in `USBHandler.h`), which is sufficient for the full settings payload.

---

## 6. Streaming Protocol

### 6.1 Continuous Data Flow

During radar operation, the FPGA generates one USB data packet per chirp processing cycle. The data flow is:

1. **FPGA produces data:** Each chirp cycle produces range profile, Doppler I/Q, and CFAR detection outputs
2. **State machine packetizes:** The `usb_data_interface.v` state machine wraps the data in header/footer framing
3. **FT601 buffers:** The FT601 IC buffers packets in its internal FIFO before USB 3.0 bulk transfer
4. **Host reads in bulk:** The host application reads from the FT601 USB endpoint, typically in 512-byte or 4096-byte chunks

### 6.2 Data Rate Estimate

$$
R_\text{data} = \frac{N_\text{transfers} \times W_\text{bus}}{T_{r,1}} \tag{SW-1}
$$

where $N_\text{transfers} = 11$ transfers per packet, $W_\text{bus} = 32$ bits per transfer, and $T_{r,1}$ is the chirp PRI (see [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for values).

At the long chirp PRI of $T_{r,1} = 167~\mu\text{s}$:

- Transfers per second: $1 / T_{r,1} \approx 5988$ packets/s
- Bits per second: $5988 \times 11 \times 32 \approx 2.1~\text{Mbps}$

This is well within the FT601 USB 3.0 SuperSpeed bandwidth (5 Gbps theoretical, ~300 MBps practical).

### 6.3 Flow Control

The FPGA respects the FT601's flow control signals:

- **`ft601_txe` (TX FIFO empty):** The state machine checks `!ft601_txe` before every write. If the FT601 TX FIFO is full, the state machine stalls in the current state until space becomes available.
- **Back-pressure:** If the host does not read data fast enough, the FT601 FIFO fills, `ft601_txe` goes high, and the FPGA state machine pauses. No data is lost -- the FPGA waits until the host drains the FIFO.
- **No explicit ACK:** The `WAIT_ACK` state is a single-cycle bus-release transition, not a true acknowledgment protocol. The FPGA does not wait for host confirmation of packet receipt.

---

## 7. Implementing a New Client

To implement a new host-side client for the AERIS-10 radar data stream:

### 7.1 FT601 Radar Data (USB 3.0)

1. **Enumerate FT601 device:** Scan USB for VID `0x0403`, PID `0x6030` or `0x6031`
2. **Open and configure:** Set Synchronous FIFO mode, 100 MHz clock, 32-bit data bus
3. **Read data:** Perform bulk reads in chunks (512 or 4096 bytes recommended)
4. **Parse packets:**
   - Scan for header byte `0xAA`
   - Read 4 x 32-bit range transfers
   - Read 4 x 32-bit Doppler transfers (extract `doppler_real[15:0]` and `doppler_imag[15:0]`)
   - Read 1-byte detection flag (bit 0 = CFAR detection)
   - Verify footer byte `0x55`
   - Discard packet if footer mismatch
5. **Interpret data:**
   - Range profile: 32-bit magnitude values for each range bin
   - Doppler I/Q: signed 16-bit I and Q components for velocity estimation
   - Detection: boolean target-present indicator

### 7.2 STM32 Telemetry (USB CDC)

1. **Enumerate STM32 device:** Open the virtual COM port (VCP) exposed by the STM32 USB CDC class
2. **Receive GPS packets:** Parse 30-byte binary frames starting with `"GPSB"` header
3. **Verify checksum:** Sum bytes [0..27], compare with bytes [28..29] (big-endian uint16)
4. **Extract fields:** Latitude (double, offset 4), longitude (double, offset 12), altitude (float, offset 20), pitch (float, offset 24)

### 7.3 Host Commands (USB CDC)

1. **Send start flag:** Transmit the start flag byte sequence to trigger the STM32 start protocol
2. **Send settings:** Serialize `RadarSettings` fields as binary payload (doubles as IEEE 754, uint32 as little-endian)
3. **Wait for ready:** The STM32 will begin radar operation after receiving valid settings

### 7.4 Python Reference Implementation

The `FT601Interface` class in `GUI_V6.py` provides a reference implementation using two access methods:

- **Primary:** `pyftdi` library (`Ftdi.open_from_url()`, `set_bitmode(SYNCFF)`, `read_data()`)
- **Fallback:** `pyusb` direct USB access (`usb.core.find()`, endpoint read/write)

See [Python GUI V6](03_python_gui.md) for the complete class documentation.

---

## 8. References

- [Symbol Table](../00_notation/symbol_table.md) -- standard symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- chirp timing and system parameters
- [FPGA Pipeline](01_fpga_pipeline.md) -- signal processing chain producing USB output data
- [FPGA Board](../02_hardware/05_fpga_board.md) -- FT601 clock domain and hardware connection details
- FTDI FT601 Datasheet -- USB 3.0 to FIFO bridge IC specification
- STM32 USB CDC Application Note (AN4879) -- Virtual COM port implementation
