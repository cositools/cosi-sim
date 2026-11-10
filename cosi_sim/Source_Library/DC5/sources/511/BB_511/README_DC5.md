# Broad Galactic bulge, 511 keV line — DC5

**DC5 status:** modified (+bug-fixed)  
**Based on:** `DC3/sources/511/BB_511`  

## Model

DC3 broad-bulge 511 keV intensity map (1 deg grid), intensity scaled by 0.85 in DC5. The resulting bulge total (narrow + broad + central source) is 9.9e-4 ph/cm2/s, within 1 sigma of the SPI bulge flux of Siegert et al. (2016).

## Change relative to the DC4 mock dataset

511 keV side nodes set to zero (bug fix) and broad-bulge intensity scaled x0.85; integrated flux 1.480e-03 -> 6.290e-04 ph/cm2/s

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Siegert et al. 2016, A&A 586, A84 (SPI 511 keV all-sky)](https://ui.adsabs.harvard.edu/abs/2016A%26A...586A..84S/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/511/BB_511`._
