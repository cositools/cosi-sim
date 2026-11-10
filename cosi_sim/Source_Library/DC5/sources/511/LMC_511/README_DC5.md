# Large Magellanic Cloud, 511 keV line — DC5

**DC5 status:** modified  
**Based on:** `DC3/sources/511/LMC_Gaussian_511 (the DC4 LMC_511 definition is not in cosi-sim)`  

## Model

The DC4 LMC_511 simulation used a definition that is not in cosi-sim. DC5 replaces it with the alternative DC3 LMC_Gaussian_511 definition (Gaussian, sigma = 3.3 deg, line at 511.5 keV) with the flux doubled to 8.54e-6 ph/cm2/s, still well below the SPI 2-sigma upper limit of 3.6e-5.

## Change relative to the DC4 mock dataset

DC4 LMC_511 model replaced by the alternative DC3 LMC_Gaussian_511 definition, with flux x2 relative to DC3 (4.27e-06 -> 8.54e-06 ph/cm2/s; still below the SPI 2-sigma limit 3.6e-5, Siegert et al. 2016)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Siegert et al. 2016, A&A 595, A25 (511 keV from Milky Way satellites, LMC limit)](https://arxiv.org/abs/1608.00393)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/511/LMC_511`._
