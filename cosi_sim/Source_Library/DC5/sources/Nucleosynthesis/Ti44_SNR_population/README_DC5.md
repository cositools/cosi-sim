# 44Ti SNR population — DC5

**DC5 status:** new (population synthesis, A. Anaya)
**Draw:** `map2.csv` of the 19 population-synthesis maps, with a random spectrum for each SNR (seed 3891814211; `DC5/DC5_ti44_draw.json`)

## Model

Young supernova remnants seen in the 44Ti 1157 keV line, from a population synthesis by A. Anaya. The map gives
the 5 known young SNRs (SN 1987A, Tycho, Kepler, Vela Jr, G1.9+0.3) at their real positions with population-synthesis
fluxes, plus 4 SNRs at random positions. Some may be below the detection threshold. Each SNR is a point
source with its own line profile (`Ti44_spectrum*.dat`, broadened and shifted by its ejecta velocities); Flux is the
line flux over the spectrum range (1110–1205 keV). Total: 0.000576 ph/cm²/s.

| Component | SNR | l (deg) | b (deg) | Flux (ph/cm²/s) | Spectrum | Centroid (keV) | Line extent (km/s) |
|---|---|---|---|---|---|---|---|
| `Ti44_SN1987A` | SN 1987A | 279.70 | -31.90 | 0.000246 | `Ti44_spectrum32.dat` | 1152.5 | -6294 to +6380 |
| `Ti44_Tycho` | Tycho | 120.10 | 1.40 | 5.78e-06 | `Ti44_spectrum17.dat` | 1155.9 | -7725 to +7904 |
| `Ti44_Kepler` | Kepler | 4.50 | 6.80 | 4.23e-06 | `Ti44_spectrum31.dat` | 1150.1 | -6317 to +6380 |
| `Ti44_VelaJr` | Vela Jr | 266.30 | -1.20 | 2.37e-06 | `Ti44_spectrum43.dat` | 1163.9 | -7654 to +7953 |
| `Ti44_G1p9p0p3` | G1.9+0.3 | 1.90 | 0.30 | 5e-06 | `Ti44_spectrum15.dat` | 1157.2 | -5281 to +5376 |
| `Ti44_popSNR1` | population-synthesis SNR 1 | 42.37 | -2.71 | 2.66e-06 | `Ti44_spectrum46.dat` | 1152.4 | -7748 to +7904 |
| `Ti44_popSNR2` | population-synthesis SNR 2 | 358.26 | 3.89 | 5.37e-05 | `Ti44_spectrum39.dat` | 1157.2 | -6270 to +6404 |
| `Ti44_popSNR3` | population-synthesis SNR 3 | 20.24 | -5.32 | 8.76e-05 | `Ti44_spectrum47.dat` | 1155.6 | -5281 to +5327 |
| `Ti44_popSNR4` | population-synthesis SNR 4 | 331.69 | 6.70 | 0.00017 | `Ti44_spectrum21.dat` | 1157.2 | -5281 to +5376 |

Cas A is not part of the map: DC5 reuses the DC4 Cas A model (`DC4/sources/Nucleosynthesis/CasAG16distribution`).

## Change relative to the DC4 mock dataset

New. It replaces the DC4 models of SN 1987A, Tycho, Kepler, Vela Jr and G1.9+0.3 (all below the detection threshold
in the DC4 analysis).

The template files and the script are in `DC5/scripts/ti44/`.

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/Ti44_SNR_population`._
