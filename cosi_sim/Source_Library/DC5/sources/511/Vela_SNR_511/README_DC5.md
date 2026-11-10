# Vela SNR, 511 keV line — DC5

**DC5 status:** reused (bug-fixed)  
**Based on:** `DC3/sources/511/Vela_SNR_511`  

## Model

DC3 model: positrons from 1e-4 Msun of 44Ti trapped in the remnant, spatial template from the ROSAT all-sky X-ray emission (~8 deg). Same model as DC3/DC4.

## Change relative to the DC4 mock dataset

511 keV side nodes set to zero; integrated flux 7.031e-04 -> 3.515e-04 ph/cm2/s (README value 3.5e-4)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- DC3 Vela SNR 511 keV model (M. Leising), DC3/sources/511/Vela_SNR_511/Readme.txt

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/511/Vela_SNR_511`._
