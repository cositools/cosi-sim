# FSRQ 4C +21.35 — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Extragalactic/4C21p35_noflare`  

## Model

DC3 two-state model (quiescent index 1.6, flaring index 2.5, flare light curve from Fermi-LAT). Both states scaled by 1.5 in DC5 (a brighter activity epoch).

## Change relative to the DC4 mock dataset

- 4C21p35_noflare: flux 0.0005535 -> 0.0008302 ph/cm2/s (x1.5)
- 4C21p35_flare: flux 0.01729 -> 0.02594 ph/cm2/s (x1.5)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- DC3 4C 21.35 model, DC3/sources/Extragalactic/4C21p35_flare/README.txt (Fermi-LAT log-parabola extrapolation)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/4C21p35_noflare`._
