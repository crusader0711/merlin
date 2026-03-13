# AERIS-10 Project-Wide Symbol Table

**Purpose:** This is the **single authoritative source** for all mathematical symbols used across the AERIS-10 documentation set. Every symbol appearing in any project document must be defined here. No ad-hoc symbol definitions are permitted.

**Notation authority:** IEEE 686-2024 (IEEE Standard Radar Definitions) is the primary reference for terminology. Where IEEE 686 does not specify a symbol, standard radar textbook conventions (Skolnik, Richards) are used.

**Formatting rules:** See [`conventions.md`](conventions.md) for equation numbering, cross-reference format, and MathJax usage guidelines.

**Numerical values:** This table defines symbols and their meanings only. For actual parameter values (both AERIS-10 Nexus and Extended variants), see [`parameter_table.md`](parameter_table.md).

---

## 1. Waveform and Timing Parameters

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $f_c$ | Center (carrier) frequency | Hz | carrier frequency |
| $B$ | Chirp bandwidth (sweep range) | Hz | bandwidth |
| $T_c$ | Chirp duration (pulse width) | s | pulse duration |
| $T_{c,1}$ | Long chirp duration | s | -- |
| $T_{c,2}$ | Short chirp duration | s | -- |
| $\mu$ | Chirp rate (sweep slope), $\mu = B / T_c$ | Hz/s | chirp rate |
| $f_b$ | Beat frequency (IF after dechirp) | Hz | beat frequency |
| $f_r$ | Pulse repetition frequency (PRF) | Hz | pulse repetition frequency |
| $f_{r,1}$ | PRF for long chirp mode | Hz | -- |
| $f_{r,2}$ | PRF for short chirp mode | Hz | -- |
| $T_r$ | Pulse repetition interval (PRI), $T_r = 1/f_r$ | s | pulse repetition interval |
| $T_{r,1}$ | PRI for long chirp mode | s | -- |
| $T_{r,2}$ | PRI for short chirp mode | s | -- |
| $\tau$ | Round-trip delay, $\tau = 2R/c$ | s | -- |
| $T_\text{guard}$ | Guard time between chirp sequences | s | -- |
| $M$ | Number of chirps per CPI (per beam position) | -- | -- |

## 2. Range and Velocity

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $R$ | Range to target | m | range |
| $R_\text{max}$ | Maximum unambiguous range | m | -- |
| $\Delta R$ | Range resolution | m | range resolution |
| $v$ | Target radial velocity | m/s | radial velocity |
| $f_d$ | Doppler frequency shift | Hz | Doppler frequency |
| $\Delta v$ | Velocity resolution | m/s | -- |
| $c$ | Speed of light, $c \approx 2.998 \times 10^8~\text{m/s}$ | m/s | -- |
| $\lambda$ | Wavelength, $\lambda = c / f_c$ | m | wavelength |

## 3. Antenna and Beamforming

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $N$ | Number of array elements | -- | -- |
| $N_\text{el}$ | Number of beam elevation positions | -- | -- |
| $N_\text{az}$ | Number of azimuth positions per revolution | -- | -- |
| $d$ | Inter-element spacing | m | element spacing |
| $\theta$ | Beam steering angle from broadside | rad or deg | scan angle |
| $\Delta\phi$ | Phase shift per element | rad or deg | -- |
| $\Delta\phi_n$ | Phase difference for elevation position $n$ | rad or deg | -- |
| $G$ | Antenna gain (combined Tx/Rx unless subscripted) | dBi | antenna gain |
| $G_t$ | Transmit antenna gain | dBi | -- |
| $G_r$ | Receive antenna gain | dBi | -- |
| $k$ | Wavenumber, $k = 2\pi/\lambda$ | rad/m | wavenumber |
| $\psi$ | Electrical angle, $\psi = kd\sin\theta + \Delta\phi$ | rad | -- |
| $\theta_0$ | Beam steering angle (desired) | rad or deg | scan angle |
| $\theta_{3\text{dB}}$ | Half-power beamwidth | rad or deg | beamwidth |
| $w_n$ | Amplitude weight for array element $n$ (dimensionless). Applying a window function $w[n]$ to the array is equivalent to amplitude tapering with weights $w_n = w[n]$. | -- | -- |
| $a_n$ | Nominal amplitude weight for element $n$ | -- | -- |
| $\delta\phi_n$ | Phase error for element $n$ | rad | -- |
| $\delta a_n$ | Amplitude error for element $n$ | -- | -- |
| $AF(\theta)$ | Array factor as function of angle | -- | array factor |

## 4. Detection and Signal

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $P_t$ | Transmit power (per element) | W | transmitted power |
| $P_r$ | Received power | W | received power |
| $\sigma$ | Radar cross section (RCS) | m$^2$ | radar cross section |
| $L$ | Total system losses (linear ratio) | -- | system loss |
| $F$ | Noise figure (linear ratio) | -- | noise figure |
| $\text{NF}$ | Noise figure (dB scale) | dB | -- |
| $T_0$ | Reference noise temperature, $T_0 = 290~\text{K}$ | K | -- |
| $k_B$ | Boltzmann constant, $k_B = 1.381 \times 10^{-23}~\text{J/K}$ | J/K | -- |
| $P_{fa}$ | Probability of false alarm | -- | false alarm probability |
| $P_d$ | Probability of detection | -- | detection probability |
| $\text{SNR}$ | Signal-to-noise ratio | dB | signal-to-noise ratio |
| $\alpha$ | CFAR threshold multiplier | -- | -- |
| $N_\text{ref}$ | Number of CFAR reference cells, total | -- | -- |
| $N_\text{guard}$ | Number of CFAR guard cells, total | -- | -- |
| $T_e$ | Equivalent noise temperature | K | noise temperature |
| $B_n$ | Noise bandwidth | Hz | noise bandwidth |
| $\text{SNR}_\text{min}$ | Minimum detectable SNR | dB | -- |

## 5. Signal Processing

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $f_s$ | ADC sampling frequency | Hz | sampling rate |
| $f_\text{IF}$ | Intermediate frequency | Hz | intermediate frequency |
| $N_\text{FFT}$ | FFT size (range dimension) | -- | -- |
| $N_\text{Doppler}$ | Doppler FFT size | -- | -- |
| $N_R$ | Number of range bins | -- | -- |
| $N_\text{CIC}$ | CIC filter stages | -- | -- |
| $D_\text{CIC}$ | CIC decimation factor | -- | -- |
| $w[n]$ | Window function (discrete) | -- | -- |
| $\chi(\tau, \nu)$ | Ambiguity function | -- | -- |

## 7. Hardware and Power

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $V_\text{rail}$ | Voltage rail value | V | -- |
| $I_\text{rail}$ | Current draw per rail | A | -- |
| $P_\text{diss}$ | Power dissipation | W | -- |
| $T_\text{junction}$ | Junction temperature | C or K | -- |
| $\theta_{JA}$ | Thermal resistance, junction-to-ambient | C/W or K/W | -- |
| $t_\text{lock}$ | PLL lock time | s | lock time |
| $\mathcal{L}(f_m)$ | Phase noise at offset $f_m$ from carrier | dBc/Hz | phase noise |
| $t_\text{pipeline}$ | End-to-end pipeline latency | s | -- |
| $N_\text{LUT}$ | FPGA look-up table count | -- | -- |
| $N_\text{FF}$ | FPGA flip-flop count | -- | -- |
| $N_\text{BRAM}$ | FPGA Block RAM count | -- | -- |
| $N_\text{DSP}$ | FPGA DSP48E1 slice count | -- | -- |

## 8. Physical Constants

| Symbol | Definition | Value | Units |
|--------|-----------|-------|-------|
| $c$ | Speed of light in vacuum | $2.998 \times 10^8$ | m/s |
| $k_B$ | Boltzmann constant | $1.381 \times 10^{-23}$ | J/K |
| $T_0$ | Standard reference noise temperature | $290$ | K |

---

**Symbols not listed here MUST be added to this table before use in any project document. No ad-hoc symbol definitions are permitted.**

When adding a new symbol:
1. Check IEEE 686-2024 for the standard term and definition.
2. Verify no existing symbol in this table already covers the same concept.
3. Add the symbol to the appropriate domain section above.
4. Update any documents that previously used a non-standard symbol.
