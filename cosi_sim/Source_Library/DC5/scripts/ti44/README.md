# 44Ti SNR population for DC5

Template files from A. Anaya's population synthesis of young supernova remnants seen in the 44Ti 1157 keV line, and the script that turns one draw into the DC5 source `DC5/sources/Nucleosynthesis/Ti44_SNR_population`.

## Files

- `popsyn/spatial/map1.csv` … `map19.csv`: one population each, with columns `l, b, flux` (Galactic degrees; flux in ph/cm²/s over 1110–1205 keV).
  - The first 5 rows are the known young SNRs at their real positions (SN 1987A, Tycho, Kepler, Vela Jr, G1.9+0.3), with population-synthesis fluxes.
  - The other 3–4 rows are SNRs at random positions.
  - Fluxes range from 1e-6 to 3.1e-4 ph/cm²/s; some sources may be below the detection threshold.
- `popsyn/spectra/spectrum1.dat` … `spectrum48.dat`: 1157 keV line profiles (MEGAlib `File` spectra, 1111.6–1204.3 keV). The normalisation is arbitrary, since the flux comes from the map.
- `popsyn/template.source`: the instructions that came with the files: pick one map at random, and give each SNR a random spectrum.
- `build_ti44_population.py`: does that draw and writes the DC5 source.
  - It writes one component per SNR (`Ti44_<name>` for the known SNRs, `Ti44_popSNR<n>` for the others), the spectra used (`Ti44_spectrum<i>.dat`) and `README_DC5.md`.
  - It also writes `DC5/DC5_ti44_draw.json` and the `DC5_build_log.json` entry.

Cas A is not in the maps. DC5 reuses the DC4 Cas A model (`DC4/sources/Nucleosynthesis/CasAG16distribution`). The DC4 models of the other known SNRs are not used, because they were all below the detection threshold in the DC4 analysis.

## Usage

From the repository root, after `build_dc5.py` (same seed):

```bash
python3 cosi_sim/Source_Library/DC5/scripts/ti44/build_ti44_population.py . 3891814211
```

The same seed gives the same map and spectra.
