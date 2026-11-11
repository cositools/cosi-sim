# Blazar 3C 454.3, flare — DC5

**DC5 status:** reused (bug-fixed)  
**Based on:** `DC4/sources/Extragalactic/3C454p3_high`  

## Model

DC4 model: flare spectrum (03/12 model of Bonnoli et al. 2011), 50% polarisation at 45 deg, on during the flare (35% of the 3 months; on/off light curve).

## Change relative to the DC4 mock dataset

same model; Flux keyword corrected to the time average over the light curve (the DC3/DC4 file gave the on-state flux, which MEGAlib would treat as the time average)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- 3C454p3_high: **fixed**, Flux 0.00624 -> 0.00218631 ph/cm2/s. Flux was the on-state flux; it is now that flux x the light-curve mean (0.3504). Basis: the spectrum file and README describe the flare (03/12 model of Bonnoli et al. 2011); on/off light curve, on 35.0% of the time.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Bonnoli et al. 2011, MNRAS 410, 368 (MeV blazar SED shapes)](https://ui.adsabs.harvard.edu/abs/2011MNRAS.410..368B/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/3C454p3_high`._
