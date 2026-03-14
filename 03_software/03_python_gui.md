# Python GUI V6 Architecture

**Purpose:** Document the AERIS-10 Python GUI V6 (`GUI_V6.py`) architecture, including all dataclasses, USB communication, signal processing design (clustering and tracking), and display rendering. Explicitly identifies which components are complete implementations and which are stubs.

**Scope:** This document covers `GUI_V6.py` only. GUI versions V1 through V5 are explicitly excluded from documentation per project requirements.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [USB Protocol](04_usb_protocol.md) -- FT601 packet format and STM32 CDC protocol

---

## 1. Architecture Overview

GUI V6 is a Python tkinter application that provides real-time radar data visualization and system control for the AERIS-10 radar. The application connects to two USB interfaces -- FT601 (radar data from FPGA) and STM32 CDC (GPS/telemetry and commands) -- and displays range-Doppler data, target information, and map overlays.

### 1.1 Data Flow

```
FT601 USB 3.0                     STM32 USB CDC
     |                                  |
     v                                  v
FT601Interface                  STM32USBInterface
     |                                  |
     v                                  |
USBPacketParser [STUB]                  |
     |                                  |
     v                                  |
RadarPacketParser [STUB]                |
     |                                  |
     v                                  v
RadarProcessor [STUB]             GPSData (parsed)
     |                                  |
     +----------------------------------+
     |
     v
RadarGUI (tkinter + matplotlib display)
     |
     v
MapGenerator [STUB]
```

Data flows from the FT601 USB 3.0 interface through a chain of parsing and processing classes before reaching the GUI display. **The parsing and processing chain is currently stub implementations** (`pass` bodies), meaning radar data is read from USB but not processed end-to-end. The FT601Interface class itself is fully implemented and functional.

### 1.2 Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `tkinter` | stdlib | Main GUI framework |
| `matplotlib` | >= 3.0 | Embedded plot rendering (range-Doppler display) |
| `numpy` | >= 1.20 | Numerical computation |
| `scipy` | >= 1.7 | Signal processing utilities |
| `scikit-learn` | >= 1.0 | DBSCAN clustering (imported but unused -- stub) |
| `filterpy` | >= 1.4 | Kalman filter (imported but unused -- stub) |
| `pyftdi` | >= 0.54 | FT601 USB 3.0 communication (primary) |
| `pyusb` | >= 1.2 | Direct USB access (fallback) |
| `crcmod` | >= 1.7 | CRC computation |

---

## 2. Implementation Status

> **CRITICAL:** The following table clearly marks each class as complete or stub. Engineers must consult this table before assuming any component is functional.

| Class | Status | Lines | Description |
|-------|--------|-------|-------------|
| `RadarTarget` | **Complete** | Dataclass | Detected target data structure with all physical fields |
| `RadarSettings` | **Complete** | Dataclass | System configuration parameters matching STM32 `RadarSettings.h` |
| `GPSData` | **Complete** | Dataclass | GPS/IMU sensor data from STM32 |
| `FT601Interface` | **Complete** | ~250 | FT601 USB 3.0 communication with pyftdi and direct USB fallback |
| `RadarGUI` | **Complete** | ~200 | tkinter main window with matplotlib, device selection, start/stop |
| `RadarProcessor` | **Stub** | `pass` | Intended: DBSCAN clustering + Kalman tracking |
| `USBPacketParser` | **Stub** | `pass` | Intended: Parse raw USB bytes into structured packets |
| `RadarPacketParser` | **Stub** | `pass` | Intended: Parse radar-specific packet fields |
| `MapGenerator` | **Stub** | `pass` | Intended: Google Maps overlay for target display |
| `STM32USBInterface` | **Not defined** | -- | Referenced in `RadarGUI.__init__()` but class definition is not in `GUI_V6.py` |

**Implication:** The GUI can connect to the FT601 and STM32 USB devices and display its interface, but the end-to-end data processing pipeline from USB packet to displayed target is not functional due to stub classes in the parsing/processing chain.

---

## 3. RadarTarget Dataclass

The `RadarTarget` dataclass represents a single detected radar target with all fields needed for display and tracking.

```python
@dataclass
class RadarTarget:
    id: int
    range: float
    velocity: float
    azimuth: int
    elevation: int
    latitude: float = 0.0
    longitude: float = 0.0
    snr: float = 0.0
    timestamp: float = 0.0
    track_id: int = -1
```

### 3.1 Field Definitions

| Field | Type | Units | Standard Symbol | Description |
|-------|------|-------|----------------|-------------|
| `id` | `int` | -- | -- | Unique target identifier within current scan |
| `range` | `float` | m | $R$ | Slant range from radar to target (see [Symbol Table](../00_notation/symbol_table.md#range-and-velocity)) |
| `velocity` | `float` | m/s | $v$ | Radial velocity (positive = approaching) |
| `azimuth` | `int` | deg | $\theta$ | Azimuth angle from radar boresight (beam steering angle, see [Symbol Table](../00_notation/symbol_table.md#antenna-and-beamforming)) |
| `elevation` | `int` | deg | -- | Elevation beam position index |
| `latitude` | `float` | decimal deg | -- | Target GPS latitude after coordinate transform |
| `longitude` | `float` | decimal deg | -- | Target GPS longitude after coordinate transform |
| `snr` | `float` | dB | $\text{SNR}$ | Signal-to-noise ratio at detection |
| `timestamp` | `float` | s | -- | Detection timestamp (epoch seconds) |
| `track_id` | `int` | -- | -- | Track association ID from Kalman tracker (-1 = untracked) |

The coordinate fields (`latitude`, `longitude`) are populated by the coordinate transform that converts radar-relative spherical coordinates $(R, \theta, \text{elevation})$ to GPS-absolute coordinates. See [GPS/IMU Coordinate Transforms](../02_hardware/09_gps_imu_transforms.md) for the transform mathematics.

---

## 4. RadarSettings Dataclass

The `RadarSettings` dataclass holds all configurable radar system parameters. These mirror the STM32 `RadarSettings` class (in `RadarSettings.h`) and are sent to the STM32 via USB CDC when the operator starts the radar.

```python
@dataclass
class RadarSettings:
    system_frequency: float = 10e9
    chirp_duration_1: float = 30e-6
    chirp_duration_2: float = 0.5e-6
    chirps_per_position: int = 32
    freq_min: float = 10e6
    freq_max: float = 30e6
    prf1: float = 1000
    prf2: float = 2000
    max_distance: float = 50000
    map_size: float = 50000
```

### 4.1 Field Definitions

| Field | Type | Default | Standard Symbol | Description |
|-------|------|---------|----------------|-------------|
| `system_frequency` | `float` | `10e9` | $f_c$ | Center frequency (Hz). **Note:** Default is `10e9` (10.0 GHz); canonical value is $f_c = 10.5~\text{GHz}$ per [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing). This discrepancy is documented as a known issue. |
| `chirp_duration_1` | `float` | `30e-6` | $T_{c,1}$ | Long chirp duration (s) |
| `chirp_duration_2` | `float` | `0.5e-6` | $T_{c,2}$ | Short chirp duration (s) |
| `chirps_per_position` | `int` | `32` | $M$ | Number of chirps per CPI per beam position |
| `freq_min` | `float` | `10e6` | -- | Minimum frequency for sweep range (Hz) |
| `freq_max` | `float` | `30e6` | -- | Maximum frequency for sweep range (Hz) |
| `prf1` | `float` | `1000` | -- | Display update rate for long chirp mode (Hz). **Not** the chirp-level PRF $f_{r,1}$; see [Parameter Table](../00_notation/parameter_table.md#system-level-derivedtbd) for clarification. |
| `prf2` | `float` | `2000` | -- | Display update rate for short chirp mode (Hz). Same caveat as `prf1`. |
| `max_distance` | `float` | `50000` | $R_\text{max}$ | Maximum display range (m). This is a display limit, not the physical maximum detection range. |
| `map_size` | `float` | `50000` | -- | Map display extent (m) |

> **Known issue:** The `system_frequency` default of `10e9` does not match the canonical center frequency $f_c = 10.5~\text{GHz}$ established in the parameter table. The firmware wavelength constant (`wavelength = 0.02857` m) corresponds to 10.5 GHz. This GUI default should be corrected to `10.5e9`.

---

## 5. GPSData Dataclass

The `GPSData` dataclass holds position and attitude data received from the STM32 GPS/IMU subsystem.

```python
@dataclass
class GPSData:
    latitude: float
    longitude: float
    altitude: float
    pitch: float
    timestamp: float
```

| Field | Type | Units | Description |
|-------|------|-------|-------------|
| `latitude` | `float` | decimal degrees | Platform latitude from GPS receiver |
| `longitude` | `float` | decimal degrees | Platform longitude from GPS receiver |
| `altitude` | `float` | m | Platform altitude (barometric or GPS) |
| `pitch` | `float` | degrees | Platform pitch angle from IMU complementary filter |
| `timestamp` | `float` | s | Time of GPS fix (epoch seconds) |

These fields correspond to the `GPS_Data_t` structure on the STM32 side (see [USB Protocol -- GPS Binary Packet](04_usb_protocol.md#41-gps-binary-packet-format)). The `pitch` field is used for elevation correction when converting radar-relative target coordinates to world coordinates. See [GPS/IMU Coordinate Transforms](../02_hardware/09_gps_imu_transforms.md) for the complementary filter and coordinate transform chain.

---

## 6. FT601Interface Class

The `FT601Interface` class provides USB 3.0 communication with the FT601 bridge IC for radar data reception. This is a **complete implementation** with two access methods.

### 6.1 Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `channel` | `0` | Default FT601 channel |
| `fifo_mode` | `True` | Synchronous FIFO operation |
| `buffer_size` | `512` | Optimal read/write buffer size (bytes) |

### 6.2 Device Enumeration

The `list_devices()` method scans USB for FT601 devices:

- **VID/PID pairs:** `0x0403:0x6030` (FT601), `0x0403:0x6031` (FT601Q)
- Returns a list of device dictionaries with `description`, `vendor_id`, `product_id`, `url`, `serial`
- Falls back to mock device list if USB enumeration fails (for development/testing)

### 6.3 Connection Methods

| Method | Library | Description |
|--------|---------|-------------|
| `open_device(device_url)` | `pyftdi` | Primary method. Opens via FTDI URL, configures Synchronous FIFO mode (`BitMode.SYNCFF`), sets 100 MHz clock, 2 ms latency timer. |
| `open_device_direct(device_info)` | `pyusb` | Fallback method. Opens via direct USB, finds bulk endpoints EP1/EP2 IN and OUT. Used when `pyftdi` is unavailable or fails. |

The GUI tries `open_device_direct()` first, falling back to `open_device()` if direct USB access fails.

### 6.4 Data Transfer

| Method | Description |
|--------|-------------|
| `read_data(bytes_to_read=None)` | Read from FT601. Aligns to 32-bit boundary. Default: 512 bytes (pyftdi) or 512 bytes (direct USB with 100 ms timeout). |
| `write_data(data)` | Write to FT601. Pads to 32-bit alignment. Sends in 512-byte chunks for direct USB. |
| `configure_burst_mode(enable)` | Enable/disable burst mode. When enabled, sets chunk size to 4096 bytes for higher throughput. |

### 6.5 Connection Lifecycle

```
list_devices() -> open_device() or open_device_direct() -> read_data() / write_data() -> close()
```

The `close()` method releases the FTDI handle or disposes USB resources. The `is_open` flag tracks connection state.

For the FT601 packet format that this class reads, see [USB Protocol -- FPGA-to-Host Packet Format](04_usb_protocol.md#3-fpga-to-host-packet-format).

---

## 7. RadarProcessor (Designed Interface -- Stub)

> **Status: STUB.** The `RadarProcessor` class body is `pass`. The following documents the **designed intent** from the import list and class name, not a working implementation.

The `RadarProcessor` is intended to perform two operations on detected targets:

### 7.1 DBSCAN Clustering

The GUI imports `sklearn.cluster.DBSCAN` for spatial clustering of radar detections.

**Intended purpose:** Group individual CFAR detections into target clusters. Multiple adjacent range-Doppler cells may trigger on a single physical target; DBSCAN groups these into unified target reports.

**DBSCAN parameters (design-level):**

$$
\text{cluster} = \text{DBSCAN}(\varepsilon, m_\text{min}, d(\mathbf{x}_i, \mathbf{x}_j)) \tag{SW-2}
$$

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| `eps` | $\varepsilon$ | Spatial neighborhood radius -- maximum distance between two points to be considered neighbors |
| `min_samples` | $m_\text{min}$ | Minimum number of detections to form a cluster (reject isolated false alarms) |
| Distance metric | $d(\mathbf{x}_i, \mathbf{x}_j)$ | Euclidean distance in range-velocity space, potentially with range/velocity scaling |

For the underlying detection theory that produces the CFAR detections clustered by DBSCAN, see [Detection Theory](../01_physics/04_detection_theory.md).

### 7.2 Kalman Filter Tracking

The GUI imports `filterpy.kalman.KalmanFilter` for target tracking across consecutive scans.

**Intended state model:**

$$
\mathbf{x}_k = \begin{bmatrix} x \\ y \\ v_x \\ v_y \end{bmatrix}, \quad
\mathbf{z}_k = \begin{bmatrix} x_\text{meas} \\ y_\text{meas} \end{bmatrix} \tag{SW-3}
$$

| Component | Description |
|-----------|-------------|
| State vector $\mathbf{x}_k$ | 2D position $(x, y)$ and velocity $(v_x, v_y)$ in Cartesian |
| Measurement vector $\mathbf{z}_k$ | Measured position from DBSCAN cluster centroid |
| Process noise | Models target acceleration uncertainty |
| Measurement noise | Models radar range/angle measurement error |

The Kalman filter would assign `track_id` values to `RadarTarget` instances, enabling track continuity across scans. A `track_id` of -1 indicates an untracked detection.

> **Note:** Since `RadarProcessor` is a stub, no DBSCAN clustering or Kalman tracking is performed. All imported signal processing libraries (`sklearn`, `filterpy`) are loaded but unused at runtime.

---

## 8. RadarGUI Class

The `RadarGUI` class is the main application window, built on tkinter with embedded matplotlib plots. This is a **complete implementation**.

### 8.1 Window Configuration

| Property | Value |
|----------|-------|
| Title | "Advanced Radar System GUI - FT601 USB 3.0" |
| Geometry | 1400 x 900 pixels |
| Theme | Custom dark theme (`clam` ttk base) |

### 8.2 Dark Theme

The GUI uses a consistent dark color scheme:

| Element | Color |
|---------|-------|
| Background | `#2b2b2b` |
| Foreground text | `#e0e0e0` |
| Accent | `#3c3f41` |
| Highlight | `#4e5254` |
| Button | `#3c3f41` (hover: `#4e5254`) |

### 8.3 Main Tab Controls

The main tab provides:

- **STM32 USB Device** dropdown: Select the virtual COM port for STM32 CDC communication
- **FT601 USB 3.0 Device** dropdown: Select the FT601 radar data device
- **Burst Mode** checkbox: Enable FT601 burst mode for higher throughput (default: on)
- **Refresh Devices** button: Re-enumerate available USB devices
- **Start Radar** / **Stop Radar** buttons: Begin or halt radar operation
- **GPS display**: Shows current latitude, longitude, altitude
- **Pitch display**: Shows current platform pitch angle
- **Status bar**: Shows connection state and operational mode

### 8.4 Start/Stop Sequence

**Start sequence (`start_radar()`):**
1. Open STM32 USB device from dropdown selection
2. Open FT601 device (try direct USB first, fallback to pyftdi)
3. Configure burst mode if checkbox is enabled
4. Send start flag to STM32 via `stm32_usb_interface.send_start_flag()`
5. Apply settings via `apply_settings()`
6. Set `running = True`, update button states

**Stop sequence (`stop_radar()`):**
1. Set `running = False`
2. Close STM32 and FT601 interfaces
3. Update button states and status label

### 8.5 Radar Data Processing Loop

The `process_radar_data()` method runs in a background thread:

1. Read data from FT601 in 4096-byte chunks
2. Append to byte buffer
3. Attempt to parse packets from buffer (minimum 8 bytes)
4. On successful parse: call `process_radar_packet()`, increment `received_packets`
5. On parse failure: shift buffer by 1 byte to resynchronize
6. Sleep 100 ms when no data available or not running

### 8.6 Thread Architecture

| Thread | Purpose | Control |
|--------|---------|---------|
| `radar_thread` | FT601 data reading and packet parsing | `self.running` flag |
| `gps_thread` | STM32 GPS/telemetry polling | `self.running` flag |
| Main thread | tkinter event loop, GUI updates | `root.mainloop()` |

Data is passed between threads via `queue.Queue` instances (`radar_data_queue`, `gps_data_queue`).

---

## 9. USBPacketParser and RadarPacketParser (Stubs)

> **Status: STUB.** Both classes have `pass` bodies.

| Class | Intended Purpose |
|-------|-----------------|
| `USBPacketParser` | Parse raw USB byte stream into structured packet objects, handling byte alignment and header/footer detection |
| `RadarPacketParser` | Extract radar-specific fields (range profile, Doppler I/Q, detection flag) from structured packets |

These classes are intended to implement the packet parsing logic described in [USB Protocol -- FPGA-to-Host Packet Format](04_usb_protocol.md#3-fpga-to-host-packet-format). The `process_radar_data()` method in `RadarGUI` calls `self.radar_packet_parser.parse_packet()`, which currently returns `None` (stub), causing the processing loop to continuously shift the buffer without extracting data.

---

## 10. MapGenerator (Designed Interface -- Stub)

> **Status: STUB.** The `MapGenerator` class body is `pass`.

**Intended interface:**

| Method | Description |
|--------|-------------|
| `generate_map(targets, gps_origin)` | Generate a Google Maps overlay with target markers positioned relative to the radar's GPS coordinates |

The GUI holds a `google_maps_api_key` field (default: `"YOUR_GOOGLE_MAPS_API_KEY"`) and a `map_file_path` for temporary HTML file storage. The intended implementation would use the Google Maps Static API or JavaScript API to render targets on a geographic map, using the coordinate transform from [GPS/IMU Coordinate Transforms](../02_hardware/09_gps_imu_transforms.md) to convert radar-relative positions to latitude/longitude.

---

## 11. Data Flow Summary

The end-to-end data path from USB reception to GUI display, with stub breaks noted:

| Stage | Component | Status | Input | Output |
|-------|-----------|--------|-------|--------|
| 1 | `FT601Interface.read_data()` | Complete | USB 3.0 bulk endpoint | Raw bytes |
| 2 | `RadarPacketParser.parse_packet()` | **STUB** | Raw bytes | None (should return parsed packet) |
| 3 | `USBPacketParser` | **STUB** | -- | -- |
| 4 | `RadarProcessor` (DBSCAN + Kalman) | **STUB** | Parsed detections | Should return `RadarTarget` list |
| 5 | `RadarGUI` display update | Complete | `RadarTarget` list | matplotlib plots |
| 6 | `MapGenerator.generate_map()` | **STUB** | `RadarTarget` list + GPS | Should return HTML map |

**Chain break:** The pipeline breaks at Stage 2. Raw USB data is read successfully by the FT601Interface, but `RadarPacketParser.parse_packet()` returns `None`, preventing any data from reaching the display or map rendering stages.

To make the GUI fully operational, a developer would need to implement:
1. `RadarPacketParser` -- parse `0xAA`-framed packets per [USB Protocol](04_usb_protocol.md#3-fpga-to-host-packet-format)
2. `USBPacketParser` -- handle byte stream synchronization
3. `RadarProcessor` -- DBSCAN clustering and Kalman tracking
4. `MapGenerator` -- Google Maps rendering (optional for basic operation)

---

## 12. References

- [Symbol Table](../00_notation/symbol_table.md) -- standard symbol definitions ($R$, $v$, $\theta$, $\text{SNR}$, $f_c$, $T_{c,1}$, $T_{c,2}$, $M$, $R_\text{max}$)
- [Parameter Table](../00_notation/parameter_table.md) -- canonical system parameter values
- [USB Protocol](04_usb_protocol.md) -- FT601 packet format and STM32 CDC protocol
- [GPS/IMU Coordinate Transforms](../02_hardware/09_gps_imu_transforms.md) -- radar-to-world coordinate transform for target positioning
- [Detection Theory](../01_physics/04_detection_theory.md) -- CFAR detection producing inputs to DBSCAN clustering
- [Antenna & Beamforming](../02_hardware/04_antenna_beamforming.md) -- beam steering angle to azimuth mapping
- scikit-learn DBSCAN documentation -- clustering algorithm reference
- FilterPy documentation -- Kalman filter implementation reference
