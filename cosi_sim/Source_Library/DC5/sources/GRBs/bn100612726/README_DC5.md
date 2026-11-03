# bn100612726 — DC5

**DC5 status:** modified (time, spectral and polarization parameters)
**Based on:** `DC3/sources/GRBs/bn100612726` (included in the DC4 mock dataset)
**Position:** unchanged, l = 338.4179 deg, b = 46.6501 deg
**Duration (light-curve span):** 10.76 s

## Changes relative to the DC4 mock dataset

| Parameter | DC4 | DC5 |
|---|---|---|
| Trigger time (unix s) | 1839617230.000 | 1835761370.066 |
| Day of the observation | 48.80 | 4.17 |
| Off-axis angle at trigger (deg) | 23.5 | 39.3 (end of burst: 38.5) |
| Zenith angle at trigger (deg) | 22.8 | 39.9 |
| Spectral model | PowerLaw | PowerLaw (unchanged) |
| Power-law index | 2.491 | 2.9000 |
| Photon flux 100 keV-10 MeV (ph/cm2/s) | 1.02358 | 1.02358 (unchanged) |
| Polarization fraction | 0.20 | 0.78 |
| Polarization angle (deg, galactic) | 35.0 | 145.0 |

The light curve is the DC3 light curve, unchanged in shape, with every time stamp shifted by -3855859.934 s.

## How the DC5 values were chosen

- **Time:** all DC5 GRBs fall in days 4-7 of the observation (3-7 days after the start of the DC4 orientation file), so they overlap the week of background simulations with ACS data and come after the activation build-up. The time was drawn so that the off-axis angle (angle between the COSI z-axis and the source) reproduces the DC4 GRB off-axis distribution (target 39.4 deg: a DC4 value jittered by up to +-3 deg and randomly reassigned). Required: off-axis angle <= 60 deg during the whole burst, zenith angle <= 100 deg (well above the ~113 deg Earth-occultation limit), livetime > 0 (no SAA) from 5 min before to 5 min after the burst, an off-axis change < 3 deg during the burst (no slew), and >= 1 h separation from any other DC5 GRB.
- **Spectrum:** same spectral model as DC4; parameters drawn from the Fermi GBM 10-year catalog fluence-spectrum distributions (long GRBs): alpha and log10(Epeak) Gaussian around the catalog medians (long: alpha = -0.84, Epeak = 144 keV; short: alpha = -0.46, Epeak = 413 keV), beta Gaussian around -2.3 (sigma 0.3), with cuts to keep alpha > beta and Epeak in a range COSI can constrain. For power-law bursts the index follows the high-energy (beta) distribution, since COSI only sees the spectrum above 100 keV. The photon flux in 100 keV-10 MeV is unchanged.
- **Polarization:** the DC4 GRB polarization fractions are spread uniformly between 0 and 0.9; DC5 fractions are drawn from the same distribution (stratified uniform on [0, 0.9]). The angle is uniform in [0, 180) deg.

## References

- [Poolakkil et al. 2021, ApJ 913, 60 — Fermi GBM GRB spectral catalog, 10 years](https://arxiv.org/abs/2103.13528) (Band and power-law parameter distributions)
- [Gruber et al. 2014, ApJS 211, 12 — Fermi GBM GRB spectral catalog, 4 years](https://arxiv.org/abs/1401.5069)
- [Kole et al. 2020, A&A 644, A124 — POLAR GRB polarization catalog](https://arxiv.org/abs/2009.04871) (time-integrated polarization is low to moderate)
- [Fermi GBM burst catalog (HEASARC FERMIGBRST)](https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html) (original burst `bn100612726`)

_Select it in inputs.yaml as `DC5/sources/GRBs/bn100612726`._
