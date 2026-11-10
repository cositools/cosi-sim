# Galactic diffuse 60Fe (NE2001 model) — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Fe60/60Fe_NE2001`  

## Model

DC3 NE2001-based 60Fe map scaled by 0.65 (total Galactic 60Fe mass 3.5 -> 2.3 Msun). The per-line 60Fe/26Al flux ratio becomes 0.12, between Martin et al. (2010, ~0.11) and Wang et al. (2020, 0.18 +- 0.04). The map is stored uncompressed (82 MB), like the DC3 original, so the pipeline can use it directly.

## Change relative to the DC4 mock dataset

map intensity x0.65 (60Fe mass 3.5 -> 2.3 Msun); total flux (both lines) 2.997e-04 -> 1.948e-04 ph/cm2/s

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Wang et al. 2020, ApJ 889, 169 (Galactic 60Fe)](https://ui.adsabs.harvard.edu/abs/2020ApJ...889..169W/abstract)
- [Martin et al. 2010, A&A 511, A86 (60Fe/26Al)](https://ui.adsabs.harvard.edu/abs/2010A%26A...511A..86M/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/60Fe_NE2001`._
