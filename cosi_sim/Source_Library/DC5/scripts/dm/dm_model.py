"""Annihilating MeV dark matter (chi chi -> e+ e- gamma, FSR) with an NFW halo: model pieces."""
import numpy as np
ALPHA = 1 / 137.035999
ME = 0.51099895          # MeV
KPC = 3.0856775814913673e21  # cm
# NFW parameters of Cirelli et al. 2011 (PPPC4DMID), Table 1
RS_KPC, RHOS_GEV, RSUN_KPC = 24.42, 0.184, 8.33

def rho_nfw(r_kpc):
    x = r_kpc / RS_KPC
    return RHOS_GEV / (x * (1 + x) ** 2)          # GeV/cm3

def jfactor_density(l_deg, b_deg, smax_kpc=200.0, n=4000):
    """J per steradian, int rho^2 ds along the line of sight, in GeV^2 cm^-5 (log-spaced quadrature)."""
    l, b = np.radians(l_deg), np.radians(b_deg)
    cospsi = np.cos(b) * np.cos(l)
    s = np.logspace(-4, np.log10(smax_kpc), n)
    sh = s.reshape((1,) * np.ndim(cospsi) + (-1,))
    r = np.sqrt(RSUN_KPC**2 + sh**2 - 2 * RSUN_KPC * sh * np.expand_dims(cospsi, -1))
    return np.trapezoid(rho_nfw(r) ** 2, sh, axis=-1) * KPC

def fsr_ap(E_mev, m_mev):
    """Altarelli-Parisi FSR photon spectrum per annihilation (dN/dE, 1/MeV), chi chi -> e+ e- gamma, sqrt(s) = 2 m."""
    s = (2 * m_mev) ** 2
    x = 2 * E_mev / np.sqrt(s)
    out = np.zeros_like(E_mev, dtype=float)
    ok = (x > 0) & (x < 1)
    xx = x[ok]
    L = np.log(s * (1 - xx) / ME**2) - 1
    dndx = ALPHA / np.pi * (1 + (1 - xx) ** 2) / xx * np.clip(L, 0, None)
    out[ok] = dndx * 2 / np.sqrt(s)
    return out
