# Upper Scorpius, 26Al and 60Fe — DC5

**DC5 status:** modified  
**Based on:** `DC4/sources/Nucleosynthesis/USco`  

## Model

DC4 extended (9 deg) 26Al and 60Fe model. DC5 halves both 60Fe lines (2.25e-5 ph/cm2/s each), giving a per-line 60Fe/26Al ratio of 0.375 instead of 0.75; still enhanced relative to the Galactic average, as expected for a ~10 Myr old association.

## Change relative to the DC4 mock dataset

60Fe line fluxes 4.5e-05 -> 2.25e-05 ph/cm2/s each (x0.5; 60Fe/26Al per line 0.75 -> 0.375); 26Al unchanged

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Diehl et al. 2010, A&A 522, A51 (26Al in Sco-Cen)](https://ui.adsabs.harvard.edu/abs/2010A%26A...522A..51D/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/USco`._
