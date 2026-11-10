# Positron in-flight annihilation (Galactic bulge, MeV continuum) — DC5

**DC5 status:** modified (+bug-fixed)  
**Based on:** `DC4/sources/511/Positrons_In_Flight_Annihilation`  

## Model

2D Gaussian (sigma = 3.3 deg, i.e. FWHM 7.8 deg) at (l, b) = (-1.4, -0.2) deg with the DC4 best-fit spectrum. DC5 flux is 1.2x the DC4 value (3.72e-4 vs 3.1e-4 ph/cm2/s in 0.1-10 MeV), within the ~17% (1 sigma) flux uncertainty of Knödlseder et al. (2025).

## Change relative to the DC4 mock dataset

Orientation 'Galactic Fixed -1.4 -0.2' -> 'Galactic Fixed -0.2 -1.4' (bug fix: MEGAlib order is b, l); flux 0.00031 -> 0.000372 ph/cm2/s (x1.2)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Knödlseder et al. 2025, A&A 700, A257 (positron in-flight annihilation, COMPTEL)](https://arxiv.org/abs/2506.17427)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/511/Positrons_In_Flight_Annihilation`._
