# ML-Based Detection Alternatives

**Purpose:** Survey machine learning approaches for radar target detection as alternatives or augmentations to the current fixed threshold detector, evaluating FPGA inference feasibility on the Artix-7 XC7A100T with INT8 quantization constraints.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resources, clock domains
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- signal processing pipeline architecture
- [Detection Theory](../01_physics/04_detection_theory.md) -- CFAR theory and detection performance

---

## 1. Current State

### 1.1 Current Detection Implementation

The AERIS-10 radar currently uses a **fixed magnitude threshold** for target detection, NOT a true CFAR algorithm. The detection logic is implemented inline in `radar_system_top.v` (Stage 9 of the pipeline, see Section 10 of [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#10-stage-8-threshold-detection)).

The detector computes the L1 norm (Manhattan distance) of the Doppler output and compares against a hardcoded constant:

$$
|I| + |Q| > 10{,}000 \tag{SW-7}
$$

This results in an **uncontrolled false alarm rate** that varies with noise level. The detection theory foundation for proper adaptive detection is derived in [`01_physics/04_detection_theory.md`](../01_physics/04_detection_theory.md), including:

- Binary hypothesis testing (Eq. (DET-1))
- Neyman-Pearson optimal detection (Eq. (DET-2))
- CA-CFAR threshold multiplier derivation (Eq. (DET-20))
- CFAR loss analysis (Eq. (DET-24))
- Swerling target models (Eqs. (DET-13) through (DET-16))

The current system has no learning capability, no adaptation to changing noise environments, and no ability to distinguish target types.

### 1.2 Artix-7 Resource Constraints

The XC7A100T FPGA provides the following resources relevant to ML inference (see Section 2.1 of [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#21-device-resources)):

| Resource | Total Available | Currently Used (est.) | Available for ML | Symbol |
|----------|----------------|----------------------|-----------------|--------|
| LUTs | 63,400 | ~16,500 (~26%) | ~46,900 | $N_\text{LUT}$ |
| DSP48E1 slices | 240 | ~88 (~37%) | ~152 | $N_\text{DSP}$ |
| Block RAM (36 Kb) | 135 | ~101 (~75%) | ~34 | $N_\text{BRAM}$ |
| Flip-Flops | 126,800 | -- | -- | $N_\text{FF}$ |

> **Important:** These are theoretical estimates based on Verilog module parameters, pending Vivado implementation reports. All ML feasibility assessments in this document use these estimates as the baseline and should be re-evaluated when Vivado reports become available.

**Critical constraints for ML inference:**

1. **No floating-point hardware:** The Artix-7 has no floating-point units. All ML inference must use fixed-point arithmetic (INT8, INT16, or smaller).
2. **Limited DSP slices:** 240 DSP48E1s total, with ~152 available. Each DSP48E1 can perform one 18x25 multiply-accumulate per clock cycle, or two 8x8 multiplies in packed mode.
3. **Tight BRAM budget:** Only ~34 BRAMs available for ML weight storage. Each 36 Kb BRAM stores 4,096 bytes (INT8) or 2,048 words (INT16). Total ML weight storage capacity: ~34 x 4,096 = ~139 KB in INT8.
4. **No external memory interface:** The XC7A100T in this design has no DDR memory controller. All model weights must reside in on-chip BRAM.

### 1.3 ADC Dynamic Range Limitation

The AD9484 ADC provides 8-bit resolution, yielding a signal-to-quantization-noise ratio (SQNR) of:

$$
\text{SQNR} = 6.02 \times 8 + 1.76 = 49.9~\text{dB}
$$

This limits the dynamic range of the range-Doppler maps that serve as input to any ML-based detector. The 8-bit quantization constrains the range of signal amplitudes that the detector can resolve, which is particularly relevant for ML approaches that operate on amplitude patterns in the range-Doppler map.

> **Open Question (per Phase 5 research):** Whether 8-bit quantized range-Doppler maps provide sufficient resolution for CNN/autoencoder-based detection is a key feasibility question. ML approaches may be more sensitive to ADC bit depth than traditional CFAR, because CFAR operates on relative thresholds while ML models may depend on absolute amplitude patterns learned during training.

---

## 2. Literature Survey

### 2.1 Autoencoder-Based Anomaly Detection

Autoencoders learn a compressed representation of "normal" data (noise-only range-Doppler patches) and detect anomalies (targets) by measuring reconstruction error. When a target is present, the autoencoder cannot accurately reconstruct the range-Doppler patch, producing a high reconstruction error that triggers detection.

**Architecture for FPGA deployment:**

A small autoencoder suitable for Artix-7 implementation:

| Layer | Type | Input Size | Output Size | Parameters (INT8) |
|-------|------|-----------|------------|-------------------|
| Encoder L1 | Dense + ReLU | 64 | 32 | 64 x 32 + 32 = 2,080 |
| Encoder L2 | Dense + ReLU | 32 | 16 | 32 x 16 + 16 = 528 |
| Decoder L1 | Dense + ReLU | 16 | 32 | 16 x 32 + 32 = 544 |
| Decoder L2 | Dense + Sigmoid | 32 | 64 | 32 x 64 + 64 = 2,112 |
| **Total** | | | | **5,264 parameters** |

The input is a flattened patch from the range-Doppler map (e.g., 8 range bins x 8 Doppler bins = 64 values). The reconstruction error is computed as the mean squared error (MSE) between input and output, compared against a learned threshold.

**Published reference:** PMC 9370841 demonstrates an autoencoder-based target detection approach for MIMO FMCW radar, achieving detection performance comparable to CFAR in homogeneous environments with improved performance in non-homogeneous clutter.

**FPGA resource estimate for INT8 inference:**

| Resource | Estimate | Calculation |
|----------|----------|-------------|
| LUTs | ~2,000--4,000 | MAC units, activation functions, control logic |
| DSPs | 20--40 | INT8 multiply-accumulate; can use packed 8x8 mode (2 MACs per DSP) |
| BRAMs | 5--10 | Weight storage (~5.3 KB for 5,264 INT8 parameters = 2 BRAMs; input/output buffers add 3--8 BRAMs) |
| Clock cycles per inference | ~300--600 | Sequential MAC with partial parallelism |

**INT8 quantization impact:** Post-training quantization from FP32 to INT8 typically incurs 1--3% accuracy loss for small dense networks. Quantization-aware training can reduce this to <1%. The 8-bit ADC input already limits input precision to 8 bits, so INT8 inference is naturally aligned with the input data precision.

**Interaction with 8-bit ADC:** The autoencoder input is already limited to 8-bit dynamic range by the AD9484. This actually simplifies the quantization challenge -- INT8 weights operating on 8-bit inputs produce 16-bit intermediate results that fit within the DSP48E1's 18-bit input width. However, the limited 49.9 dB SQNR means that weak targets near the noise floor may be indistinguishable from quantization noise, reducing the autoencoder's ability to detect low-SNR targets compared to approaches that benefit from higher dynamic range.

### 2.2 CNN Range-Doppler Detectors

Convolutional neural networks (CNNs) can process 2D range-Doppler maps directly, learning spatial patterns associated with targets, clutter, and noise. CNN-based detectors can potentially learn features that are not captured by threshold-based methods.

**Model size constraints on XC7A100T:**

The available on-chip storage (~34 BRAMs x 4,096 bytes = ~139 KB in INT8) constrains the maximum model size:

| Model Class | Parameters | INT8 Storage | BRAMs Required | Feasibility |
|-------------|-----------|-------------|---------------|-------------|
| Tiny CNN (<10K params) | ~5K--10K | 5--10 KB | 2--3 | FEASIBLE (resource-wise) |
| Small CNN (10K--50K params) | ~10K--50K | 10--50 KB | 3--13 | MARGINAL |
| Medium CNN (50K--100K params) | ~50K--100K | 50--100 KB | 13--25 | MARGINAL (BRAM-constrained) |
| Large CNN (>100K params) | >100K | >100 KB | >25 | INFEASIBLE (exceeds BRAM budget) |

**Tiny CNN architecture example:**

| Layer | Type | Input | Output | Params (INT8) | Notes |
|-------|------|-------|--------|---------------|-------|
| Conv1 | 3x3, 4 filters | 8x32x1 | 8x32x4 | 3x3x1x4 + 4 = 40 | Range-Doppler input (8 range x 32 Doppler) |
| Pool1 | 2x2 max pool | 8x32x4 | 4x16x4 | 0 | Reduces spatial dimensions |
| Conv2 | 3x3, 8 filters | 4x16x4 | 4x16x8 | 3x3x4x8 + 8 = 296 | Feature extraction |
| Pool2 | 2x2 max pool | 4x16x8 | 2x8x8 | 0 | Further reduction |
| FC1 | Dense + ReLU | 128 | 32 | 128x32 + 32 = 4,128 | Classification |
| FC2 | Dense + Sigmoid | 32 | 1 | 32x1 + 1 = 33 | Detection output |
| **Total** | | | | **4,497 params** | ~4.5 KB INT8 |

**FPGA resource estimate for tiny CNN (INT8):**

| Resource | Estimate | Notes |
|----------|----------|-------|
| LUTs | ~4,000--8,000 | Convolution datapath, pooling, FC layers |
| DSPs | 16--32 | Convolution MAC units; 3x3 kernel requires 9 MACs per output pixel |
| BRAMs | 3--8 | Weight storage + feature map double buffering |
| Clock cycles per inference | ~1,000--5,000 | Depends on parallelism vs. resource sharing |

**Published references:**
- arXiv 2509.04153 surveys real-time FPGA-based CNN implementations, demonstrating INT8 inference on Zynq and Kintex-class FPGAs. Artix-7 implementations are rare due to resource constraints.
- PMC 10857097 presents an FPGA-based CNN+LSTM architecture for radar signal recognition, achieving real-time performance on a Kintex UltraScale FPGA with ~100K parameters.

> **Critical note (per Pitfall 2):** GPU and cloud benchmarks are NOT evidence of Artix-7 feasibility. The Kintex UltraScale FPGA used in PMC 10857097 has ~10x the DSP slices and ~5x the BRAM of the Artix-7 XC7A100T. Resource estimates in this section are specifically scaled for the XC7A100T.

**INT8 quantization impact on CNN detection accuracy:** Published results show that INT8 quantization of small CNNs (<50K parameters) typically reduces classification accuracy by 1--5% compared to FP32 baseline. For radar detection (binary classification: target/no-target), the impact may be smaller than for multi-class classification tasks. However, the 8-bit ADC input dynamic range (49.9 dB SQNR) is a more fundamental limitation: the CNN cannot learn features at resolutions finer than the ADC quantization step, regardless of model precision.

### 2.3 Hybrid CFAR + ML Approaches

Hybrid approaches combine traditional CFAR detection on the FPGA with ML-based post-processing on the host PC. This architecture avoids the FPGA resource constraint entirely for the ML portion while leveraging the FPGA's strength in real-time signal processing.

**Architecture:**

```
FPGA Pipeline                          Host PC (Python)
-----------------                      ----------------
ADC -> DDC -> Matched Filter           Receive USB data
    -> Doppler FFT -> CFAR             CFAR detections
    -> USB Output  ----USB 3.0---->    ML classification
                                       (CNN, autoencoder,
                                        random forest, etc.)
```

**FPGA-side changes:** Replace the current fixed threshold (Eq. (SW-7)) with a true CA-CFAR implementation (see Phase 5 SWRES-01 for CFAR variant analysis). CFAR requires ~2,000--4,000 LUTs, 2--4 DSPs, and 2--4 BRAMs -- well within Artix-7 headroom.

**Host PC-side ML options:**

| Approach | Model Size | Inference Time (Python) | Training Data Required | Notes |
|----------|-----------|------------------------|----------------------|-------|
| Random forest classifier | 10--100 trees | <1 ms per frame | ~1,000+ labeled frames | Lightweight, interpretable |
| Small CNN (PyTorch) | 50K--500K params | 1--10 ms per frame | ~5,000+ labeled frames | Good for spatial pattern recognition |
| Autoencoder anomaly detection | 5K--50K params | <1 ms per frame | ~1,000+ noise-only frames | Unsupervised; no target labels needed |
| LSTM sequence classifier | 10K--100K params | 1--5 ms per frame | ~2,000+ labeled sequences | Temporal pattern recognition |

**Advantages of hybrid approach:**
1. No FPGA resource constraint for ML -- host PC has effectively unlimited compute and memory
2. Model can be updated without FPGA re-synthesis -- Python model weights are loaded at runtime
3. Full floating-point precision -- no INT8 quantization accuracy loss
4. Larger model capacity -- can use models with >1M parameters if needed
5. Access to standard ML frameworks (PyTorch, scikit-learn, TensorFlow)

**Disadvantages:**
1. USB transfer latency -- adds several ms to detection pipeline
2. Host PC must be powered and running -- not suitable for standalone FPGA operation
3. Real-time constraint depends on host PC processing speed
4. ML classification occurs after CFAR pre-filtering -- cannot improve raw detection sensitivity

**Integration with current system:** The AERIS-10 already has a host PC running `GUI_V6.py` that receives USB data. The hybrid approach adds ML post-processing to the existing Python pipeline with minimal architectural change.

---

## 3. Gap Analysis

### 3.1 No ML Capability

**Gap:** The current system has no machine learning capability. Detection is performed by a fixed threshold comparator with no learning or adaptation. There is no mechanism for the detector to improve based on experience or adapt to changing environmental conditions.

### 3.2 Fixed Threshold Limitations

**Gap:** The fixed threshold $|I| + |Q| > 10{,}000$ (Eq. (SW-7)) cannot adapt to varying noise levels, clutter environments, or interference. The false alarm rate varies directly with noise power, violating the constant false alarm rate principle derived in Eq. (DET-19) and (DET-20) of the [detection theory](../01_physics/04_detection_theory.md).

### 3.3 No Training Data Available

**Gap:** No labeled training data (range-Doppler maps with known target locations) exists for the AERIS-10 system. All ML approaches require training data, though the amount varies:
- Supervised approaches (CNN, random forest) require target-labeled data
- Unsupervised approaches (autoencoder) require only noise-only data for baseline learning
- Training data acquisition requires controlled field experiments with known target positions

**Impact:** Training data collection is a prerequisite for any ML approach and represents a significant effort that must precede ML development.

### 3.4 8-Bit ADC Dynamic Range Constraint

**Gap:** The AD9484's 8-bit resolution provides 49.9 dB SQNR, which limits the dynamic range of input data for any ML model. This constrains:
- The ability to detect weak targets near the noise floor
- The resolution of amplitude features in the range-Doppler map
- The effective number of distinguishable amplitude levels (256 for 8-bit unsigned)

ML models trained on higher-precision data would need to be re-evaluated for 8-bit input compatibility. The quantization floor is a fundamental limit that ML cannot overcome.

---

## 4. Feasibility Assessment

> **Note:** All resource estimates are based on theoretical utilization from Phase 3, pending Vivado implementation reports. All ML-specific resource estimates are extrapolated from published implementations on similar-class FPGAs and should be validated through actual synthesis.

### 4.1 Autoencoder-Based Detection (On-FPGA)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{params})$ per inference (~5,264 MACs) |
| Model size | ~5,264 parameters (INT8) |
| Estimated LUTs | ~2,000--4,000 |
| Estimated DSPs | 20--40 (packed 8x8 mode: ~10--20 DSP slices) |
| Estimated BRAMs | 5--10 |
| Current LUT utilization after | ~29--32% |
| Current DSP utilization after | ~45--53% |
| Current BRAM utilization after | **~79--83%** |
| Inference latency | ~300--600 clock cycles at 100 MHz ($3{-}6~\mu\text{s}$) |
| Pipeline integration | Parallel to or replacing Stage 9 (threshold detection) |
| Training data requirement | ~1,000+ noise-only frames (unsupervised) |
| INT8 accuracy impact | 1--3% accuracy loss vs. FP32 (typical for small dense networks) |
| 8-bit ADC compatibility | ALIGNED -- INT8 inference matches ADC input precision |
| Verdict | **MARGINAL** -- fits within resource budget but competes with FFT modules for DSPs; BRAM utilization approaches 83% |

### 4.2 Tiny CNN Detector (On-FPGA)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(K^2 \cdot C_\text{in} \cdot C_\text{out} \cdot H \cdot W)$ per conv layer |
| Model size | ~4,497 parameters (INT8, tiny architecture) |
| Estimated LUTs | ~4,000--8,000 |
| Estimated DSPs | 16--32 |
| Estimated BRAMs | 3--8 |
| Current LUT utilization after | ~32--39% |
| Current DSP utilization after | ~43--50% |
| Current BRAM utilization after | **~77--81%** |
| Inference latency | ~1,000--5,000 clock cycles at 100 MHz ($10{-}50~\mu\text{s}$) |
| Pipeline integration | Parallel to or replacing Stage 9 |
| Training data requirement | ~5,000+ labeled frames (supervised) |
| INT8 accuracy impact | 1--5% accuracy loss vs. FP32 |
| 8-bit ADC compatibility | INPUT-LIMITED -- CNN feature learning limited by 8-bit dynamic range |
| Published FPGA reference | No direct Artix-7 radar detection CNN found; estimates extrapolated from Kintex/Zynq literature |
| Verdict | **MARGINAL** for tiny models (<10K params); **INFEASIBLE** for larger models (>50K params due to BRAM) |

### 4.3 Hybrid CFAR + ML (ML on Host PC)

| Property | Value |
|----------|-------|
| FPGA changes | Replace fixed threshold with CA-CFAR (~2,000--4,000 LUTs, 2--4 DSPs, 2--4 BRAMs) |
| Host PC ML model | Unconstrained (Python/PyTorch, any model size) |
| Additional LUTs (FPGA) | ~2,000--4,000 (for CFAR only) |
| Additional DSPs (FPGA) | 2--4 (for CFAR only) |
| Additional BRAMs (FPGA) | 2--4 (for CFAR only) |
| Current LUT utilization after | ~29--32% |
| Current DSP utilization after | ~38--39% |
| Current BRAM utilization after | ~76--78% |
| End-to-end latency | FPGA pipeline + USB transfer + Python inference (~10--50 ms total) |
| Pipeline integration | CFAR replaces Stage 9 on FPGA; ML post-processing added to `GUI_V6.py` |
| Training data requirement | Varies by approach (1,000--5,000+ frames) |
| INT8 accuracy impact | None -- host PC uses FP32 |
| 8-bit ADC compatibility | Same limitation as all approaches -- ML cannot exceed ADC dynamic range |
| Verdict | **FEASIBLE** -- leverages existing host PC; only CFAR added to FPGA |

### 4.4 Summary Table

| Approach | LUT Impact | DSP Impact | BRAM Impact | Training Data | 8-Bit ADC | Verdict |
|----------|-----------|-----------|------------|---------------|-----------|---------|
| Autoencoder (FPGA) | +3--6% | +8--17% | +4--7% | 1,000+ frames | Aligned | **MARGINAL** |
| Tiny CNN (FPGA) | +6--13% | +7--13% | +2--6% | 5,000+ frames | Input-limited | **MARGINAL** |
| Large CNN (FPGA) | >15% | >20% | >18% | 10,000+ frames | Input-limited | **INFEASIBLE** |
| Hybrid CFAR+ML | +3--6% | +1--2% | +1--3% | 1,000+ frames | Same for all | **FEASIBLE** |

---

## 5. Recommendations

### Priority 1: Hybrid CFAR + ML (Host PC)

- **Expected improvement:** Controlled $P_{fa}$ via CFAR (replacing fixed threshold), plus ML-based target classification and false alarm rejection on host PC
- **FPGA resource cost:** ~2,000--4,000 LUTs, 2--4 DSPs, 2--4 BRAMs (CFAR only)
- **Risk:** LOW -- CFAR is well-understood (see SWRES-01); ML runs on unconstrained host PC
- **Rationale:** This is the most practical approach because it avoids the FPGA resource constraint entirely for the ML portion. The AERIS-10 already has a host PC running `GUI_V6.py` that receives all pipeline data via USB. Adding ML post-processing to the Python pipeline requires no FPGA redesign beyond implementing CFAR (which is recommended independently in SWRES-01).
- **Prerequisites:**
  1. Implement CA-CFAR on FPGA (see SWRES-01 for variant analysis)
  2. Collect labeled training data through controlled field experiments
  3. Develop Python ML pipeline in `GUI_V6.py` or companion module
- **Investigation steps:**
  1. Implement CA-CFAR as recommended in SWRES-01
  2. Design data collection protocol for labeled range-Doppler maps (target type, position, SNR)
  3. Prototype random forest classifier on collected data as baseline ML approach
  4. Evaluate autoencoder anomaly detection as unsupervised alternative (requires only noise-only data)
  5. Compare ML-augmented detection performance against CFAR-only baseline

### Priority 2: Tiny Autoencoder (On-FPGA)

- **Expected improvement:** Anomaly-based detection that adapts to learned noise characteristics; potential improvement in non-homogeneous clutter environments where CFAR performance degrades
- **FPGA resource cost:** ~2,000--4,000 LUTs, 20--40 DSPs, 5--10 BRAMs
- **Risk:** MEDIUM-HIGH -- BRAM utilization reaches ~83%; DSP competition with FFT modules; no published Artix-7 radar autoencoder implementation for validation
- **Rationale:** The autoencoder approach requires only noise-only training data (unsupervised), reducing the training data acquisition burden. The INT8 inference is naturally aligned with the 8-bit ADC input precision. However, the resource requirements are non-trivial and compete with the existing FFT/matched filter for DSP slices.
- **Prerequisites:**
  1. Validate BRAM availability via Vivado synthesis of current design
  2. Collect noise-only range-Doppler map data for autoencoder training
  3. Train and quantize autoencoder model offline (Python/PyTorch)
  4. Evaluate INT8 quantization impact on reconstruction error threshold
- **Investigation steps:**
  1. Train FP32 autoencoder on simulated or measured noise-only range-Doppler patches
  2. Quantize to INT8 using post-training quantization and quantization-aware training
  3. Evaluate detection performance vs. CFAR on simulated data with known targets
  4. Synthesize INT8 inference engine in Vivado to obtain actual resource utilization on XC7A100T
  5. Compare detection ROC curves: autoencoder vs. CFAR vs. fixed threshold

### Priority 3: CNN Detector (On-FPGA, Research-Stage)

- **Expected improvement:** Spatial pattern recognition in range-Doppler maps; potential to learn complex clutter/target discrimination features
- **FPGA resource cost:** ~4,000--8,000 LUTs, 16--32 DSPs, 3--8 BRAMs (tiny model only)
- **Risk:** HIGH -- FPGA feasibility uncertain for Artix-7; no published XC7A100T radar CNN implementation; 8-bit ADC limits feature learning; large labeled dataset required
- **Rationale:** CNN-based detection offers the most powerful feature learning capability but faces the most severe feasibility constraints on the Artix-7. The 8-bit ADC dynamic range limitation compounds the FPGA resource constraint: even if a CNN fits on the FPGA, the limited input dynamic range may prevent the CNN from learning features that outperform simpler approaches like CFAR. This approach is recommended for research evaluation only, not near-term deployment.
- **Prerequisites:**
  1. All Priority 1 and Priority 2 prerequisites
  2. Large labeled dataset (5,000+ frames with target annotations)
  3. Vivado resource validation confirming BRAM and DSP availability
- **Investigation steps:**
  1. Define tiny CNN architecture constrained to <10K INT8 parameters
  2. Train on simulated range-Doppler data with synthetic targets at various SNR levels
  3. Evaluate INT8 quantization impact on detection probability vs. false alarm rate
  4. Synthesize INT8 CNN inference engine on XC7A100T and measure actual resource utilization
  5. Compare detection performance against CFAR baseline at equivalent false alarm rates
  6. Assess whether CNN detection gains justify the resource cost over CFAR

### Training Data Prerequisite

All ML approaches require training data, which does not currently exist for the AERIS-10 system. Training data collection is a non-trivial prerequisite that should begin before any ML development:

| Data Type | Collection Method | Volume | ML Approaches Served |
|-----------|------------------|--------|---------------------|
| Noise-only frames | Record with no targets present | ~1,000+ frames | Autoencoder (unsupervised) |
| Labeled target frames | Controlled experiments with known target positions | ~5,000+ frames | CNN, random forest (supervised) |
| Multi-environment data | Record across weather, clutter, interference conditions | ~10,000+ frames | All approaches (robustness) |

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- Section 5 (Signal Processing) and Section 6 (Software Signal Processing)
- [Parameter Table](../00_notation/parameter_table.md) -- Signal Processing (FPGA) section
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity (Section 2), clock domains (Section 3)
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- threshold detection (Section 10, Eq. (SW-7))
- [Detection Theory](../01_physics/04_detection_theory.md) -- CFAR derivation (Eqs. (DET-17) through (DET-24)), Swerling models

### External References
- [PMC 9370841](https://pmc.ncbi.nlm.nih.gov/articles/PMC9370841/) -- Autoencoder-based target detection in MIMO FMCW radar
- [arXiv 2509.04153](https://arxiv.org/abs/2509.04153) -- Survey of real-time FPGA-based CNN implementations
- [PMC 10857097](https://pmc.ncbi.nlm.nih.gov/articles/PMC10857097/) -- Efficient FPGA CNN+LSTM architecture for radar signal recognition
- Xilinx, *7 Series DSP48E1 Slice User Guide* (UG479) -- DSP48E1 packed arithmetic modes for INT8 inference
- Xilinx, *Artix-7 FPGAs Data Sheet: DC and AC Switching Characteristics* (DS181)
- Goodfellow, I., Bengio, Y., and Courville, A., *Deep Learning*, MIT Press, 2016 -- Autoencoder theory (Ch. 14), CNN architectures (Ch. 9)
- Jacob, B. et al., "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference," *CVPR*, 2018 -- INT8 quantization methodology
