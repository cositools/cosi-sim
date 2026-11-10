# Fictitious ONe nova, 22Na line (new in DC5) — DC5

**DC5 status:** new (arbitrary)  
**Position:** l = 71.159 deg, b = 4.096 deg  

## Model

Arbitrary source: an ONe nova at 1.5 kpc that erupted shortly before the observation. 22Na 1274.5 keV line with ~20 keV FWHM (sigma 8.5 keV); flux ~1e-5 ph/cm2/s at 1 kpc (Hernanz 2014) scaled to 4.4e-6. Steady, since the 22Na lifetime (3.75 yr) is much longer than 3 months. Position drawn at random.

## Change relative to the DC4 mock dataset

ONe nova at 1.5 kpc: 22Na 1275 keV line (~20 keV FWHM), ~1e-5 ph/cm2/s at 1 kpc (Hernanz 2014) scaled to 1.5 kpc; constant (22Na lifetime 3.75 yr)

Any other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.

## References

- [Hernanz 2014, ASPC 490, 319 (gamma-rays from classical novae)](https://arxiv.org/abs/1305.0769)

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/nova_one_22Na`._
