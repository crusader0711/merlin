#!/usr/bin/env python3
"""
Generate beam pattern SVG figures for AERIS-10 beamforming theory document.

Figures:
  1. beam_pattern_N16_uniform.svg -- N=16 ULA, uniform weights, multiple steering angles
  2. beam_pattern_N16_taylor.svg -- N=16 ULA, uniform vs Taylor weighting comparison

Reference: 01_physics/03_beamforming_theory.md
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------------------------
# Array parameters (symbolic values from parameter_table.md)
# ---------------------------------------------------------------------------
N = 16          # Number of array elements
d_over_lam = 0.5  # Element spacing d = lambda/2

# Angular axis
theta_deg = np.linspace(-90, 90, 4001)
theta_rad = np.deg2rad(theta_deg)

# ---------------------------------------------------------------------------
# Helper: compute normalized array factor in dB
# ---------------------------------------------------------------------------

def array_factor_db(theta_rad, N, d_over_lam, theta0_rad, weights=None):
    """
    Compute |AF(theta)|^2 / max in dB.

    Parameters
    ----------
    theta_rad : array
        Observation angles in radians.
    N : int
        Number of elements.
    d_over_lam : float
        Element spacing in wavelengths (d / lambda).
    theta0_rad : float
        Steering angle in radians.
    weights : array or None
        Element amplitude weights (length N). None => uniform.

    Returns
    -------
    af_db : array
        Normalized power pattern in dB.
    """
    k_d = 2 * np.pi * d_over_lam  # k * d
    psi = k_d * (np.sin(theta_rad) - np.sin(theta0_rad))

    if weights is None:
        # Closed-form for uniform weights: sin(N*psi/2) / sin(psi/2)
        numerator = np.sin(N * psi / 2)
        denominator = np.sin(psi / 2)
        # Handle 0/0 at psi = 0
        with np.errstate(divide="ignore", invalid="ignore"):
            af = np.where(np.abs(denominator) < 1e-12, float(N), numerator / denominator)
        af_power = np.abs(af) ** 2 / N ** 2
    else:
        # General weighted sum
        n_vec = np.arange(N)
        # AF = sum_n w_n * exp(j*n*psi)
        af = np.zeros(len(theta_rad), dtype=complex)
        for n in range(N):
            af += weights[n] * np.exp(1j * n * psi)
        af_power = np.abs(af) ** 2 / (np.sum(np.abs(weights)) ** 2)

    af_power = np.maximum(af_power, 1e-10)  # floor to avoid log(0)
    af_db = 10 * np.log10(af_power)
    return af_db


def taylor_weights(N, nbar=5, sll_db=-30):
    """
    Compute Taylor window weights for an N-element array.

    Parameters
    ----------
    N : int
        Number of elements.
    nbar : int
        Number of nearly-constant-level sidelobes adjacent to the main lobe.
    sll_db : float
        Desired peak sidelobe level in dB (negative value).

    Returns
    -------
    w : array
        Taylor window weights of length N.
    """
    # Taylor one-parameter design (Villeneuve / Mailloux formulation)
    B = 10 ** (-sll_db / 20)  # voltage ratio
    A = (1 / np.pi) * np.arccosh(B)
    sigma2 = nbar ** 2 / (A ** 2 + (nbar - 0.5) ** 2)

    # Compute F_m coefficients
    def F_m(m, nbar, A, sigma2):
        num = 1.0
        den = 1.0
        for p in range(1, nbar):
            num *= 1 - m ** 2 / (sigma2 * (A ** 2 + (p - 0.5) ** 2))
            if p != m:
                den *= 1 - m ** 2 / p ** 2
        return num / den

    # Build the window in the spatial domain
    w = np.ones(N)
    for n in range(N):
        x = (n - (N - 1) / 2) / N  # normalized position [-0.5, 0.5]
        val = 0.0
        for m in range(1, nbar):
            Fm = F_m(m, nbar, A, sigma2)
            val += Fm * np.cos(2 * np.pi * m * x)
        w[n] = 1 + 2 * val

    # Normalize to peak of 1
    w = w / np.max(w)
    return w


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
out_dir = Path(__file__).parent

# ---------------------------------------------------------------------------
# Figure 1: Uniform weights, multiple steering angles
# ---------------------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(8, 5))

steering_angles = [0, 15, 33]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
styles = ["-", "--", "-."]

for theta0, color, ls in zip(steering_angles, colors, styles):
    theta0_rad = np.deg2rad(theta0)
    af_db = array_factor_db(theta_rad, N, d_over_lam, theta0_rad)
    label = rf"$\theta_0 = {theta0}°$"
    ax1.plot(theta_deg, af_db, color=color, linestyle=ls, linewidth=1.5, label=label)

ax1.set_xlim(-90, 90)
ax1.set_ylim(-40, 0)
ax1.set_xlabel(r"Angle $\theta$ (degrees)", fontsize=11)
ax1.set_ylabel("Normalized Power (dB)", fontsize=11)
ax1.set_title(r"Beam Pattern -- $N=16$ ULA, Uniform Weights", fontsize=12)
ax1.tick_params(labelsize=10)
ax1.legend(fontsize=9, loc="upper right")
ax1.grid(True, alpha=0.3)
ax1.axhline(-3, color="gray", linewidth=0.8, linestyle=":", alpha=0.5)

fig1.tight_layout()
fig1.savefig(out_dir / "beam_pattern_N16_uniform.svg", format="svg", bbox_inches="tight")
plt.close(fig1)
print("Generated: beam_pattern_N16_uniform.svg")

# ---------------------------------------------------------------------------
# Figure 2: Uniform vs Taylor weighting comparison (broadside)
# ---------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(8, 5))

# Uniform weights
af_uniform_db = array_factor_db(theta_rad, N, d_over_lam, 0.0)
ax2.plot(theta_deg, af_uniform_db, color="#1f77b4", linestyle="-", linewidth=1.5,
         label="Uniform weights")

# Taylor weights (nbar=5, SLL=-30 dB)
tw = taylor_weights(N, nbar=5, sll_db=-30)
af_taylor_db = array_factor_db(theta_rad, N, d_over_lam, 0.0, weights=tw)
ax2.plot(theta_deg, af_taylor_db, color="#d62728", linestyle="--", linewidth=1.5,
         label=r"Taylor ($\bar{n}=5$, SLL $= -30$ dB)")

ax2.set_xlim(-90, 90)
ax2.set_ylim(-50, 0)
ax2.set_xlabel(r"Angle $\theta$ (degrees)", fontsize=11)
ax2.set_ylabel("Normalized Power (dB)", fontsize=11)
ax2.set_title(r"Beam Pattern -- $N=16$ ULA, Uniform vs Taylor Weighting", fontsize=12)
ax2.tick_params(labelsize=10)
ax2.legend(fontsize=9, loc="upper right")
ax2.grid(True, alpha=0.3)
ax2.axhline(-3, color="gray", linewidth=0.8, linestyle=":", alpha=0.5)
ax2.axhline(-30, color="gray", linewidth=0.8, linestyle=":", alpha=0.5)

fig2.tight_layout()
fig2.savefig(out_dir / "beam_pattern_N16_taylor.svg", format="svg", bbox_inches="tight")
plt.close(fig2)
print("Generated: beam_pattern_N16_taylor.svg")

print("Done.")
