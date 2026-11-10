# Seyfert galaxy NGC 4151 — DC5

**DC5 status:** modified  
**Based on:** `DC4/sources/Extragalactic/NGC_4151`  

## Model

DC4 model (thermal cutoff power law Gamma=1.75, Ecut=200 keV + non-thermal Gamma=3.8 tail). DC5 increases the thermal (coronal) normalisation by 1.5, representing one of the brighter states of Lubinski et al. (2010); the non-thermal tail is unchanged. Spectrum: NGC4151_ec200_TH_and_NTH_bright_COSI.dat (thermal norm 0.2235, non-thermal norm 142.8 at 1 keV).

## Change relative to the DC4 mock dataset

thermal (Gamma=1.75, Ecut=200 keV) normalisation x1.5 (brighter state, Lubinski et al. 2010); non-thermal tail unchanged; flux 0.00188 -> 0.002726 ph/cm2/s

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Lubiński et al. 2010, MNRAS 408, 1851 (NGC 4151 spectral states)](https://ui.adsabs.harvard.edu/abs/2010MNRAS.408.1851L/abstract)
- [Inoue, Totani & Ueda 2008, ApJL 672, L5 (non-thermal AGN tail)](https://ui.adsabs.harvard.edu/abs/2008ApJ...672L...5I/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/NGC_4151`._
