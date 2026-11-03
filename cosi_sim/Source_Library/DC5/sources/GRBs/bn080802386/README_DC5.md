# bn080802386 — DC5

**DC5 status:** modified (time, spectral and polarization parameters)
**Based on:** `DC3/sources/GRBs/bn080802386` (included in the DC4 mock dataset)
**Position:** unchanged, l = 23.5300 deg, b = -53.4400 deg
**Duration (light-curve span):** 0.54 s

## Changes relative to the DC4 mock dataset

| Parameter | DC4 | DC5 |
|---|---|---|
| Trigger time (unix s) | 1835493492.227 | 1835935843.422 |
| Day of the observation | 1.07 | 6.19 |
| Off-axis angle at trigger (deg) | 20.6 | 6.1 (end of burst: 6.1) |
| Zenith angle at trigger (deg) | 34.2 | 27.2 |
| Spectral model | Band | Band (unchanged) |
| Band alpha | -0.737 | -0.9204 |
| Band beta | -2.095 | -2.4112 |
| Epeak (keV) | 622.4 | 634.8 |
| Photon flux 100 keV-10 MeV (ph/cm2/s) | 150 | 150 (unchanged) |
| Polarization fraction | 0.80 | 0.16 |
| Polarization angle (deg, galactic) | 90.0 | 169.4 |

The light curve is the DC3 light curve, unchanged in shape, with every time stamp shifted by +442351.195 s.

## How the DC5 values were chosen

- **Time:** all DC5 GRBs fall in days 4-7 of the observation (3-7 days after the start of the DC4 orientation file), so they overlap the week of background simulations with ACS data and come after the activation build-up. The time was drawn so that the off-axis angle (angle between the COSI z-axis and the source) reproduces the DC4 GRB off-axis distribution (target 5.7 deg: a DC4 value jittered by up to +-3 deg and randomly reassigned). Required: off-axis angle <= 60 deg during the whole burst, zenith angle <= 100 deg (well above the ~113 deg Earth-occultation limit), livetime > 0 (no SAA) from 5 min before to 5 min after the burst, an off-axis change < 3 deg during the burst (no slew), and >= 1 h separation from any other DC5 GRB.
- **Spectrum:** same spectral model as DC4; parameters drawn from the Fermi GBM 10-year catalog fluence-spectrum distributions (short GRBs): alpha and log10(Epeak) Gaussian around the catalog medians (long: alpha = -0.84, Epeak = 144 keV; short: alpha = -0.46, Epeak = 413 keV), beta Gaussian around -2.3 (sigma 0.3), with cuts to keep alpha > beta and Epeak in a range COSI can constrain. For power-law bursts the index follows the high-energy (beta) distribution, since COSI only sees the spectrum above 100 keV. The photon flux in 100 keV-10 MeV is unchanged.
- **Polarization:** the DC4 GRB polarization fractions are spread uniformly between 0 and 0.9; DC5 fractions are drawn from the same distribution (stratified uniform on [0, 0.9]). The angle is uniform in [0, 180) deg.

## References

- [Poolakkil et al. 2021, ApJ 913, 60 — Fermi GBM GRB spectral catalog, 10 years](https://arxiv.org/abs/2103.13528) (Band and power-law parameter distributions)
- [Gruber et al. 2014, ApJS 211, 12 — Fermi GBM GRB spectral catalog, 4 years](https://arxiv.org/abs/1401.5069)
- [Kole et al. 2020, A&A 644, A124 — POLAR GRB polarization catalog](https://arxiv.org/abs/2009.04871) (time-integrated polarization is low to moderate)
- [Fermi GBM burst catalog (HEASARC FERMIGBRST)](https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html) (original burst `bn080802386`)

_Select it in inputs.yaml as `DC5/sources/GRBs/bn080802386`._
