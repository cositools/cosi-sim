# FSRQ 4C +21.35 — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Extragalactic/4C21p35_noflare`  

## Model

DC3 two-state model (quiescent index 1.6, flaring index 2.5, flare light curve from Fermi-LAT). Both states scaled by 1.5 in DC5 (a brighter activity epoch).

## Change relative to the DC4 mock dataset

- 4C21p35_noflare: flux 0.0005535 -> 0.0008302 ph/cm2/s (x1.5)
- 4C21p35_flare: flux 0.01729 -> 0.02594 ph/cm2/s (x1.5)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- 4C21p35_noflare: **to be checked**, not changed. Unclear: the light curve varies within the quiescent state (on 77.3% of the time) and the README does not say whether Flux (the integral of the 4FGL-DR3 extrapolation, 5.5e-4 in DC4) is the 3-month average or the average while quiescent. If the latter, Flux should be 0.00083025 x 0.7726 = 6.41e-4. Not changed.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- DC3 4C 21.35 model, DC3/sources/Extragalactic/4C21p35_flare/README.txt (Fermi-LAT log-parabola extrapolation)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/4C21p35_noflare`._
