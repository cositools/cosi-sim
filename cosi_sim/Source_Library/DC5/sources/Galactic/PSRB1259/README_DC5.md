# Gamma-ray binary PSR B1259-63, periastron flare — DC5

**DC5 status:** reused (bug-fixed)  
**Based on:** `DC3/sources/Galactic/PSRB1259`  

## Model

DC3/DC4 model: 30 days of constant emission (T > 1839487305.0) at the nominal Fermi-LAT flux of Abdo et al. (2011), 6.13e-4 ph/cm2/s in 0.1-10 MeV.

## Change relative to the DC4 mock dataset

same model; Flux keyword corrected to the time average over the light curve (the DC3/DC4 file gave the on-state flux, which MEGAlib would treat as the time average)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- PSRB1259: **fixed**, Flux 0.00061253 -> 0.000198826 ph/cm2/s. Flux was the on-state flux; it is now that flux x the light-curve mean (0.3246). Basis: README and DC4 docs: 30-day constant emission at the nominal Abdo et al. (2011) flux of 6.13e-4 ph/cm2/s; on/off light curve, on 32.5% of the time.

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Abdo et al. 2011, ApJL 736, L11 (Fermi-LAT PSR B1259-63 periastron flare)](https://doi.org/10.1088/2041-8205/736/1/L11)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/PSRB1259`._
