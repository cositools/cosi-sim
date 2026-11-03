# bn161004964 — DC5

**DC5 status:** modified (time, spectral and polarization parameters)
**Based on:** `DC3/sources/GRBs/bn161004964` (included in the DC4 mock dataset)
**Position:** unchanged, l = 190.8472 deg, b = -48.9008 deg
**Duration (light-curve span):** 18.95 s

## Changes relative to the DC4 mock dataset

| Parameter | DC4 | DC5 |
|---|---|---|
| Trigger time (unix s) | 1842948485.000 | 1835954669.991 |
| Day of the observation | 87.36 | 6.41 |
| Off-axis angle at trigger (deg) | 15.0 | 58.5 (end of burst: 56.9) |
| Zenith angle at trigger (deg) | 7.5 | 59.2 |
| Spectral model | Band | Band (unchanged) |
| Band alpha | -0.811 | -0.8342 |
| Band beta | -2.392 | -2.2766 |
| Epeak (keV) | 114.0 | 72.0 |
| Photon flux 100 keV-10 MeV (ph/cm2/s) | 0.856912 | 0.856912 (unchanged) |
| Polarization fraction | 0.60 | 0.18 |
| Polarization angle (deg, galactic) | 10.0 | 76.4 |

The light curve is the DC3 light curve, unchanged in shape, with every time stamp shifted by -6993815.009 s.

## How the DC5 values were chosen

- **Time:** all DC5 GRBs fall in days 4-7 of the observation (3-7 days after the start of the DC4 orientation file), so they overlap the week of background simulations with ACS data and come after the activation build-up. The time was drawn so that the off-axis angle (angle between the COSI z-axis and the source) reproduces the DC4 GRB off-axis distribution (target 58.1 deg: a DC4 value jittered by up to +-3 deg and randomly reassigned). Required: off-axis angle <= 60 deg during the whole burst, zenith angle <= 100 deg (well above the ~113 deg Earth-occultation limit), livetime > 0 (no SAA) from 5 min before to 5 min after the burst, an off-axis change < 3 deg during the burst (no slew), and >= 1 h separation from any other DC5 GRB.
- **Spectrum:** same spectral model as DC4; parameters drawn from the Fermi GBM 10-year catalog fluence-spectrum distributions (long GRBs): alpha and log10(Epeak) Gaussian around the catalog medians (long: alpha = -0.84, Epeak = 144 keV; short: alpha = -0.46, Epeak = 413 keV), beta Gaussian around -2.3 (sigma 0.3), with cuts to keep alpha > beta and Epeak in a range COSI can constrain. For power-law bursts the index follows the high-energy (beta) distribution, since COSI only sees the spectrum above 100 keV. The photon flux in 100 keV-10 MeV is unchanged.
- **Polarization:** the DC4 GRB polarization fractions are spread uniformly between 0 and 0.9; DC5 fractions are drawn from the same distribution (stratified uniform on [0, 0.9]). The angle is uniform in [0, 180) deg.

## References

- [Poolakkil et al. 2021, ApJ 913, 60 — Fermi GBM GRB spectral catalog, 10 years](https://arxiv.org/abs/2103.13528) (Band and power-law parameter distributions)
- [Gruber et al. 2014, ApJS 211, 12 — Fermi GBM GRB spectral catalog, 4 years](https://arxiv.org/abs/1401.5069)
- [Kole et al. 2020, A&A 644, A124 — POLAR GRB polarization catalog](https://arxiv.org/abs/2009.04871) (time-integrated polarization is low to moderate)
- [Fermi GBM burst catalog (HEASARC FERMIGBRST)](https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html) (original burst `bn161004964`)

_Select it in inputs.yaml as `DC5/sources/GRBs/bn161004964`._
