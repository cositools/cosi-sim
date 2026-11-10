# Seyfert 2 galaxy NGC 4945 (new in DC5) — DC5

**DC5 status:** new (literature)  
**Position:** l = 305.2721 deg, b = 13.3397 deg  

## Model

Cutoff power law, Gamma = 1.9, Ecut = 300 keV (NuSTAR lower limits 200-300 keV), normalised to F(20-100 keV) = 2.0e-10 erg/cm2/s. Absorption is negligible above 100 keV. Flux 4.6e-4 ph/cm2/s (0.1-10 MeV), <1% of the Crab.

## Change relative to the DC4 mock dataset

cutoff power law Gamma=1.9, Ecut=300 keV (NuSTAR: Ecut > 200-300 keV, Puccetti et al. 2014); F(20-100 keV)=2.0e-10 erg/cm2/s

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Puccetti et al. 2014, ApJ 793, 26 (NuSTAR NGC 4945)](https://www.arxiv.org/abs/1407.3974)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Extragalactic/NGC_4945`._
