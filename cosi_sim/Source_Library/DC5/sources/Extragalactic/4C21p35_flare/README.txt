DC3 4C 21.35:

We present a lightcurve showing 2 states: a flaring state and a quiescent state.
The Flaring state is defined every time in which the average flux is 3 times greater than the 16-years average flux (given by Fermi).

The two states come with two different spectra: both powerlaws with different indices 
- index_COSI_noflare = 1.6
- index_COSI_flare = 2.5
and normalization derived from the integrated flux in COSI energy band derived from the extrapolation of the Fermi-LAT log parabola:


def LogParabola(norm_keV, index1, index2, pivot_energy):
    """Returns a spline of a LogParabola spectrum with given parameters
    """
    _ee = _ENERGY = np.logspace(-2, np.log10(800000), 10000)
    _spec = norm*(_ENERGY/pivot_energy)**(-index1-index2*np.log(_ENERGY/pivot_energy))
    _spec_spline = interp1d(_ENERGY, _spec)
    return _spec_spline

where:

norm         = 1.5773076E-10 #/cm2/s/MeV
norm_keV     = norm / 1000 #/cm2/s/keV
pivot_energy = 1000

# Quiescent state
index1       = 2.27
index2       = 0.049

# Flaring state
index1_flare = 2.7
index2_flare = 0.049




