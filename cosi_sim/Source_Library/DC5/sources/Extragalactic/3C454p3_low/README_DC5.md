# Blazar 3C 454.3, low state — DC5

**DC5 status:** reused (bug-fixed)  
**Based on:** `DC4/sources/Extragalactic/3C454p3_low`  

## Model

DC4 model: low-state spectrum of Bonnoli et al. (2011), unpolarised, on whenever the source is not flaring (65% of the 3 months; on/off light curve).

## Change relative to the DC4 mock dataset

same model; Flux keyword corrected to the time average over the light curve (the DC3/DC4 file gave the on-state flux, which MEGAlib would treat as the time average)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- 3C454p3_low: **fixed**, Flux 0.00029 -> 0.000188391 ph/cm2/s. Flux was the on-state flux; it is now that flux x the light-curve mean (0.6496). Basis: the spectrum file and README describe the low state (Bonnoli et al. 2011); on/off light curve, on 65.0% of the time.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Bonnoli et al. 2011, MNRAS 410, 368 (MeV blazar SED shapes)](https://ui.adsabs.harvard.edu/abs/2011MNRAS.410..368B/abstract)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/3C454p3_low`._
