# Generic magnetar (fictitious, DC4) — DC5

**DC5 status:** modified  
**Based on:** `DC4/sources/Galactic/magnetar2`  

## Model

DC4 generic magnetar (log-parabola, 40% polarisation, 5.5 s pulsation light curve). DC5 flux scaled by 1.5 (4.95e-4 ph/cm2/s).

## Change relative to the DC4 mock dataset

flux 0.00033 -> 0.000495 ph/cm2/s (x1.5); light curve trimmed to 109913 whole pulse periods so that the periodic repeat keeps the pulse phase continuous (DC4 period bug fix)

## Light-curve flux

MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux keyword must be the time-averaged flux over that range.

- magnetar2: correct, not changed (phase-integrated flux; the light curve 1 + 0.5 sin(2 pi t/P) has mean 1).

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [den Hartog, Kuiper & Hermsen 2008, A&A 489, 263 (1RXS J1708-40)](https://www.arxiv.org/abs/0804.1641)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/magnetar2`._
