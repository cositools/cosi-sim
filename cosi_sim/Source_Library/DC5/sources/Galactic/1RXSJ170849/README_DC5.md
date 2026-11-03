# Magnetar 1RXS J170849.0-400910 — DC5

**DC5 status:** modified  
**Based on:** `DC4/sources/Galactic/1RXSJ170849`  

## Model

DC4 log-parabola spectrum, 80% polarisation and 11 s pulsation light curve. DC5 flux scaled by 0.75 (2.48e-4 ph/cm2/s), motivated by the reported long-term hard X-ray variability.

## Change relative to the DC4 mock dataset

flux 0.00033 -> 0.000247 ph/cm2/s (x0.75, long-term hard X-ray variability, den Hartog et al. 2008); light curve trimmed to 235528 whole pulse periods so that the periodic repeat keeps the pulse phase continuous (DC4 period bug fix)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [den Hartog, Kuiper & Hermsen 2008, A&A 489, 263 (1RXS J1708-40)](https://www.arxiv.org/abs/0804.1641)
- [Götz et al. 2007, A&A 475, 317 (long-term hard X-ray variability of 1RXS J1708-40)](https://arxiv.org/abs/0709.3712)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Galactic/1RXSJ170849`._
