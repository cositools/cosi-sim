"""
Estimate the detection significance of the DC5 dark-matter annihilation signal in the 3-month mock dataset.

Inputs (all from the DC4 mock dataset):
  * total background count spectrum and Crab count spectrum, digitized from
    cosi-data-challenges/data-products/images/spectrum.png (counts / keV / s, all reconstructed Compton events)
  * DC4 Crab input spectrum (cosi-sim DC4/sources/Galactic/Crab) -> effective exposure A(E) = counts / flux
  * DC4 orientation file -> exposure of the dark-matter region relative to the Crab
  * DC4 annihilation map (cosi-sim DC4/sources/DarkMatter/Annihilation_eeg_NFW) -> spatial template

Method (on/off in Compton data space, statistics only):
  S_i = T * A(E_i) * kappa * eps_ARM * Phi_DM(<R, E_i) * dE_i
  B_i = T * B_tot(E_i) * f_cone(R, E_i) * dE_i,      f_cone = <sin(phi)> * sin(R + ARM_FWHM(E))
  Z   = sqrt( sum_i S_i^2 / B_i )                     (Asimov, S << B), maximised over the ROI radius R
f_cone is the fraction of (isotropic) background events whose Compton cone passes within R + ARM of the
ROI centre; eps_ARM is the fraction of signal events whose cone passes within that band.
"""
import json, gzip, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dm_model import fsr_ap

T_OBS = 92.36 * 86400                     # s, DC4/DC5 observation (orientation file span)
SIN_PHI = 0.64                            # <sin phi> for Compton scatter angles ~uniform in 0-90 deg
EPS_ARM = 0.7                             # signal containment within +-ARM FWHM of the ROI edge

D = json.load(open(os.path.join(HERE, "dc4_spectrum_digitized.json")))
tot = np.array(D["total"]); crab = np.array(D["darkorange"])
crabE, crabF = np.array(D["crabE"]), np.array(D["crabF"])
def loginterp(a, E): return np.exp(np.interp(np.log(E), np.log(a[:, 0]), np.log(a[:, 1])))
def A_eff(E):        # cm2 (time-averaged, all-sky event selection), from the Crab
    return loginterp(crab, E) / np.exp(np.interp(np.log(E), np.log(crabE), np.log(crabF)))
def B_tot(E): return loginterp(tot, E)     # counts / keV / s
def arm_fwhm(E):     # deg; 4.1 deg @ 511 keV, 2.1 deg @ 1809 keV (Tomsick et al. 2023), power law in between
    k = np.log(4.1 / 2.1) / np.log(1809 / 511)
    return np.clip(4.1 * (E / 511.0) ** (-k), 1.5, 10.0)
def f_cone(R, E): return SIN_PHI * np.sin(np.radians(R + arm_fwhm(E)))

# ---------------- spatial template and exposure from DC4 files
def load_dm_template(map_path):
    """Spatial template of the DC4 annihilation map (the map is separable: J(l, b) x dN/dE)."""
    import mapflux
    pa, ta, ea, c = mapflux.load(map_path)
    S = c[:, :, 0]
    l = np.radians(pa)[:, None]; b = np.radians(90 - ta)[None, :]
    dOm = np.radians(pa[1] - pa[0]) * np.radians(ta[1] - ta[0]) * np.cos(b) * np.ones_like(l)
    psi = np.degrees(np.arccos(np.clip(np.cos(b) * np.cos(l), -1, 1)))
    return S, dOm, psi, np.degrees(l) * np.ones_like(b), np.degrees(b) * np.ones_like(l)

def relative_exposure(ori_path, lgrid, bgrid, weights, ncut=4):
    """Exposure of a weighted sky region relative to the Crab, sum over time of live * A(theta),
    with A(theta) = cos(theta) for theta < 90 deg (uses every ncut-th orientation bin)."""
    rows = [l.split()[1:10] for i, l in enumerate(gzip.open(ori_path, "rt")) if l.startswith("OG") and i % ncut == 0]
    a = np.array(rows, float)
    def u(l, b): l, b = np.radians(l), np.radians(b); return np.stack([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)], -1)
    z = u(a[:, 4], a[:, 3]); live = a[:, 8]
    def expo(v): return np.sum(live * np.clip(z @ v, 0, None))
    crab = expo(u(184.5575, -5.78434))
    sel = weights > weights.max() * 1e-3
    vs = u(lgrid[sel], bgrid[sel]); w = weights[sel]
    ex = np.array([expo(v) for v in vs[:: max(1, len(vs) // 400)]]); ww = w[:: max(1, len(vs) // 400)]
    return float(np.sum(ex * ww) / np.sum(ww) / crab)

def significance(m_mev, sv, kappa, frac_in_R, Phi_total_sv_m, Rs, Ebins):
    """Phi_total_sv_m(E): all-sky DM intensity spectrum (ph/cm2/s/keV) for given m, sv."""
    Ec = np.sqrt(Ebins[1:] * Ebins[:-1]); dE = np.diff(Ebins)
    best = (0, None)
    for R in Rs:
        S = T_OBS * A_eff(Ec) * kappa * EPS_ARM * frac_in_R(R) * Phi_total_sv_m(Ec, m_mev, sv) * dE
        B = T_OBS * B_tot(Ec) * f_cone(R, Ec) * dE
        Z = np.sqrt(np.sum(S**2 / B))
        if Z > best[0]: best = (Z, R, S.sum(), B.sum())
    return best

if __name__ == "__main__":
    print("A_eff (cm2):", {E: round(float(A_eff(E)), 1) for E in [200, 300, 511, 1000, 1809, 3000]})
    # ---- calibration: COSI 3-sigma 2-yr narrow-line point-source sensitivities (Tomsick et al. 2023)
    T2 = 2 * 365.25 * 86400
    for E, fwhm_keV, ref in [(511, 6.0, 1.2e-5), (1809, 11.0, 3.0e-6)]:
        win = 2 * fwhm_keV                          # +-1 FWHM window, ~98% of a Gaussian line
        B = T2 * B_tot(E) * win * f_cone(0.0, E)
        # point source: ROI radius 0, signal containment EPS_ARM, line containment 0.98
        F3 = 3 * np.sqrt(B) / (T2 * A_eff(E) * EPS_ARM * 0.98)
        print(f"calibration {E} keV: predicted 3-sigma 2-yr line sensitivity {F3:.2e} vs published {ref:.1e} (ratio {F3/ref:.2f})")
