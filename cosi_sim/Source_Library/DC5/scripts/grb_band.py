"""cosima's Band spectrum for the DC5 GRBs.

cosima's Band keyword is "Band Emin Emax alpha beta E0": the photon spectrum is E^alpha exp(-E/E0) below the
break (alpha - beta) E0 (MCSource::BandFunction), so Epeak = (2 + alpha) E0, and cosima requires E0 > Emin.
The DC5 draw gives Epeak; where E0 = Epeak / (2 + alpha) would not be above Emin, Epeak is drawn again from
the same distribution with a separate random generator (seed + 1), so the other draws are unchanged.
"""
import numpy as np


def band_e0(alpha, epeak):
    """E0 (keV) for cosima's Band keyword."""
    return epeak / (2 + alpha)


def draw_epeak(rng, short):
    """Epeak (keV) from the Fermi GBM 10-yr catalog fluence-spectrum distribution (Poolakkil et al. 2021)."""
    if short:
        return float(np.clip(10 ** rng.normal(np.log10(413), 0.35), 150, 2000))
    return float(np.clip(10 ** rng.normal(np.log10(144), 0.38), 60, 1200))


def epeak_for_cosima(alpha, epeak, emin, short, rng_e0):
    """epeak if E0 > emin, otherwise a new Epeak from the same distribution with E0 > emin."""
    while band_e0(alpha, epeak) <= emin:
        epeak = draw_epeak(rng_e0, short)
    return epeak
