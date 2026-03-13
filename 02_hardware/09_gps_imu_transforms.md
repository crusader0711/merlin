# GPS/IMU Coordinate Transforms

**Purpose:** Document the AERIS-10 navigation subsystem that converts radar-relative detections (range, azimuth, elevation) into GPS-absolute coordinates for map display. Covers the GY-85 IMU sensor suite, complementary filter attitude estimation, magnetometer calibration, barometric altitude, and the complete radar-to-world coordinate transform chain.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Antenna & Beamforming](04_antenna_beamforming.md) -- beam position to steering angle mapping

---

## 1. Overview

The AERIS-10 navigation subsystem converts radar detections from the radar's local spherical coordinate frame (range, azimuth angle, elevation angle) into GPS-absolute coordinates (latitude, longitude, altitude) for display on a map interface. This requires:

1. **Attitude estimation** -- determining the radar platform's orientation (pitch, roll, yaw) using IMU sensors
2. **Position determination** -- obtaining the platform's GPS coordinates (latitude, longitude) and barometric altitude
3. **Coordinate transformation** -- rotating radar-frame target vectors into the world frame and adding the platform's GPS position

The navigation sensor suite consists of:

| Sensor | IC | Interface | Function |
|--------|-----|-----------|----------|
| 3-axis accelerometer | ADXL345 | I2C (0x53) | Pitch and roll from gravity vector |
| 3-axis gyroscope | ITG3200 | I2C (0x68) | Angular rate for complementary filter |
| 3-axis magnetometer | HMC5883 | I2C (0x1E) | Yaw (heading) from magnetic field |
| Barometric pressure | BMP180 | I2C | Altitude from atmospheric pressure |
| GPS receiver | -- | UART5 (TinyGPS++) | Latitude, longitude, altitude |

All IMU sensors are integrated into the GY-85 9-DOF module. The firmware driver is implemented in `GY_85_HAL.h` / `GY_85_HAL.c`, and the sensor fusion is performed in `main.cpp:1279--1386`.

---

## 2. GY-85 IMU Sensors

The GY-85 is a 9-DOF (degrees of freedom) inertial measurement unit combining three sensor ICs on a single breakout board.

### 2.1 ADXL345 Accelerometer

| Parameter | Value | Source |
|-----------|-------|--------|
| I2C address | `0x53` | `GY_85_HAL.h:7` |
| Range | $\pm 2g$ | Firmware scaling factor |
| Resolution | 13-bit (full resolution mode) | ADXL345 datasheet |
| Output | 16-bit signed integer (raw) | `GY85_t.ax`, `GY85_t.ay`, `GY85_t.az` |
| Scaling | $6.10351 \times 10^{-5}~\text{g/LSB}$ ($= 2.0 / 32768$) | `main.cpp:1294` |

The raw accelerometer readings are converted to units of $g$ and bias-corrected:

$$
a_i = a_{i,\text{raw}} \times \frac{2.0}{32768} - a_{i,\text{bias}} \quad (i = x, y, z) \tag{HW-NAV-1}
$$

where $a_{i,\text{bias}}$ are the stored calibration biases (`abias[3] = {-0.108, -0.038, -0.006}` in `main.cpp:139`).

### 2.2 ITG3200 Gyroscope

| Parameter | Value | Source |
|-----------|-------|--------|
| I2C address | `0x68` | `GY_85_HAL.h:9` |
| Range | $\pm 500~\text{deg/s}$ | Firmware scaling factor |
| Output | 16-bit signed float (after HAL) | `GY85_t.gx`, `GY85_t.gy`, `GY85_t.gz` |
| Scaling | $0.0152588~\text{deg/s/LSB}$ ($= 500.0 / 32768$) | `main.cpp:1302` |

The raw gyroscope readings are converted to degrees per second and bias-corrected. Note that the firmware inverts the $x$ and $y$ axes (`gx = -imu.gx`, `gy = -imu.gy` in `main.cpp:1287--1288`) to align the gyroscope axes with the accelerometer frame:

$$
\omega_i = \omega_{i,\text{raw}} \times \frac{500.0}{32768} - \omega_{i,\text{bias}} \quad (i = x, y, z) \tag{HW-NAV-2}
$$

where $\omega_{i,\text{bias}}$ are the gyroscope biases (`gbias[3] = {-10, 6, -12}` in `main.cpp:139`). The gyroscope values are subsequently converted from degrees/s to radians/s by multiplying by $\pi/180 \approx 0.01745$ (`main.cpp:1338--1340`).

### 2.3 HMC5883 Magnetometer

| Parameter | Value | Source |
|-----------|-------|--------|
| I2C address | `0x1E` | `GY_85_HAL.h:8` |
| Range | $\pm 2~\text{Ga}$ (implied by scaling) | Firmware scaling factor |
| Output | 16-bit signed integer (raw) | `GY85_t.mx`, `GY85_t.my`, `GY85_t.mz` |
| Scaling | $6.10351 \times 10^{-5}~\text{Ga/LSB}$ ($= 2.0 / 32768$) | `main.cpp:1310` |

The magnetometer readings require both bias correction and rotation matrix calibration (see Section 4).

### 2.4 I2C Initialization

The `GY85_Init()` function (`GY_85_HAL.h:22`) initializes all three sensor ICs via the STM32 I2C3 peripheral (`hi2c3`). Sensor data is read by `GY85_Update()`, which populates the `GY85_t` struct with raw readings from all three sensors in a single call.

---

## 3. Attitude Estimation: Complementary Filter

The firmware implements a complementary filter (`main.cpp:1327--1383`) that fuses accelerometer and gyroscope data to estimate platform attitude (pitch, roll, yaw). The complementary filter combines:

- **Accelerometer:** Accurate over long time scales (measures gravity direction) but noisy at short time scales (vibration-sensitive)
- **Gyroscope:** Accurate over short time scales (measures angular rate) but drifts over long time scales (integration error)

### 3.1 Accelerometer-Based Angle Estimates

The accelerometer provides absolute angle estimates from the gravity vector. Using the sensor-frame acceleration components $(a_x, a_y, a_z)$ after bias correction:

$$
\theta_\text{pitch,acc} = \arctan\!\left(\frac{a_x}{\sqrt{a_y^2 + a_z^2}}\right) \tag{HW-NAV-3}
$$

$$
\theta_\text{roll,acc} = \arctan\!\left(\frac{a_y}{\sqrt{a_x^2 + a_z^2}}\right) \tag{HW-NAV-4}
$$

In the firmware, these are computed as `RxAcc = ax` and `RyAcc = ay`, with the final pitch and roll extracted from the fused estimates (see Section 3.3).

### 3.2 Gyroscope Integration

The gyroscope provides angular rates that are integrated over the sampling interval $\Delta t$ to estimate angle changes. The firmware (`main.cpp:1343--1353`) computes the angle from the previous estimate plus the integrated rate:

$$
\theta_{\text{gyro},k} = \theta_{k-1} + \omega \cdot \Delta t \tag{HW-NAV-5}
$$

where $\omega$ is the angular rate in radians/s (after the deg/s to rad/s conversion) and $\Delta t$ is the time since the last update, computed from the hardware timer: `Time_Period = now_timeperiod - lasttime_timeperiod` in microseconds, converted to seconds by multiplying by $10^{-6}$ (`main.cpp:1351`).

The firmware uses a direction-cosine approach to convert from Euler angle rates to estimated gravity vector components:

$$
\begin{aligned}
R_{x,\text{gyro}} &= \frac{\sin(\theta_{xz,1})}{\sqrt{1 + \cos^2(\theta_{xz,1}) \cdot \tan^2(\theta_{yz,1})}} \\
R_{y,\text{gyro}} &= \frac{\sin(\theta_{yz,1})}{\sqrt{1 + \cos^2(\theta_{yz,1}) \cdot \tan^2(\theta_{xz,1})}}
\end{aligned}
\tag{HW-NAV-6}
$$

$$
R_{z,\text{gyro}} = \pm\sqrt{1 - R_{x,\text{gyro}}^2 - R_{y,\text{gyro}}^2} \tag{HW-NAV-7}
$$

The sign of $R_{z,\text{gyro}}$ is determined by the sign of the previous estimate $R_{z,\text{est},0}$ (`main.cpp:1359--1364`), ensuring continuity when the platform is inverted.

### 3.3 Complementary Filter Fusion

The complementary filter combines the accelerometer and gyroscope estimates with equal weighting $\alpha = 0.5$ (`main.cpp:1366--1368`):

$$
R_{i,\text{est}} = \alpha \cdot R_{i,\text{acc}} + (1 - \alpha) \cdot R_{i,\text{gyro}} \quad (i = x, y, z) \tag{HW-NAV-8}
$$

with $\alpha = 0.5$. This 50/50 weighting gives equal trust to the accelerometer and gyroscope, which is appropriate for moderate dynamics. The fused estimate is then normalized:

$$
R_\text{est} = \sqrt{R_{x,\text{est}}^2 + R_{y,\text{est}}^2 + R_{z,\text{est}}^2} \tag{HW-NAV-9}
$$

### 3.4 Pitch and Roll Extraction

The pitch and roll angles are extracted from the fused gravity vector estimate:

$$
\theta_\text{pitch} = \arctan\!\left(\frac{R_{x,\text{est}}}{\sqrt{R_{y,\text{est}}^2 + R_{z,\text{est}}^2}}\right) \tag{HW-NAV-10}
$$

$$
\theta_\text{roll} = \arctan\!\left(\frac{R_{y,\text{est}}}{\sqrt{R_{x,\text{est}}^2 + R_{z,\text{est}}^2}}\right) \tag{HW-NAV-11}
$$

These are computed in `main.cpp:1372--1373` with output in degrees (multiplied by $180/\pi$) and stored in `Pitch_Sensor` and `Roll_Sensor`.

### 3.5 Firmware Variable Mapping

| Standard Symbol | Firmware Variable | Description |
|----------------|-------------------|-------------|
| $a_x, a_y, a_z$ | `ax`, `ay`, `az` | Bias-corrected accelerometer ($g$) |
| $\omega_x, \omega_y, \omega_z$ | `gx`, `gy`, `gz` | Bias-corrected gyroscope (deg/s) |
| $R_{x,\text{acc}}$ | `RxAcc` | Accelerometer gravity estimate |
| $R_{x,\text{gyro}}$ | `RxGyro` | Gyroscope gravity estimate |
| $R_{x,\text{est}}$ | `RxEst_1` | Fused gravity estimate (current) |
| $R_{x,\text{est},0}$ | `RxEst_0` | Fused gravity estimate (previous) |
| $\theta_\text{pitch}$ | `Pitch_Sensor` | Output pitch (degrees) |
| $\theta_\text{roll}$ | `Roll_Sensor` | Output roll (degrees) |
| $\alpha$ | 0.5 (literal) | Complementary filter weight |
| $\Delta t$ | `Time_Period * 1e-6` | Sampling interval (seconds) |

---

## 4. Magnetometer Calibration and Yaw

The magnetometer provides heading (yaw) information by measuring the Earth's magnetic field. Raw magnetometer data requires calibration to remove hard-iron and soft-iron distortions, followed by tilt compensation using the pitch and roll from the complementary filter.

### 4.1 Magnetometer Calibration Transform

The firmware applies a 3x3 rotation/scaling matrix and bias correction to the raw magnetometer readings (`main.cpp:1314--1316`):

$$
\begin{bmatrix} m_{x,c} \\ m_{y,c} \\ m_{z,c} \end{bmatrix} = \begin{bmatrix} M_{11} & M_{12} & M_{13} \\ M_{21} & M_{22} & M_{23} \\ M_{31} & M_{32} & M_{33} \end{bmatrix} \begin{bmatrix} m_x - m_{x,\text{bias}} \\ m_y - m_{y,\text{bias}} \\ m_z - m_{z,\text{bias}} \end{bmatrix} \tag{HW-NAV-12}
$$

The calibration matrix corrects for:
- **Hard-iron distortion** (bias vector $\mathbf{m}_\text{bias}$): constant magnetic field offsets from nearby ferromagnetic materials
- **Soft-iron distortion** (matrix $\mathbf{M}$): scaling and cross-axis coupling from nearby magnetically permeable materials

The default calibration values from `main.cpp:139--142`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `mbias[3]` | $\{0.0, 0.0, 0.0\}$ | Hard-iron bias (uncalibrated default) |
| $\mathbf{M}$ | $\mathbf{I}_{3\times3}$ (identity) | Soft-iron matrix (uncalibrated default) |

> **Note:** The default calibration values are identity/zero, indicating that magnetometer calibration has not been performed for the current installation. Proper calibration requires collecting magnetometer data while rotating the sensor through all orientations and fitting an ellipsoid model to extract the bias vector and correction matrix.

After calibration, the corrected values are normalized to unit magnitude (`main.cpp:1322--1325`):

$$
\hat{m}_i = \frac{m_{i,c}}{\|\mathbf{m}_c\|} \quad \text{where} \quad \|\mathbf{m}_c\| = \sqrt{m_{x,c}^2 + m_{y,c}^2 + m_{z,c}^2} \tag{HW-NAV-13}
$$

### 4.2 Tilt-Compensated Heading

The raw magnetometer heading is only accurate when the sensor is level. For a tilted platform, the magnetic field components must be projected onto the horizontal plane using the pitch and roll angles from the complementary filter.

The firmware computes tilt-compensated magnetic field components (`main.cpp:1375--1376`):

$$
m_{x,\text{horiz}} = \hat{m}_x \cos\theta_\text{pitch} - \hat{m}_z \sin\theta_\text{pitch} \tag{HW-NAV-14}
$$

$$
m_{y,\text{horiz}} = \hat{m}_x \sin\theta_\text{roll} \sin\theta_\text{pitch} + \hat{m}_y \cos\theta_\text{roll} - \hat{m}_z \sin\theta_\text{roll} \cos\theta_\text{pitch} \tag{HW-NAV-15}
$$

### 4.3 Yaw Computation

The yaw (heading) angle is computed from the tilt-compensated horizontal magnetic field components, corrected for magnetic declination (`main.cpp:1377`):

$$
\psi_\text{yaw} = \arctan2(m_{y,\text{horiz}},\; m_{x,\text{horiz}}) - \delta_\text{mag} \tag{HW-NAV-16}
$$

where $\delta_\text{mag}$ is the local magnetic declination (`Mag_Declination = -0.61` degrees in `main.cpp:146`, see [Parameter Table](../00_notation/parameter_table.md#system-level-derivedtbd)).

The result is normalized to $[0^\circ, 360^\circ)$ by adding $360^\circ$ if negative (`main.cpp:1379`).

| Firmware Variable | Symbol | Description |
|-------------------|--------|-------------|
| `magRawX` | $m_{x,\text{horiz}}$ | Tilt-compensated magnetic X |
| `magRawY` | $m_{y,\text{horiz}}$ | Tilt-compensated magnetic Y |
| `Yaw_Sensor` | $\psi_\text{yaw}$ | Output yaw (degrees, 0--360) |
| `Mag_Declination` | $\delta_\text{mag}$ | Magnetic declination ($-0.61^\circ$) |

---

## 5. Barometric Altitude

The BMP180 barometric pressure sensor provides altitude estimation independent of GPS.

### 5.1 BMP180 Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Resolution mode | `BMP180_ULTRAHIGHRES` | `main.cpp:166` |
| Oversampling | 8x | BMP180 datasheet |
| Power consumption | $12~\mu\text{A}$ | BMP180 datasheet |

### 5.2 Hypsometric Formula

The firmware computes altitude from pressure using a simplified hypsometric formula (`main.cpp:1393`):

$$
h = 44330 \left(1 - \left(\frac{P}{P_0}\right)^{1/5.255}\right) \tag{HW-NAV-17}
$$

where $P$ is the measured pressure (Pa) from the BMP180 and $P_0 = 101325~\text{Pa}$ is the standard sea-level pressure. The exponent $1/5.255 \approx 0.1903$ is derived from the international barometric formula:

$$
h = \frac{T_0}{L} \left[\left(\frac{P_0}{P}\right)^{R_\text{air} L / (g \, M_\text{air})} - 1\right] \tag{HW-NAV-18}
$$

where $T_0 = 288.15~\text{K}$ (standard temperature), $L = 0.0065~\text{K/m}$ (temperature lapse rate), $R_\text{air} = 8.31447~\text{J/(mol\cdot K)}$ (universal gas constant), $g = 9.80665~\text{m/s}^2$ (standard gravity), and $M_\text{air} = 0.0289644~\text{kg/mol}$ (molar mass of dry air). Substituting the standard atmosphere constants yields the coefficient 44330 and exponent 1/5.255 used in the firmware.

The firmware averages 5 consecutive readings with 100 ms intervals for noise reduction (`main.cpp:1391--1395`). The altitude is stored in `RADAR_Altitude`.

---

## 6. Radar-to-World Coordinate Transform

The complete coordinate transform converts a target detection in the radar's local frame to a world-frame position relative to the radar's GPS coordinates.

### 6.1 Radar Frame

In the radar's local spherical coordinate frame, a target is described by:
- **Range** $R$ -- distance from the radar (from beat frequency, see Eq. (FMCW-1) in [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md))
- **Azimuth angle** $\phi_\text{az}$ -- determined by the stepper motor position (mechanical rotation, $N_\text{az} = 50$ positions per revolution)
- **Elevation angle** $\theta_\text{el}$ -- determined by the electronic beam steering position (ADAR1000 phase shifts, $N_\text{el} = 31$ positions, see [`04_antenna_beamforming.md`](04_antenna_beamforming.md))

The target position in radar-frame Cartesian coordinates is:

$$
\mathbf{p}_\text{radar} = \begin{bmatrix} R \cos\theta_\text{el} \cos\phi_\text{az} \\ R \cos\theta_\text{el} \sin\phi_\text{az} \\ R \sin\theta_\text{el} \end{bmatrix} \tag{HW-NAV-19}
$$

### 6.2 Rotation Matrices

To transform from the radar body frame to the world (North-East-Down or East-North-Up) frame, three successive rotations are applied for roll ($\theta_\text{roll}$), pitch ($\theta_\text{pitch}$), and yaw ($\psi_\text{yaw}$):

**Roll rotation** (about the $x$-axis):

$$
\mathbf{R}_\text{roll} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta_\text{roll} & -\sin\theta_\text{roll} \\ 0 & \sin\theta_\text{roll} & \cos\theta_\text{roll} \end{bmatrix} \tag{HW-NAV-20}
$$

**Pitch rotation** (about the $y$-axis):

$$
\mathbf{R}_\text{pitch} = \begin{bmatrix} \cos\theta_\text{pitch} & 0 & \sin\theta_\text{pitch} \\ 0 & 1 & 0 \\ -\sin\theta_\text{pitch} & 0 & \cos\theta_\text{pitch} \end{bmatrix} \tag{HW-NAV-21}
$$

**Yaw rotation** (about the $z$-axis):

$$
\mathbf{R}_\text{yaw} = \begin{bmatrix} \cos\psi_\text{yaw} & -\sin\psi_\text{yaw} & 0 \\ \sin\psi_\text{yaw} & \cos\psi_\text{yaw} & 0 \\ 0 & 0 & 1 \end{bmatrix} \tag{HW-NAV-22}
$$

### 6.3 Complete Body-to-World Transform

The world-frame target position is obtained by applying the rotation sequence yaw, then pitch, then roll (Tait-Bryan ZYX convention):

$$
\mathbf{p}_\text{world} = \mathbf{R}_\text{yaw} \, \mathbf{R}_\text{pitch} \, \mathbf{R}_\text{roll} \, \mathbf{p}_\text{radar} \tag{HW-NAV-23}
$$

The combined rotation matrix $\mathbf{R} = \mathbf{R}_\text{yaw} \, \mathbf{R}_\text{pitch} \, \mathbf{R}_\text{roll}$ expands to:

$$
\mathbf{R} = \begin{bmatrix}
c_\psi c_\theta & c_\psi s_\theta s_\phi - s_\psi c_\phi & c_\psi s_\theta c_\phi + s_\psi s_\phi \\
s_\psi c_\theta & s_\psi s_\theta s_\phi + c_\psi c_\phi & s_\psi s_\theta c_\phi - c_\psi s_\phi \\
-s_\theta & c_\theta s_\phi & c_\theta c_\phi
\end{bmatrix} \tag{HW-NAV-24}
$$

where $c_\psi = \cos\psi_\text{yaw}$, $s_\psi = \sin\psi_\text{yaw}$, $c_\theta = \cos\theta_\text{pitch}$, $s_\theta = \sin\theta_\text{pitch}$, $c_\phi = \cos\theta_\text{roll}$, $s_\phi = \sin\theta_\text{roll}$.

### 6.4 Quaternion Representation

The firmware initializes a quaternion array `q[4] = {1.0, 0.0, 0.0, 0.0}` (`main.cpp:144`), representing the identity rotation in quaternion form $q = (w, x, y, z)$. However, the actual attitude estimation uses the **Euler-angle complementary filter** (Section 3), not a quaternion-based filter.

For reference, the conversion from Euler angles to quaternion is:

$$
\begin{aligned}
q_w &= \cos(\psi/2)\cos(\theta/2)\cos(\phi/2) + \sin(\psi/2)\sin(\theta/2)\sin(\phi/2) \\
q_x &= \cos(\psi/2)\cos(\theta/2)\sin(\phi/2) - \sin(\psi/2)\sin(\theta/2)\cos(\phi/2) \\
q_y &= \cos(\psi/2)\sin(\theta/2)\cos(\phi/2) + \sin(\psi/2)\cos(\theta/2)\sin(\phi/2) \\
q_z &= \sin(\psi/2)\cos(\theta/2)\cos(\phi/2) - \cos(\psi/2)\sin(\theta/2)\sin(\phi/2)
\end{aligned}
\tag{HW-NAV-25}
$$

> **Implementation Note:** The `q[4]` array is initialized but **not updated** in the current firmware. The complementary filter outputs Euler angles directly (`Pitch_Sensor`, `Roll_Sensor`, `Yaw_Sensor`). A future firmware revision could implement a quaternion-based Madgwick or Mahony filter to avoid gimbal lock near $\pm 90^\circ$ pitch, but the current Euler-angle approach is adequate for the AERIS-10's expected operating tilt range.

---

## 7. GPS Integration

### 7.1 GPS Receiver

The AERIS-10 uses a GPS receiver connected via UART5 on the STM32F746 microcontroller. GPS data is parsed using the TinyGPS++ library (`TinyGPSPlus.h`, `main.cpp:122`).

UART5 is initialized in `MX_UART5_Init()` (`main.cpp:2143--2169`). Incoming bytes are passed to `gps.encode(ch)` (`main.cpp:909`) for NMEA sentence parsing.

### 7.2 GPS Data Structure

The firmware defines a `GPS_Data_t` structure for packaging navigation data (`main.cpp:125,1530`):

| Field | Type | Description |
|-------|------|-------------|
| Latitude | `double` | Radar position latitude (degrees) |
| Longitude | `double` | Radar position longitude (degrees) |
| Altitude | `float` | Radar altitude from BMP180 (meters) |
| Pitch | `float` | Platform pitch from IMU (degrees) |
| Timestamp | `uint32_t` | System tick count (`HAL_GetTick()`) |

This data is transmitted to the GUI via USB using `GPS_SendBinaryToGUI()` (`main.cpp:1531`) as a binary packet: `[Header 4B][Latitude 8B][Longitude 8B][Altitude 4B][CRC 2B]`.

### 7.3 Radar-to-Absolute Position

Given the radar's GPS position $(\lambda_\text{radar}, \varphi_\text{radar}, h_\text{radar})$ (latitude, longitude, altitude) and a target at world-frame offset $\mathbf{p}_\text{world} = (p_E, p_N, p_U)$ (East, North, Up components from Eq. (HW-NAV-23)), the target's absolute GPS position is approximated by:

$$
\begin{aligned}
\lambda_\text{target} &= \lambda_\text{radar} + \frac{p_N}{R_\oplus} \cdot \frac{180}{\pi} \\
\varphi_\text{target} &= \varphi_\text{radar} + \frac{p_E}{R_\oplus \cos(\lambda_\text{radar} \cdot \pi / 180)} \cdot \frac{180}{\pi} \\
h_\text{target} &= h_\text{radar} + p_U
\end{aligned}
\tag{HW-NAV-26}
$$

where $R_\oplus \approx 6{,}371{,}000~\text{m}$ is the mean Earth radius. This flat-Earth approximation is valid for the AERIS-10's detection ranges ($R_\text{max} \leq 20~\text{km}$, see [Parameter Table](../00_notation/parameter_table.md#system-level-derivedtbd)), where the curvature error is negligible ($< 0.003\%$ at 20 km).

---

## 8. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbols for $N_\text{el}$, $N_\text{az}$, $\theta$, $R$
- [Parameter Table](../00_notation/parameter_table.md) -- magnetic declination, beam position count, detection range
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Hardware Cross-References
- [`04_antenna_beamforming.md`](04_antenna_beamforming.md) -- beam position to steering angle mapping ($N_\text{el} = 31$ positions, phase shift array `phase_differences[31]`)
- [`01_system_overview.md`](01_system_overview.md) -- STM32 I2C bus to IMU sensors, UART to GPS

### Firmware Sources
- `GY_85_HAL.h` -- GY-85 IMU driver: I2C addresses (ADXL345: 0x53, ITG3200: 0x68, HMC5883: 0x1E), sensor struct, init/update API
- `main.cpp:139--156` -- IMU calibration constants (accelerometer, gyroscope, magnetometer biases; calibration matrix M; quaternion array; magnetic declination)
- `main.cpp:1279--1386` -- Complementary filter implementation: sensor reading, bias correction, scaling, gravity vector estimation, pitch/roll/yaw computation
- `main.cpp:1388--1395` -- BMP180 barometric altitude computation
- `main.cpp:1527--1531` -- GPS data packaging and transmission to GUI
- `BMP180.h` -- BMP180 barometric pressure sensor driver

### Component Datasheets
- ADXL345 -- 3-axis digital accelerometer (Analog Devices)
- ITG3200 -- 3-axis digital gyroscope (InvenSense)
- HMC5883L -- 3-axis digital magnetometer (Honeywell)
- BMP180 -- Digital pressure sensor (Bosch Sensortec)
- TinyGPS++ -- Arduino/STM32 GPS parsing library
