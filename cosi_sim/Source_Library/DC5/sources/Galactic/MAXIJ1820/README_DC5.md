# MAXI J1820+070 (hard-state outburst) — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/Galactic/MAXIJ1820`  

## Model

DC3 two-component spectral/polarisation model with the 60-day ON light curve. Both components scaled by 0.7 (a fainter hard-state outburst than the exceptional 2018 one).

## Change relative to the DC4 mock dataset

MAXIJ1820_0p1-0p4: 0.1382 -> 0.09675; MAXIJ1820_0p4-10: 0.005964 -> 0.004174 ph/cm2/s (x0.7, fainter hard-state outburst)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- MAXIJ1820_0p1-0p4: **fixed**, Flux 0.0967469 -> 0.0628494 ph/cm2/s. Flux was the on-state flux; it is now that flux x the light-curve mean (0.6496). Basis: hard-state spectra (Cangemi et al. 2023) with the source 'on' for 60 days (README, DC4 docs); on/off light curve, on 65.0% of the time.
- MAXIJ1820_0p4-10: **fixed**, Flux 0.00417446 -> 0.00271184 ph/cm2/s. Flux was the on-state flux; it is now that flux x the light-curve mean (0.6496). Basis: hard-state spectra (Cangemi et al. 2023) with the source 'on' for 60 days (README, DC4 docs); on/off light curve, on 65.0% of the time.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Cangemi et al. 2023, A&A 669, A65 (MAXI J1820+070, MAXI J1348-630)](https://ui.adsabs.harvard.edu/abs/2023A%26A...669A..65C/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/MAXIJ1820`._
