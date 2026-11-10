# M31, 511 keV line — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/511/M31_Gaussian_511 (the DC4 M31_511 definition is not in cosi-sim)`  

## Model

The DC4 M31_511 simulation used a definition that is not in cosi-sim. DC5 replaces it with the alternative DC3 M31_Gaussian_511 definition, with a more compact emission region (sigma 0.5 deg instead of 1.0 deg), i.e. annihilation concentrated toward the bulge; DC3 flux 2.13e-7 ph/cm2/s.

## Change relative to the DC4 mock dataset

DC4 M31_511 model replaced by the alternative DC3 M31_Gaussian_511 definition, with the Gaussian width reduced 1.0 -> 0.5 deg (emission concentrated in the M31 bulge); DC3 flux 2.13e-7 ph/cm2/s

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Siegert et al. 2016, A&A 595, A25 (511 keV from Milky Way satellites, LMC limit)](https://arxiv.org/abs/1608.00393)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/511/M31_511`._
