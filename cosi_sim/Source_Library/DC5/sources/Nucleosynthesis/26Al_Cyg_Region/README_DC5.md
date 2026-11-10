# 26Al in the Cygnus region — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Al26/26Al_Cyg_Region`  

## Model

DC3 model (1808.8 keV line, 1.6 keV FWHM, 3.9e-5 ph/cm2/s at l=81, b=1) with a wider spatial distribution: Gaussian sigma 4.5 deg instead of 3.0 deg. Martin et al. (2009) note 3 deg is a lower limit with ~3 deg uncertainty.

## Change relative to the DC4 mock dataset

Gaussian width 3.0 -> 4.5 deg (Martin et al. 2009: 3 deg is a lower limit, +-3 deg uncertainty); flux unchanged

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Martin et al. 2009, A&A 506, 703 (26Al in Cygnus)](https://arxiv.org/abs/1001.1521)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/26Al_Cyg_Region`._
