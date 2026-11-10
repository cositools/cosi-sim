# Tycho SNR, 44Ti — DC5

**DC5 status:** modified  
**Based on:** `DC4/sources/Nucleosynthesis/Tycho`  

## Model

Point-like 44Ti line (1157 keV, 4000 km/s broadening). DC5 flux 1.0e-5 ph/cm2/s, equal to the NuSTAR upper limit, instead of 1.6x the limit in DC4.

## Change relative to the DC4 mock dataset

flux 1.6e-05 -> 1e-05 ph/cm2/s (1.0x instead of 1.6x the Lopez et al. 2015 upper limit)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Lopez et al. 2015, ApJ 814, 132 (NuSTAR 44Ti limits, Tycho)](https://ui.adsabs.harvard.edu/abs/2015ApJ...814..132L/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/Tycho`._
