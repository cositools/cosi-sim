# Classical CO nova — DC5

**DC5 status:** reused (bug-fixed)  
**Based on:** `DC3/sources/Galactic/nova_co_continuum`  

## Model

DC3 CO-nova model (continuum, 511 keV line, 478 keV 7Be line with their light curves) at the position of V1369 Cen, at 1 kpc. DC5 keeps this model, with the Flux keywords set to the time averages of the Hernanz (2014) model, which should be the correct model.

## Change relative to the DC4 mock dataset

- nova_co_continuum: same model as DC4 (Hernanz 2014 CO nova at 1 kpc); Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model (the DC3/DC4 file gave the peak flux). The earlier DC5 x1.5 modification (0.82 kpc) is dropped
- nova_co_511keV: same model as DC4 (Hernanz 2014 CO nova at 1 kpc); Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model (the DC3/DC4 file gave the peak flux). The earlier DC5 x1.5 modification (0.82 kpc) is dropped
- nova_co_478keV: same model as DC4 (Hernanz 2014 CO nova at 1 kpc); Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model (the DC3/DC4 file gave the peak flux). The earlier DC5 x1.5 modification (0.82 kpc) is dropped

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- nova_co_cont: **fixed**, Flux 0.122071 -> 2.12e-05 ph/cm2/s. Flux set to the time average of the Hernanz (2014) CO nova model at 1 kpc, which should be the correct model (Hernanz 2014). The DC3/DC4 file gave the peak flux (0.122071), and the earlier DC5 x1.5 modification is dropped.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Hernanz 2014, ASPC 490, 319 (gamma-rays from classical novae)](https://arxiv.org/abs/1305.0769)
- [Gómez-Gomar et al. 1998, MNRAS 296, 913 (gamma-ray emission of individual classical novae)](https://arxiv.org/abs/astro-ph/9711322)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/nova_co_continuum`._
