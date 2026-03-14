# Target Tracking Improvements

**Purpose:** Survey advanced Kalman filtering approaches for maneuvering target tracking in the AERIS-10 radar system, with feasibility assessment and ranked recommendations for the Python-based host processing pipeline.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Python GUI V6](../03_software/03_python_gui.md) -- current Kalman filter baseline and RadarTarget dataclass
- [Detection Theory](../01_physics/04_detection_theory.md) -- CFAR detection producing inputs to tracking

---

## 1. Current State

The AERIS-10 radar target tracking is implemented in the Python GUI application (`GUI_V6.py`) running on the host PC. All tracking computation executes in Python -- **no FPGA resource constraint applies** to any tracking algorithm. The FPGA pipeline produces detections that are transferred to the host via FT601 USB 3.0; tracking is a post-detection, host-side operation.

### 1.1 Current Kalman Filter

The GUI imports `filterpy.kalman.KalmanFilter` for target tracking across consecutive scans (see Section 7.2 of [`03_software/03_python_gui.md`](../03_software/03_python_gui.md#72-kalman-filter-tracking)). The intended state model uses a **fixed-parameter constant-velocity Kalman filter**:

$$
\mathbf{x}_k = \begin{bmatrix} x \\ y \\ v_x \\ v_y \end{bmatrix}, \quad
\mathbf{z}_k = \begin{bmatrix} x_\text{meas} \\ y_\text{meas} \end{bmatrix} \tag{SW-3}
$$

as documented in Eq. (SW-3) of the GUI documentation. The state vector tracks 2D position and velocity in Cartesian coordinates. The measurement vector contains the measured position from DBSCAN cluster centroids.

The constant-velocity state transition model is:

$$
\mathbf{F} = \begin{bmatrix} 1 & 0 & \Delta t & 0 \\ 0 & 1 & 0 & \Delta t \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}
$$

where $\Delta t$ is the scan-to-scan time interval.

**Key limitations of the current approach:**
- **Fixed process noise** $\mathbf{Q}$: Cannot adapt to changing target dynamics
- **Single motion model**: Assumes constant velocity -- no acceleration or turn modeling
- **No model switching**: Cannot detect transitions between cruise and maneuver
- **Fixed measurement noise** $\mathbf{R}$: Does not adapt to varying SNR conditions

> **Note:** The `RadarProcessor` class is currently a stub (`pass` body). The Kalman filter and DBSCAN clustering described here represent the **designed intent** from the import list, not a working implementation. See Section 2 of [`03_software/03_python_gui.md`](../03_software/03_python_gui.md#2-implementation-status) for the implementation status table.

### 1.2 DBSCAN Clustering Baseline

The GUI imports `sklearn.cluster.DBSCAN` for spatial clustering of radar detections before tracking (see Section 7.1 of [`03_software/03_python_gui.md`](../03_software/03_python_gui.md#71-dbscan-clustering)):

$$
\text{cluster} = \text{DBSCAN}(\varepsilon, m_\text{min}, d(\mathbf{x}_i, \mathbf{x}_j)) \tag{SW-2}
$$

DBSCAN groups adjacent range-Doppler cell detections into unified target reports before Kalman filter association. The clustering quality directly affects tracking performance -- poorly separated clusters produce noisy measurements that degrade filter convergence.

### 1.3 RadarTarget Dataclass

Each detected target is represented by the `RadarTarget` dataclass (Section 3 of [`03_software/03_python_gui.md`](../03_software/03_python_gui.md#3-radartarget-dataclass)), which includes a `track_id` field (default $-1$ for untracked). The Kalman tracker assigns persistent `track_id` values to enable track continuity across scans.

### 1.4 Measurement Geometry

The radar provides measurements in polar coordinates $(R, \theta, \text{elevation})$ where $R$ is slant range and $\theta$ is azimuth beam steering angle. Converting these to Cartesian coordinates for the Kalman state vector introduces a **nonlinear measurement model**:

$$
\begin{aligned}
x &= R \cos\theta \cos\phi_\text{el} \\
y &= R \sin\theta \cos\phi_\text{el}
\end{aligned}
$$

The current design converts to Cartesian before filtering, applying a linear measurement model $\mathbf{H} = [I_{2 \times 2} \mid 0_{2 \times 2}]$. This is an approximation that discards the nonlinear error structure of the polar-to-Cartesian conversion.

---

## 2. Literature Survey

### 2.1 IMM-Kalman (Interacting Multiple Model)

The IMM estimator runs $r$ Kalman filters in parallel, each with a different motion model, and combines their estimates using model probabilities that are updated at each time step.

**Architecture:** For radar target tracking, a typical IMM uses $r = 2$ or $r = 3$ models:

| Model | State Transition | Use Case |
|-------|-----------------|----------|
| Constant velocity (CV) | $\mathbf{F}_\text{CV}$: linear motion, $\mathbf{Q}$ tuned for low process noise | Cruising targets, straight-line flight |
| Constant acceleration (CA) | $\mathbf{F}_\text{CA}$: includes acceleration states $[a_x, a_y]^T$ | Accelerating/decelerating targets |
| Coordinated turn (CT) | $\mathbf{F}_\text{CT}$: includes turn rate $\omega$ with nonlinear state propagation | Turning targets, orbital flight |

The IMM algorithm proceeds in four steps at each time step $k$:

1. **Mixing:** Combine previous model-conditioned state estimates using mixing probabilities derived from the model transition probability matrix $\pi_{ij} = P(M_j^k \mid M_i^{k-1})$
2. **Filtering:** Run each Kalman filter independently with its mixed initial condition
3. **Model probability update:** Compute likelihood of the current measurement under each model, update model probabilities $\mu_j^k$ using Bayes' rule
4. **Combination:** Form the overall state estimate as the probability-weighted average of model-conditioned estimates:

$$
\hat{\mathbf{x}}_k = \sum_{j=1}^{r} \mu_j^k \, \hat{\mathbf{x}}_k^j
$$

**Model transition probability matrix:** The Markov transition matrix $\boldsymbol{\Pi}$ governs how likely each model is to transition to another. A typical initialization for 3-model IMM:

$$
\boldsymbol{\Pi} = \begin{bmatrix}
0.95 & 0.025 & 0.025 \\
0.025 & 0.95 & 0.025 \\
0.025 & 0.025 & 0.95
\end{bmatrix}
$$

The diagonal elements (0.95) reflect the assumption that targets usually maintain their current behavior. Off-diagonal elements control mode transition sensitivity -- higher values enable faster mode switching but increase false transitions. Tuning $\boldsymbol{\Pi}$ requires balancing maneuver detection latency against steady-state noise.

**Computational overhead:** Running $r$ Kalman filters requires $r$ matrix multiplications and inversions per update. For $r = 3$ with a 4-state model, this is approximately 3x the computation of a single Kalman filter. In Python with NumPy, this amounts to microseconds per update -- negligible compared to the radar scan rate.

**Performance advantage over fixed-model Kalman:** The IMM automatically increases the weight of the acceleration or turn model when the measurement innovations from the CV model grow large. This allows rapid adaptation to maneuvers without the lag inherent in a single filter with high process noise (which would degrade steady-state tracking accuracy).

**References:**
- Blom, H.A.P. and Bar-Shalom, Y., "The interacting multiple model algorithm for systems with Markovian switching coefficients," *IEEE Trans. Automatic Control*, vol. 33, no. 8, pp. 780-783, 1988
- Bar-Shalom, Y., Li, X.R., and Kirubarajan, T., *Estimation with Applications to Tracking and Navigation*, Wiley, 2001

### 2.2 Variational Bayesian IMM

Recent work extends the IMM framework using variational Bayesian (VB) inference to improve maneuver detection responsiveness. The 2025 MDPI Electronics paper proposes a model-adaptive Kalman filter that uses variational inference to adapt change-point statistics in real time.

**Key innovation:** Rather than relying solely on the fixed Markov transition matrix $\boldsymbol{\Pi}$ for mode switching, the VB-IMM method treats the model transition probabilities as random variables and estimates them jointly with the target state. This provides:

- **Faster maneuver detection:** The transition probabilities adapt based on measurement evidence, allowing the filter to switch models more aggressively when strong innovation sequences indicate a mode change
- **RMSE improvement:** Published results show 10-25% RMSE reduction compared to standard IMM for maneuvering targets, with the improvement concentrated during transition periods
- **Automatic tuning:** Reduces sensitivity to the initial choice of $\boldsymbol{\Pi}$, a key practical advantage since transition matrix tuning is often the most difficult aspect of IMM deployment

**Computational requirements:** The variational inference adds an iterative optimization step (typically 3-5 iterations per time step) to the standard IMM update. Total overhead is approximately 5-8x a single Kalman filter -- still trivial in Python on a modern host PC.

**Limitations:**
- Newer algorithm with fewer field-validated deployments than standard IMM
- Convergence of the variational iterations is not always guaranteed for poorly conditioned problems
- More complex to implement and debug than standard IMM

**Reference:**
- "Model Adaptive Kalman Filter for Maneuvering Target Tracking," *MDPI Electronics*, vol. 14, no. 10, 2025 (Article 1908)

### 2.3 Adaptive Kalman (Process Noise Estimation)

Adaptive Kalman filtering adjusts the process noise covariance $\mathbf{Q}$ online, without switching between discrete models. This is a simpler alternative to IMM that can improve tracking of maneuvering targets without the complexity of multiple parallel filters.

**Innovation-Based Adaptive Estimation (IAE):**

The innovation sequence $\boldsymbol{\nu}_k = \mathbf{z}_k - \mathbf{H}\hat{\mathbf{x}}_{k|k-1}$ provides a real-time measure of filter consistency. The expected innovation covariance is:

$$
\mathbf{S}_k = \mathbf{H}\mathbf{P}_{k|k-1}\mathbf{H}^T + \mathbf{R}
$$

When the actual innovations consistently exceed $\mathbf{S}_k$ (indicating the filter is not tracking well), the process noise $\mathbf{Q}$ is increased. A common IAE estimator uses a sliding window of $W$ innovations:

$$
\hat{\mathbf{Q}}_k = \frac{1}{W}\sum_{i=k-W+1}^{k} \left(\boldsymbol{\nu}_i \boldsymbol{\nu}_i^T - \mathbf{H}\mathbf{P}_{i|i-1}\mathbf{H}^T - \mathbf{R}\right)
$$

**Maximum Likelihood Estimation (MLE):**

An alternative approach estimates $\mathbf{Q}$ by maximizing the likelihood of the observed measurement sequence. This provides statistically optimal estimates but requires more computation (typically iterative optimization).

**Advantages over IMM:**
- Simpler implementation -- single filter, no mixing step
- Continuous adaptation rather than discrete model switching
- Fewer tuning parameters (window size $W$ vs. full transition matrix)

**Disadvantages:**
- Cannot capture distinct motion modes (e.g., cruise vs. coordinated turn)
- Slower to respond to abrupt maneuvers than IMM (requires several innovations to build evidence)
- The IAE estimate of $\mathbf{Q}$ can become negative semi-definite, requiring projection to ensure validity

**References:**
- Mehra, R.K., "On the identification of variances and adaptive Kalman filtering," *IEEE Trans. Automatic Control*, vol. 15, no. 2, pp. 175-184, 1970
- Mohamed, A.H. and Schwarz, K.P., "Adaptive Kalman filtering for INS/GPS," *Journal of Geodesy*, vol. 73, pp. 193-203, 1999

### 2.4 Extended Kalman Filter (EKF) and Unscented Kalman Filter (UKF)

The current design converts radar measurements from polar $(R, \theta)$ to Cartesian $(x, y)$ before applying a linear Kalman filter. This introduces systematic errors from the nonlinear coordinate transformation. The EKF and UKF operate directly in the measurement space, avoiding this approximation.

**Extended Kalman Filter (EKF):**

The EKF linearizes the nonlinear measurement function $\mathbf{h}(\mathbf{x})$ around the current state estimate:

$$
\mathbf{H}_k = \frac{\partial \mathbf{h}}{\partial \mathbf{x}}\bigg|_{\mathbf{x}=\hat{\mathbf{x}}_{k|k-1}}
$$

For the radar measurement model $\mathbf{h}(\mathbf{x}) = [R, \theta]^T = [\sqrt{x^2 + y^2}, \arctan(y/x)]^T$, the Jacobian is:

$$
\mathbf{H}_k = \begin{bmatrix}
\frac{x}{\sqrt{x^2+y^2}} & \frac{y}{\sqrt{x^2+y^2}} & 0 & 0 \\[4pt]
\frac{-y}{x^2+y^2} & \frac{x}{x^2+y^2} & 0 & 0
\end{bmatrix}
$$

The EKF uses this linearized Jacobian in place of the constant $\mathbf{H}$ matrix, providing better handling of the nonlinear measurement geometry.

**Unscented Kalman Filter (UKF):**

The UKF uses deterministic sigma points to propagate the state distribution through the nonlinear functions, avoiding the Jacobian computation entirely. For a state dimension $n$, the UKF generates $2n + 1 = 9$ sigma points (for $n = 4$), propagates each through the measurement function, and reconstructs the predicted measurement statistics from the transformed points.

**Comparison for radar tracking:**

| Property | Linear KF (current) | EKF | UKF |
|----------|---------------------|-----|-----|
| Measurement model | Linear ($\mathbf{H}$ constant) | Linearized Jacobian | Sigma point propagation |
| Coordinate conversion | Pre-filter (introduces error) | In-filter (measurement space) | In-filter (measurement space) |
| Accuracy at close range | Good (small angular spread) | Better (captures nonlinearity) | Best (no linearization error) |
| Accuracy at long range | Good (narrow angular spread) | Good | Good |
| Computational cost | Lowest | Moderate (Jacobian computation) | Moderate (sigma point propagation) |
| Python library support | `filterpy.kalman.KalmanFilter` | `filterpy.kalman.ExtendedKalmanFilter` | `filterpy.kalman.UnscentedKalmanFilter` |

**When EKF/UKF matters:** The benefit is most significant at short ranges where the angular measurement uncertainty maps to a large Cartesian position uncertainty, and at extreme steering angles where the polar-to-Cartesian nonlinearity is strongest. For the AERIS-10 scan range of approximately $\pm 33°$ (from beam steering analysis in [`02_hardware/04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#32-steering-angle-derivation)), the nonlinearity is moderate.

**References:**
- Julier, S.J. and Uhlmann, J.K., "Unscented filtering and nonlinear estimation," *Proceedings of the IEEE*, vol. 92, no. 3, pp. 401-422, 2004
- Ristic, B., Arulampalam, S., and Gordon, N., *Beyond the Kalman Filter: Particle Filters for Tracking Applications*, Artech House, 2004

---

## 3. Gap Analysis

The current fixed-parameter constant-velocity Kalman filter has the following gaps relative to state-of-the-art radar target tracking:

| Gap | Impact | Severity |
|-----|--------|----------|
| **No model switching** | Cannot adapt to maneuvering targets; track diverges during acceleration or turns | HIGH |
| **Fixed process noise** $\mathbf{Q}$ | Noise tuned for steady state is too low for maneuvers; noise tuned for maneuvers degrades steady-state accuracy | HIGH |
| **Single motion model** (constant velocity) | No representation of acceleration or turn dynamics | HIGH |
| **Linear measurement model** | Polar-to-Cartesian conversion error not captured in filter covariance | MEDIUM |
| **Fixed measurement noise** $\mathbf{R}$ | Does not account for SNR-dependent measurement accuracy | LOW-MEDIUM |
| **No track management** | No track initiation logic (M-of-N), no track quality scoring, no track deletion | MEDIUM |

**Prioritized gap summary:**
1. **Model adaptation** (IMM or adaptive Q): The most impactful improvement. Maneuvering targets are the primary failure mode of the current tracker.
2. **Nonlinear measurement handling** (EKF/UKF): Moderate improvement, most beneficial at short range and wide scan angles.
3. **Track management**: Important for operational robustness but orthogonal to filter algorithm choice.

---

## 4. Feasibility Assessment

Since all tracking algorithms run in Python on the host PC, feasibility is **HIGH for all approaches**. There is no FPGA resource constraint. The relevant constraints are:

- **Computational latency:** Must complete tracking update within the scan-to-scan interval (order of milliseconds for 31 beam positions with $M = 32$ chirps each)
- **Python library support:** Availability of well-tested implementations reduces development risk
- **Integration complexity:** How much of the existing GUI codebase needs modification

### 4.1 IMM-Kalman (2-3 Models)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(r \cdot n^3)$ per update, where $r$ = number of models, $n$ = state dimension |
| Computational time (Python) | ~50-200 us per update (NumPy matrix operations) |
| Python library support | `filterpy.IMM` (direct support), `pykalman` (requires custom wrapper) |
| Estimated latency impact | Negligible -- well within scan interval |
| Accuracy improvement | 30-50% RMSE reduction for maneuvering targets (published benchmarks) |
| Implementation effort | Moderate -- requires defining motion models and tuning transition matrix |
| **Verdict** | **FEASIBLE** -- well-supported, proven improvement |

### 4.2 Variational Bayesian IMM

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(r \cdot n^3 \cdot N_\text{iter})$ per update, $N_\text{iter} \approx 3$-$5$ |
| Computational time (Python) | ~200-800 us per update |
| Python library support | No off-the-shelf library; requires custom implementation (~200-400 lines) |
| Estimated latency impact | Negligible |
| Accuracy improvement | 10-25% RMSE improvement over standard IMM during maneuver transitions |
| Implementation effort | High -- variational inference requires careful derivation and testing |
| **Verdict** | **FEASIBLE** -- but higher development risk than standard IMM |

### 4.3 Adaptive Kalman (IAE)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(n^3 + W \cdot n^2)$ per update, $W$ = window size |
| Computational time (Python) | ~30-100 us per update |
| Python library support | Straightforward extension of `filterpy.KalmanFilter` (~50 lines) |
| Estimated latency impact | Negligible |
| Accuracy improvement | 15-30% RMSE improvement for smoothly varying dynamics |
| Implementation effort | Low -- minimal modification to existing filter |
| **Verdict** | **FEASIBLE** -- simplest path to improvement |

### 4.4 EKF/UKF for Nonlinear Measurements

| Property | Value |
|----------|-------|
| Algorithm complexity | EKF: $O(n^3)$; UKF: $O((2n+1) \cdot n^2)$ |
| Computational time (Python) | EKF: ~30-80 us; UKF: ~50-150 us per update |
| Python library support | `filterpy.kalman.ExtendedKalmanFilter`, `filterpy.kalman.UnscentedKalmanFilter` |
| Estimated latency impact | Negligible |
| Accuracy improvement | 5-15% position accuracy improvement at short range and wide scan angles |
| Implementation effort | Low-Moderate -- requires defining measurement function and Jacobian |
| **Verdict** | **FEASIBLE** -- complementary to IMM/adaptive approaches |

### 4.5 Why No FPGA Feasibility Table

All tracking algorithms execute in Python on the host PC, as documented in Section 7 of [`03_software/03_python_gui.md`](../03_software/03_python_gui.md#7-radarprocessor-designed-interface--stub). The FPGA pipeline terminates at detection (USB transfer to host). No FPGA resource table is needed because:

1. The FPGA performs signal processing up to and including detection (Stages 1-9 in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md))
2. Detection results are transferred to the host via FT601 USB 3.0
3. DBSCAN clustering and Kalman tracking are Python-side post-processing
4. All proposed improvements operate within this same Python-side architecture

The computational budget for Python tracking is bounded by the host PC's CPU, which provides orders of magnitude more processing capability than needed for any of the surveyed algorithms operating on the AERIS-10's target count (typically tens of targets per scan).

---

## 5. Recommendations

### Priority 1: IMM-Kalman (Standard 2-3 Model)

- **Expected improvement:** 30-50% RMSE reduction for maneuvering targets; robust tracking through accelerations and turns
- **Resource cost:** Negligible CPU overhead; ~200-300 lines of Python
- **Risk:** LOW -- proven algorithm, direct `filterpy` support, extensive published radar tracking results
- **Investigation steps:**
  1. Define motion models: constant velocity, constant acceleration, and optionally coordinated turn
  2. Tune transition probability matrix $\boldsymbol{\Pi}$ using expected target maneuver statistics
  3. Implement using `filterpy.IMM` with `filterpy.kalman.KalmanFilter` for CV and CA models, `filterpy.kalman.ExtendedKalmanFilter` for CT model
  4. Validate against simulated maneuvering target trajectories (straight segments, acceleration, turns)
  5. Compare RMSE against current fixed-parameter Kalman baseline

### Priority 2: Variational Bayesian IMM

- **Expected improvement:** Additional 10-25% RMSE improvement over standard IMM during maneuver transitions; reduced sensitivity to transition matrix tuning
- **Resource cost:** Negligible CPU overhead; ~300-500 lines of custom Python
- **Risk:** MEDIUM -- newer algorithm, no off-the-shelf library, requires careful variational inference implementation
- **Investigation steps:**
  1. Complete Priority 1 (standard IMM) first as baseline
  2. Implement variational Bayesian mode probability update following the MDPI Electronics 2025 methodology
  3. Validate convergence of variational iterations across operational scenarios
  4. Compare RMSE and maneuver detection latency against standard IMM
  5. Evaluate whether the marginal improvement justifies the added complexity

### Priority 3: Adaptive Process Noise (IAE)

- **Expected improvement:** 15-30% RMSE improvement for smoothly varying dynamics; simpler alternative to IMM for moderate maneuvers
- **Resource cost:** Negligible; ~50 lines added to existing Kalman filter
- **Risk:** LOW -- straightforward extension of existing filter
- **Investigation steps:**
  1. Implement IAE with sliding window ($W = 10$-$20$ samples as starting point)
  2. Add positive semi-definiteness projection for the estimated $\mathbf{Q}$
  3. Compare against IMM for both smooth and abrupt maneuver scenarios
  4. Consider as fallback if IMM complexity is not justified for the target environment

### Supplementary: EKF/UKF Measurement Model

- **Expected improvement:** 5-15% position accuracy improvement, primarily at short range
- **Resource cost:** Negligible; uses existing `filterpy` implementations
- **Risk:** LOW
- **Investigation steps:**
  1. Replace linear $\mathbf{H}$ with EKF Jacobian or UKF sigma points for the $(R, \theta) \to (x, y)$ measurement model
  2. Can be combined with any of the above approaches (IMM-EKF, IMM-UKF, adaptive EKF)
  3. Evaluate whether the improvement justifies the additional complexity for the AERIS-10 scan geometry ($\pm 33°$ azimuth)

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- canonical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Python GUI V6](../03_software/03_python_gui.md) -- current Kalman filter baseline (Eq. SW-3), RadarTarget dataclass, DBSCAN clustering (Eq. SW-2)
- [Antenna & Beamforming Hardware](../02_hardware/04_antenna_beamforming.md) -- beam steering angles and scan range
- [Detection Theory](../01_physics/04_detection_theory.md) -- detection pipeline producing inputs to tracking

### Literature
- Bar-Shalom, Y., Li, X.R., and Kirubarajan, T., *Estimation with Applications to Tracking and Navigation*, Wiley, 2001
- Blom, H.A.P. and Bar-Shalom, Y., "The interacting multiple model algorithm for systems with Markovian switching coefficients," *IEEE Trans. Automatic Control*, vol. 33, no. 8, pp. 780-783, 1988
- Julier, S.J. and Uhlmann, J.K., "Unscented filtering and nonlinear estimation," *Proceedings of the IEEE*, vol. 92, no. 3, pp. 401-422, 2004
- Mehra, R.K., "On the identification of variances and adaptive Kalman filtering," *IEEE Trans. Automatic Control*, vol. 15, no. 2, pp. 175-184, 1970
- Mohamed, A.H. and Schwarz, K.P., "Adaptive Kalman filtering for INS/GPS," *Journal of Geodesy*, vol. 73, pp. 193-203, 1999
- Ristic, B., Arulampalam, S., and Gordon, N., *Beyond the Kalman Filter: Particle Filters for Tracking Applications*, Artech House, 2004
- "Model Adaptive Kalman Filter for Maneuvering Target Tracking," *MDPI Electronics*, vol. 14, no. 10, Article 1908, 2025
