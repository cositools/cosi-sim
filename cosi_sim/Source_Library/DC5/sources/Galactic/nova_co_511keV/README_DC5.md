# Classical CO nova — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Galactic/nova_co_continuum`  

## Model

DC3 CO-nova model (continuum, 511 keV line, 478 keV 7Be line with their light curves) at the position of V1369 Cen. DC5 places the nova at 0.82 kpc instead of 1 kpc, so all three components are 1.5x brighter.

## Change relative to the DC4 mock dataset

- nova_co_continuum: flux 0.1221 -> 0.1831 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc)
- nova_co_511keV: flux 0.01537 -> 0.02305 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc)
- nova_co_478keV: flux 2.044e-06 -> 3.066e-06 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- nova_co_511keV: **fixed**, Flux 0.023055 -> 4.27646e-06 ph/cm2/s. Flux was the peak flux; it is now that flux x the light-curve mean (0.0001855). Basis: Gomez-Gomar et al. 1998 (MNRAS 296, 913): CO nova at 1 kpc, peak continuum (170-470 keV) ~0.17, peak 511 keV line ~1e-2, late 478 keV maximum 1.4-2.6e-6 ph/cm2/s.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Hernanz 2014, ASPC 490, 319 (gamma-rays from classical novae)](https://arxiv.org/abs/1305.0769)
- [Gómez-Gomar et al. 1998, MNRAS 296, 913 (gamma-ray emission of individual classical novae)](https://arxiv.org/abs/astro-ph/9711322)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/nova_co_511keV`._
