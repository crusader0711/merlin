"""Generate detection probability curve SVG figures for Swerling Cases 0 and I.

Uses numerical computation of the Marcum Q-function via numerical integration
(no scipy dependency). Generates publication-quality SVG figures.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def _bessel_i0(z):
    """Compute modified Bessel function I_0(z) via power series.

    I_0(z) = sum_{k=0}^{K} (z^2/4)^k / (k!)^2
    """
    z = np.asarray(z, dtype=np.float64)
    result = np.ones_like(z)
    term = np.ones_like(z)
    z2_over_4 = z**2 / 4.0
    for k in range(1, 80):
        term = term * z2_over_4 / (k * k)
        result += term
        if np.all(np.abs(term) / (np.abs(result) + 1e-300) < 1e-15):
            break
    return result


def marcum_q1_scalar(a, b):
    """Compute Marcum Q-function Q_1(a, b) for scalar a, scalar b.

    Q_1(a,b) = integral_b^inf x * exp(-(x^2+a^2)/2) * I_0(a*x) dx
    """
    if b <= 0:
        return 1.0
    if a <= 0:
        return np.exp(-b**2 / 2.0)

    # Check for very large arguments
    exp_check = -(a**2 + b**2) / 2.0
    if exp_check < -700:
        return 1.0 if a > b else 0.0

    # Numerical integration using trapezoidal rule
    upper = max(a + 8.0 * np.sqrt(1.0 + a), b + 30.0, 50.0)
    num_pts = 4000
    x = np.linspace(b, upper, num_pts)

    ax = a * x
    i0_vals = _bessel_i0(ax)

    # Compute integrand in log-space for stability then exponentiate
    log_integrand = np.log(x + 1e-300) - (x**2 + a**2) / 2.0 + np.log(i0_vals + 1e-300)
    max_log = np.max(log_integrand)
    integrand = np.exp(log_integrand - max_log)

    result = np.exp(max_log) * np.trapezoid(integrand, x)
    return min(max(result, 0.0), 1.0)


def pd_swerling0(snr_linear, pfa):
    """Detection probability for Swerling Case 0 (non-fluctuating).

    P_d = Q_1(sqrt(2*SNR), sqrt(-2*ln(P_fa)))
    """
    snr_arr = np.atleast_1d(snr_linear)
    b = np.sqrt(-2.0 * np.log(pfa))
    result = np.zeros_like(snr_arr, dtype=np.float64)
    for i, snr in enumerate(snr_arr):
        a = np.sqrt(2.0 * snr)
        result[i] = marcum_q1_scalar(a, b)
    return result


def pd_swerling1(snr_linear, pfa):
    """Detection probability for Swerling Case I (single pulse).

    P_d = P_fa^(1/(1+SNR))
    """
    return pfa ** (1.0 / (1.0 + snr_linear))


def make_figure(pd_func, title, filename, pfa_values):
    """Generate a detection probability curve figure."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

    snr_db = np.linspace(0, 25, 300)
    snr_linear = 10.0 ** (snr_db / 10.0)

    line_styles = ['-', '--', '-.', ':']
    colors = ['#1f77b4', '#d62728', '#2ca02c', '#9467bd']

    for i, pfa in enumerate(pfa_values):
        pd = pd_func(snr_linear, pfa)
        label = r'$P_{fa} = 10^{' + str(int(np.log10(pfa))) + r'}$'
        ax.plot(snr_db, pd, linestyle=line_styles[i], color=colors[i],
                linewidth=1.5, label=label)

    ax.set_xlabel('SNR (dB)', fontsize=11)
    ax.set_ylabel(r'$P_d$', fontsize=11)
    ax.set_title(title, fontsize=12)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 1.02)
    ax.tick_params(labelsize=10)
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)

    # Clean style
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

    fig.tight_layout()
    fig.savefig(filename, format='svg', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {filename}")


if __name__ == '__main__':
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    pfa_values = [1e-4, 1e-6, 1e-8, 1e-10]

    make_figure(
        pd_swerling0,
        'Detection Probability -- Swerling Case 0',
        os.path.join(script_dir, 'detection_curves_swerling0.svg'),
        pfa_values
    )

    make_figure(
        pd_swerling1,
        'Detection Probability -- Swerling Case I',
        os.path.join(script_dir, 'detection_curves_swerling1.svg'),
        pfa_values
    )
