# DC5 mock dataset — source definitions

> **Blind dataset.** This directory is the answer key for the DC5 mock dataset. It should not be shared with the COSI team or the community until the data challenge is unblinded.

The DC5 mock dataset starts from the DC4 mock dataset (3 months, same orbit, orientation and backgrounds) and changes the source content:

| | DC4 components | Fraction |
|---|---|---|
| Reused (same source files; 2 of these carry only the 511 keV bug fix) | 27 | 51% |
| Modified | 21 | 40% |
| Removed | 5 | 9% |
| **New** (relative to the ~71 DC4 components) | 18 | 25% |
| GRBs (`GRB_bn*`): new time, spectrum and polarization | 11 | all |
| Magnetar bursts (`MGF*`, `MgtBurst*`): unchanged, half kept | 4 kept, 3 removed | |

Percentages refer to the non-GRB DC4 components. DC5 therefore has 66 non-GRB components, 11 GRBs and 4 magnetar bursts.

**How the split was made.** Components that belong to one physical source (e.g. line + continuum maps, flare + quiescent states, the three nova components) were grouped, and the groups were shuffled with a random seed (3891814211, recorded in `DC5_draw.json`). Groups were assigned to *removed* (≈10% of files, only from sources that are not well-known detections: the Crab, Cyg X-1/X-3, Cen A, NGC 4151, the 511 keV bulge/disk, Galactic 26Al/60Fe, Cas A, etc. were protected), then *modified* (≈40%), with the rest *reused*. The modification applied to each drawn source was then chosen by hand from the literature (alternative library model where one exists, otherwise a simple flux/width/state change within the published range). Positions of the arbitrary new sources are drawn from the same seed. The GRB draw uses its own seed (3662968627, `DC5_grb_draw.json`). Running `scripts/draw_dc5.py` or `scripts/draw_dc5_grbs.py` without a seed gives a different realisation.

Files:
- `DC5_mock_dataset_src_list.txt` — the `src_list` for cosi-sim (80 entries; checked with `Setup.setup_srcs()`).
- `DC5_mock_dataset_manifest.md` — every component with its status, source path and what to do (simulate / re-simulate / reuse the existing DC3/DC4 event file).
- `DC5_build_log.json`, `DC5_draw.json`, `DC5_grb_draw.json` — machine-readable record of the draws and of every change.
- `scripts/` — `draw_dc5.py` (random split), `build_dc5.py` (writes the non-GRB `sources/` for this draw), `fix_magnetar_lightcurves.py` (period bug fix), `draw_dc5_grbs.py` + `build_dc5_grbs.py` (GRBs), `make_sim_time_inputs.py` (time-shifted MEGAlib inputs for GRBs and magnetar bursts), `ori_tools.py` (orientation-file geometry), `mapflux.py` (integrates cosima 3D maps), `eq2gal.py` (RA/Dec → l, b), `write_manifest.py` (src_list, manifest and `manifest_rows.json`), `write_readmes.py` (per-source `README_DC5.md` for non-GRB sources), `write_dc5_readme.py` (this file), `dm/` (dark matter map and significance estimate). Order: draw_dc5 → build_dc5 → fix_magnetar_lightcurves → `python -m cosi_sim.pipeline.time_reference --ori <9-column ori> DC5/sources/Galactic/{1RXSJ170849,magnetar2,PSRB1509}` (repeating light curves in t − t_ref) → draw_dc5_grbs → build_dc5_grbs → make_sim_time_inputs → dm/run_dm_choice → dm/build_dc5_dm → write_manifest → write_readmes → write_dc5_readme.
- `sources/` — one directory per modified, bug-fixed or new source, each with a `README_DC5.md` describing the model, the change, and references.

## Reused sources (same source files)
| DC4 mock component | cosi-sim source path | Action |
|---|---|---|
| CasAG16distribution | `DC4/sources/Nucleosynthesis/CasAG16distribution` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/CasAG16distribution_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Positrons_Central_Source | `DC4/sources/511/Positrons_Central_Source` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/Positrons_Central_Source_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| positrons_thin_disk_cont | `DC4/sources/511/Positrons_Thin_Disk_cont` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/positrons_thin_disk_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| positrons_thin_disk_line | `DC4/sources/511/Positrons_Thin_Disk_line` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/positrons_thin_disk_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| SN1987A | `DC4/sources/Nucleosynthesis/SN1987A` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/SN1987A_unbinned_data_filtered_with_SAAcut.fits.gz |
| VelaJr_44Ti | `DC4/sources/Nucleosynthesis/VelaJr_44Ti` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/VelaJr_44Ti_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Virgo_511 | `(no library file)` | reuse DC4 event file COSI-SMEX/DC4/Data/Sources/Virgo_511_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| NGC_1068 | `DC4/sources/Extragalactic/NGC_1068` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/NGC_1068_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| 4C71p07 | `DC4/sources/Extragalactic/4C71p07` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/4C71p07_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| 3C454p3_low | `DC4/sources/Extragalactic/3C454p3_low` | re-simulate with the same source file (time-chunk light-curve bug) |
| 3C454p3_high | `DC4/sources/Extragalactic/3C454p3_high` | re-simulate with the same source file (time-chunk light-curve bug) |
| CenA | `DC4/sources/Extragalactic/CenA` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/CenA_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Crab_DC4 | `DC4/sources/Galactic/Crab` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/Crab_DC4_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Globular_Cluster_Tuc_47 | `DC3/sources/511/Globular_Cluster_Tuc_47` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_Tuc_47_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Globular_Cluster_Omega_Cen | `DC3/sources/511/Globular_Cluster_Omega_Cen` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_Omega_Cen_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Globular_Cluster_NGC_6397 | `DC3/sources/511/Globular_Cluster_NGC_6397` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_NGC_6397_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Globular_Cluster_NGC_6121 | `DC3/sources/511/Globular_Cluster_NGC_6121` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_NGC_6121_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Positrons_from_26Al_line | `DC3/sources/511/Positrons_from_26Al_line` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_26Al_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Positrons_from_26Al_cont | `DC3/sources/511/Positrons_from_26Al_cont` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_26Al_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Positrons_from_44Ti_line | `DC3/sources/511/Positrons_from_44Ti_line` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_44Ti_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Positrons_from_44Ti_cont | `DC3/sources/511/Positrons_from_44Ti_cont` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_44Ti_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| PSRB1259 | `DC3/sources/Galactic/PSRB1259` | re-simulate with the same source file (time-chunk light-curve bug) |
| LS5039 | `DC3/sources/Galactic/LS5039` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/LS5039_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| 26Al_NE2001 | `DC3/sources/Al26/26Al_NE2001` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/26Al_NE2001_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| 60Fe_Cyg_Region | `DC3/sources/Fe60/60Fe_Cyg_Region` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/60Fe_Cyg_Region_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| Narrow_Bulge_511 | `DC5/sources/511/NB_511` | re-simulate (511 keV map bug fixed) |
| Vela_SNR_511 | `DC5/sources/511/Vela_SNR_511` | re-simulate (511 keV map bug fixed) |

## Modified sources
| DC4 mock component | DC5 source path | Modification |
|---|---|---|
| cygX3 | `DC5/sources/Galactic/cygX3` | transition state replaced by the hypersoft state (DC3 Cangemi et al. 2021 models) for the full 3 months at nominal flux 0.001233 ph/cm2/s |
| positron_annihilation_in_flight | `DC5/sources/511/Positrons_In_Flight_Annihilation` | Orientation 'Galactic Fixed -1.4 -0.2' -> 'Galactic Fixed -0.2 -1.4' (bug fix: MEGAlib order is b, l); flux 0.00031 -> 0.000372 ph/cm2/s (x1.2) |
| Tycho | `DC5/sources/Nucleosynthesis/Tycho` | flux 1.6e-05 -> 1e-05 ph/cm2/s (1.0x instead of 1.6x the Lopez et al. 2015 upper limit) |
| USco | `DC5/sources/Nucleosynthesis/USco` | 60Fe line fluxes 4.5e-05 -> 2.25e-05 ph/cm2/s each (x0.5; 60Fe/26Al per line 0.75 -> 0.375); 26Al unchanged |
| LMC_511 | `DC5/sources/511/LMC_511` | DC4 LMC_511 model replaced by the alternative DC3 LMC_Gaussian_511 definition, with flux x2 relative to DC3 (4.27e-06 -> 8.54e-06 ph/cm2/s; still below the SPI 2-sigma limit 3.6e-5, Siegert et al. 2016) |
| M31_511 | `DC5/sources/511/M31_511` | DC4 M31_511 model replaced by the alternative DC3 M31_Gaussian_511 definition, with the Gaussian width reduced 1.0 -> 0.5 deg (emission concentrated in the M31 bulge); DC3 flux 2.13e-7 ph/cm2/s |
| NGC_4151 | `DC5/sources/Extragalactic/NGC_4151` | thermal (Gamma=1.75, Ecut=200 keV) normalisation x1.5 (brighter state, Lubinski et al. 2010); non-thermal tail unchanged; flux 0.00188 -> 0.002726 ph/cm2/s |
| 1RXSJ170849 | `DC5/sources/Galactic/1RXSJ170849` | flux 0.00033 -> 0.000247 ph/cm2/s (x0.75, long-term hard X-ray variability, den Hartog et al. 2008); light curve trimmed to 235528 whole pulse periods so that the periodic repeat keeps the pulse phase continuous (DC4 period bug fix) |
| magnetar2 | `DC5/sources/Galactic/magnetar2` | flux 0.00033 -> 0.000495 ph/cm2/s (x1.5); light curve trimmed to 109913 whole pulse periods so that the periodic repeat keeps the pulse phase continuous (DC4 period bug fix) |
| Broad_Bulge_511 | `DC5/sources/511/BB_511` | 511 keV side nodes set to zero (bug fix) and broad-bulge intensity scaled x0.85; integrated flux 1.480e-03 -> 6.290e-04 ph/cm2/s |
| nova_co_511keV | `DC5/sources/Galactic/nova_co_511keV` | flux 0.01537 -> 0.02305 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc) |
| nova_co_continuum | `DC5/sources/Galactic/nova_co_continuum` | flux 0.1221 -> 0.1831 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc) |
| nova_co_478keV | `DC5/sources/Galactic/nova_co_478keV` | flux 2.044e-06 -> 3.066e-06 ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc) |
| 4C21p35_noflare | `DC5/sources/Extragalactic/4C21p35_noflare` | flux 0.0005535 -> 0.0008302 ph/cm2/s (x1.5) |
| 4C21p35_flare | `DC5/sources/Extragalactic/4C21p35_flare` | flux 0.01729 -> 0.02594 ph/cm2/s (x1.5) |
| 1E1740_compow | `DC5/sources/Galactic/1E1740_twocompt` | swapped compow model for the alternative twocompt model (Bouchet et al. 2009) |
| cygX1_hard | `DC5/sources/Galactic/cygX1_soft` | source in the soft state for the full 3 months (Cangemi et al. 2021 model) |
| GRS1758 | `DC5/sources/Galactic/GRS1758` | flux 0.003495 -> 0.002621 ph/cm2/s (x0.75, dimmer hard-state epoch) |
| MAXIJ1820 | `DC5/sources/Galactic/MAXIJ1820` | MAXIJ1820_0p1-0p4: 0.1382 -> 0.09675; MAXIJ1820_0p4-10: 0.005964 -> 0.004174 ph/cm2/s (x0.7, fainter hard-state outburst) |
| 26Al_Cyg_Region | `DC5/sources/Nucleosynthesis/26Al_Cyg_Region` | Gaussian width 3.0 -> 4.5 deg (Martin et al. 2009: 3 deg is a lower limit, +-3 deg uncertainty); flux unchanged |
| 60Fe_NE2001 | `DC5/sources/Nucleosynthesis/60Fe_NE2001` | map intensity x0.65 (60Fe mass 3.5 -> 2.3 Msun); total flux (both lines) 2.997e-04 -> 1.948e-04 ph/cm2/s |

## Removed sources
| DC4 mock component |
|---|
| GS1903 |
| Kepler |
| OrEr |
| PSRJ1846 |
| MAXIJ1348 |

## New sources
| Name | Origin | Position | Model |
|---|---|---|---|
| 3C273 | (from DC2) |  | average state (Madsen et al. 2015), flux 8.6e-4 ph/cm2/s; DC2 transmission-probability line replaced by DC3+ settings |
| 3C279_high | (from DC3) |  | high-state spectrum at its physical flux (x1 instead of x100): 1.19e-4 ph/cm2/s, 19.6% polarisation at 45 deg |
| PSRB1509 | (from DC2) |  | 3 energy bands with periodic pulse profiles (Kuiper et al. 2015); DC2 transmission-probability lines replaced by DC3+ settings |
| NGC_4945 | (literature) | l=305.2721, b=13.3397 | cutoff power law Gamma=1.9, Ecut=300 keV (NuSTAR: Ecut > 200-300 keV, Puccetti et al. 2014); F(20-100 keV)=2.0e-10 erg/cm2/s |
| IC_4329A | (literature) | l=317.4963, b=30.92 | cutoff power law Gamma=1.70, Ecut=178 keV, F(5-79 keV)=3.04e-10 erg/cm2/s (Brenneman et al. 2014) |
| GX339m4_hard | (literature) | l=338.9391, b=-4.3265 | black-hole LMXB in a moderately bright hard state for the full 3 months: Gamma=1.6, Ecut=200 keV, F(20-200 keV)=1.5e-9 erg/cm2/s; 5% polarisation |
| 4U0142p61 | (literature) | l=129.384, b=-0.4307 | log-parabola, local index 0.93 at 50 keV with the nuFnu peak at 228 keV (beta=0.353); F(20-229 keV)=1.5e-10 erg/cm2/s (den Hartog et al. 2008); steady (no pulsation light curve) |
| 26Al_Carina_Region | (literature) | l=287.6, b=-0.6 | 1809 keV line, 2 deg Gaussian at Trumpler 16, flux 1.5e-5 ph/cm2/s (Voss et al. 2012), width as DC3 Cygnus model |
| Ti44_hidden_SNR | (arbitrary) | l=300.398, b=-0.163 | unknown young, dust-obscured SNR: point-like 44Ti line, 4000 km/s broadening, 1.2e-5 ph/cm2/s (comparable to Tycho/Kepler models) |
| nova_one_22Na | (arbitrary) | l=71.159, b=4.096 | ONe nova at 1.5 kpc: 22Na 1275 keV line (~20 keV FWHM), ~1e-5 ph/cm2/s at 1 kpc (Hernanz 2014) scaled to 1.5 kpc; constant (22Na lifetime 3.75 yr) |
| Positrons_Point_Source | (arbitrary) | l=55.505, b=1.707 | steady point-like 511 keV line (e.g. a microquasar or pulsar positron source), 2.5e-5 ph/cm2/s, same line width as the DC4 central source |
| BHXB_hard_transient | (arbitrary) | l=15.756, b=0.966 | new black-hole X-ray binary in a long hard-state outburst: Gamma=1.6, Ecut=150 keV, 1.5e-3 ph/cm2/s (about 1/20 of the Crab in 100 keV-10 MeV) |
| PWN_hard_source | (arbitrary) | l=349.231, b=0.547 | Crab-like pulsar wind nebula ~80x fainter than the Crab nebula: power law Gamma=2.1, 4e-4 ph/cm2/s, 30% polarisation |
| magnetar3 | (arbitrary) | l=199.713, b=0.009 | steady hard-tail magnetar (no pulsation light curve): log-parabola alpha=1.2, beta=0.30, pivot 143 keV, 2.5e-4 ph/cm2/s, 50% polarisation |
| MeV_blazar | (arbitrary) | l=330.525, b=-30.528 | high-redshift FSRQ with nuFnu peak at 1 MeV: log-parabola alpha=2.0, beta=0.2 at 1 MeV, 3e-4 ph/cm2/s (between 4C 71.07 and 3C 279), 15% polarisation |
| Seyfert_new | (arbitrary) | l=31.746, b=-21.833 | Seyfert galaxy with Gamma=1.8, Ecut=300 keV, 3e-4 ph/cm2/s (a few times fainter than NGC 4151) |
| 26Al_new_region | (arbitrary) | l=316.177, b=-0.02 | additional massive-star region: 4 deg Gaussian 1809 keV source, 1.5e-5 ph/cm2/s (similar to Carina / ~40% of Cygnus) |
| Annihilation_eeg_NFW | (dark matter) |  | annihilating DM, chi chi -> e+ e- gamma (FSR), NFW: m = 17.3 MeV, <sigma v> = 3.9e-28 cm3/s (DC4: 30 MeV, 1e-25); 5.9e-4 ph/cm2/s in 0.1-10 MeV, ~5 sigma expected in 3 months |

## Dark matter (Request 6)

New in the DC5 mock dataset: annihilating MeV dark matter, χχ → e⁺e⁻γ (final-state radiation), with an NFW halo (`DC5/sources/DarkMatter/Annihilation_eeg_NFW`). It is the DC4 model (not included in the DC4 mock dataset) with a new mass and cross section: **m = 17.3 MeV, ⟨σv⟩ = 3.9 × 10⁻²⁸ cm³ s⁻¹** (DC4: 30 MeV, 10⁻²⁵ cm³ s⁻¹), giving 5.9 × 10⁻⁴ ph cm⁻² s⁻¹ in 100 keV–10 MeV. The map keeps the DC4 spatial template and grid, with each energy node rescaled.

The expected significance in the 3-month dataset is **~5σ**. This is estimated from the DC4 total-background and Crab count spectra (effective exposure from the Crab, NFW-weighted exposure from the orientation file, Compton-cone ROI background fraction), calibrated against COSI's published 1809 keV line sensitivity, and is uncertain by about a factor of 2. It is statistics-only: the signal is ~0.07% of the background in the best ROI, so detecting it requires an accurate background model. Details, caveats and references are in the source's `README_DC5.md`. The scripts are in `scripts/dm/`.

## GRBs (Request 5)

All 11 DC4 `GRB_bn` bursts keep their light-curve shape and spectral model. Their trigger time, sky position, flux, spectral parameters and polarization are new. Sources: `DC5/sources/GRBs/<name>`; the light-curve files are the DC3 ones with every time stamp shifted to the new trigger time.

| GRB | Duration (s) | Day (DC4 → DC5) | DC5 end time (unix s) | (l, b) deg | Off-axis (deg) | Zenith (deg, DC5) | Flux 0.1–10 MeV (ph/cm²/s) | Spectrum α / β / Epeak (keV) | Pol. fraction, angle |
|---|---|---|---|---|---|---|---|---|---|
| bn081207680 | 89.0 | 12.68 → **4.15** | **1835759702.1** | (177.4, -9.4) → **(208.6, -20.9)** | 5.3 → **17.7** | 9.5 | 0.0785 → **0.108** | Band -0.59 / -2.10 / 298 → **Band -0.55 / -2.39 / 196** | 0.00, 0° → **0.65, 132°** |
| bn170405777 | 88.1 | 75.40 → **4.27** | **1835770152.1** | (70.1, 24.3) → **(51.6, -44.6)** | 59.7 → **15.5** | 7.4 | 0.576 → **0.289** | Band -0.80 / -2.35 / 222 → **Band -0.36 / -2.33 / 1046** | 0.70, 160° → **0.88, 13°** |
| bn140329295 | 7.9 | 26.08 → **4.77** | **1835813092.5** | (49.4, -0.1) → **(70.0, -28.2)** | 8.2 → **7.7** | 15.3 | 0.242 → **0.356** | Band -0.81 / -2.25 / 193 → **Band -0.77 / -2.08 / 141** | 0.50, 95° → **0.00, 73°** |
| bn161004964 | 19.0 | 87.36 → **4.85** | **1835819905.8** | (190.8, -48.9) → **(91.0, -29.1)** | 15.0 → **25.0** | 36.7 | 0.857 → **1.17** | Band -0.81 / -2.39 / 114 → **Band -0.62 / -2.31 / 60** | 0.60, 10° → **0.41, 23°** |
| bn100612726 | 10.8 | 48.80 → **5.58** | **1835883013.4** | (338.4, 46.7) → **(189.5, 17.7)** | 23.5 → **6.6** | 28.4 | 1.02 → **2.02** | PL 2.49 → **PL 2.67** | 0.20, 35° → **0.56, 141°** |
| bn180504136 | 25.6 | 18.34 → **5.71** | **1835894655.6** | (27.4, -33.7) → **(135.2, 26.8)** | 12.6 → **59.0** | 80.7 | 0.418 → **0.553** | Band -0.74 / -2.12 / 113 → **Band -0.90 / -2.27 / 236** | 0.80, 45° → **0.09, 150°** |
| bn180703876 | 19.5 | 37.64 → **5.78** | **1835899952.3** | (269.7, 14.2) → **(162.5, -53.6)** | 24.8 → **23.2** | 13.0 | 0.354 → **0.514** | Band -0.78 / -1.97 / 287 → **Band -0.73 / -2.26 / 590** | 0.90, 25° → **0.34, 92°** |
| bn131122490 | 32.9 | 77.81 → **6.85** | **1835992884.9** | (59.7, -3.5) → **(202.8, -23.2)** | 0.0 → **24.8** | 6.9 | 0.965 → **1.09** | Band -0.90 / -2.29 / 258 → **Band -0.51 / -2.60 / 79** | 0.40, 175° → **0.66, 124°** |
| bn110605183 | 44.3 | 75.18 → **6.94** | **1836000254.4** | (41.6, 19.2) → **(240.6, 53.1)** | 39.8 → **22.7** | 18.7 | 1.56 → **2.28** | Band -0.61 / -2.22 / 109 → **Band -0.30 / -2.36 / 774** | 0.30, 50° → **0.31, 11°** |
| bn090424592 | 9.9 | 24.38 → **7.75** | **1836070343.2** | (21.3, -42.4) → **(57.3, 1.7)** | 20.6 → **1.2** | 22.4 | 245 → **171** | Band -1.02 / -2.76 / 164 → **Band -0.32 / -2.71 / 148** | 0.10, 110° → **0.74, 159°** |
| bn080802386 | 0.5 | 1.07 → **7.85** | **1836078836.4** | (23.5, -53.4) → **(219.5, -14.7)** | 20.6 → **39.3** | 23.1 | 150 → **88.8** | Band -0.74 / -2.10 / 622 → **Band -0.65 / -2.09 / 955** | 0.80, 90° → **0.22, 126°** |

**Timing.** All DC5 GRBs fall on days 4.15–7.85, i.e. 3–7 days after the start of the DC4 orientation file (unix 1835487300), within the first week covered by the ACS background simulations and after several days of activation build-up. Every burst, including a 5 min margin after its last light-curve time stamp, ends before 1836092100.0 (start + 7 days); the latest burst ends at 1836078836.4. Consecutive bursts are at least 1 h apart, and each burst has livetime > 0 (no SAA) from 5 min before to 5 min after.

**Off-axis angles and field of view.** The off-axis angle is the angle between the COSI z-axis (from the orientation file, same column convention as `cosipy.spacecraftfile.SpacecraftHistory`) and the GRB position. DC4: 0.0, 5.3, 8.2, 12.6, 15.0, 20.6, 20.6, 23.5, 24.8, 39.8, 59.7 deg (median 20.6). DC5: 1.2, 6.6, 7.7, 15.5, 17.7, 22.7, 23.2, 24.8, 25.0, 39.3, 59.0 deg (median 22.7). Each DC5 burst is placed at a target angle (the DC4 set jittered by ±3 deg and randomly reassigned) from the z-axis at its trigger time, at a random azimuth around the z-axis. The off-axis angle stays ≤ 60 deg and the zenith angle ≤ 100 deg (Earth occultation sets in at ~113 deg) for the full burst, and there is no slew during the burst.

**Flux.** The time-averaged photon flux (100 keV–10 MeV) is the DC4 value times a log-uniform factor in [0.5, 2]. For bn090424592 and bn080802386, which DC3/DC4 had already made artificially bright (> 100 ph/cm²/s), the factor is in [0.5, 1] so they do not get brighter.

**Spectra.** Same spectral model as in DC4 (10 Band, 1 power law). Band parameters are drawn from the Fermi GBM 10-year spectral catalog (Poolakkil et al. 2021, fluence spectra): long bursts α ~ N(−0.84, 0.35) in [−1.5, −0.3], log Epeak ~ N(log 144 keV, 0.38 dex) in [60, 1200] keV; the short burst bn080802386 α ~ N(−0.46, 0.45), log Epeak ~ N(log 413 keV, 0.35 dex); β ~ N(−2.3, 0.3) in [−3.2, −1.95]. The power-law index of bn100612726 follows the high-energy slope distribution, N(2.3, 0.25) in [1.9, 2.9], because COSI only sees the spectrum above 100 keV.

**Polarization.** The DC4 polarization fractions are spread uniformly between 0 and 0.9 (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 0.9). The DC5 fractions are drawn from the same distribution, stratified uniform on [0, 0.9] (0.00, 0.09, 0.22, 0.31, 0.34, 0.41, 0.56, 0.65, 0.66, 0.74, 0.88). Angles are uniform in [0, 180) deg.

**MEGAlib simulation inputs (Request 7).** MEGAlib has trouble simulating short bursts at large absolute unix times, so every GRB and magnetar-burst directory holds inputs in times relative to **t_ref = 1835487300.0**, the first time of the orientation file:
- `<light curve>_shifted.dat`: the light curve with time − t_ref; the source file points to it, and the original light curve is kept;
- `DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth_cut_normed.ori`: the orientation file for the Cosima run, cut to the 1 s rows covering the burst (at least 3), with time − t_ref. `..._cut.ori` holds the same rows with absolute times;
- `sim_time_reference.txt`: t_ref and the burst window, absolute and shifted.

After the Cosima run, add t_ref to the simulated times. The files were made with `scripts/make_sim_time_inputs.py` from `DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth.ori`, the 9-column orientation file with 1 s steps used for the DC4 GRB simulations (no livetime column; the cosipy SAA cut uses the 15 s file with livetime). The method is the same as `cut_ori.py` and `shift_times.py`. Two cases differ: bursts shorter than the orientation step keep the bracketing rows (at least 3), and the light curves of MGF180128A and MGF200415A, which have no `EN` footer, get their last data point shifted too.

**Fix.** The DC3 bn180703876 source file declared `EarthOccultation` for the wrong component (`bn090424592`); the DC5 file uses the correct name.

## Magnetar bursts (unchanged, half kept)

The models are unchanged from DC3/DC4. The kept bursts are copied to `DC5/sources/GRBs/<name>` only to add the time-shifted MEGAlib simulation inputs (see the GRB section).

| Component | Source path | Action |
|---|---|---|
| GRB_MGF051103 | `DC5/sources/GRBs/MGF051103` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF051103_3months_unbinned_data_filtered_with_SAAcut.fits.gz) |
| GRB_MGF180128A | `DC5/sources/GRBs/MGF180128A` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF180128A_3months_unbinned_data_filtered_with_SAAcut.fits.gz) |
| GRB_MGF200415A | `DC5/sources/GRBs/MGF200415A` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF200415A_3months_unbinned_data_filtered_with_SAAcut.fits.gz) |
| MgtBurst_bright_complex | `DC5/sources/GRBs/MgtBurst_bright_complex` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC4/Data/Sources/MgtBurst_bright_complex_unbinned_data_filtered_with_SAAcut.fits.gz) |

Not included in DC5 (random draw, seed 3662968627): GRB_MGF070201, GRB_MGF070222, GRB_MGF231115A. Four of the seven DC4 magnetar bursts are kept (half, rounded up).

## Light-curve bugs — what needs to be re-simulated
From the [bug report](https://github.com/cositools/cosi-data-challenges/blob/develop/README.md#bug-report):

- **Time-chunk normalisation bug:** nova_co (all three components), 3C454p3 (low/high), 4C21p35 (flare/no flare), PSRB1259, MAXIJ1820, MAXIJ1348. In DC5, 3C454p3 and PSRB1259 are reused and must be re-simulated with the same source file. nova_co, 4C21p35 and MAXIJ1820 are modified, so they are simulated anyway. MAXIJ1348 is removed. Any light-curve source simulated in time chunks must use the corrected normalisation.
- **Period bug:** 1RXSJ170849 and magnetar2 (both modified in DC5). Their light curves repeat periodically, but the DC4 files covered a non-whole number of rotations (235528.7 periods over 30 days and 109913.4 over 7 days), so the pulse phase jumped at every repeat. The DC5 copies are cut at 235528 and 109913 whole periods, ending on the phase-0 value (`scripts/fix_magnetar_lightcurves.py`). The time-averaged light curve stays at 1.000000, so the Flux keyword is unchanged in meaning.
- **Not affected:** the Crab (all components), LS5039 and PSRJ1846 (simulated by splitting the flux), and all GRBs and magnetar bursts (no splitting).
- **Repeating light curves in t − t_ref:** the repeating sources of the DC4 and DC5 sets (the Crab, LS5039, 1RXSJ170849, magnetar2, PSRB1509, and PSRJ1846 in DC4) have a `sim_time_reference.txt` with t_ref = 1835487300.0: they are simulated with the orientation file in t − t_ref, and t_ref is added back to the simulated times. Their light curves hold one cycle starting at 0 and are used as they are, so the first cycle starts at t_ref, as in DC4. MEGAlib counts the repeats of a light curve with a 32-bit integer (`MFunction::FindX`), which overflows at absolute times for periods below ~0.9 s.

## 511 keV and in-flight annihilation bug fixes
**In-flight annihilation position.** `DC5/sources/511/Positrons_In_Flight_Annihilation` now declares `Galactic Fixed -0.2 -1.4`. MEGAlib reads Galactic Fixed as (b, l): every other library source follows this order, e.g. the Crab `-5.78434 184.5575` (l = 184.56°, b = −5.78°, recomputed independently from RA/Dec with `scripts/eq2gal.py`), the LMC `-32.89 280.46` and Kepler `6.8 4.5`. The source is therefore centred at (l, b) = (−1.4°, −0.2°) as intended. The final check is a short cosima run (a few minutes on one core) imaged with mimrec; MEGAlib was not available where this directory was built.

**511 keV line maps.** The 510 and 512 keV nodes were set to zero, so the linearly interpolated line contains exactly the 511 keV node value per keV. Integrated fluxes (from `scripts/mapflux.py`):

| Map | Before | After fix | Note |
|---|---|---|---|
| NB_511 | 5.60e-4 | 2.80e-4 | |
| BB_511 | 1.48e-3 | 7.40e-4 | DC5 additionally scales BB by 0.85 → 6.29e-4 |
| Vela_SNR_511 | 7.03e-4 | 3.52e-4 | matches the 3.5e-4 in its README |

With the fix alone, narrow + broad bulge + DC4 central source = 2.80e-4 + 7.40e-4 + 0.80e-4 = 1.10e-3 ph cm⁻² s⁻¹, i.e. the intended ≈1.09e-3. In DC5 (BB × 0.85) the bulge total is 9.9e-4, within 1σ of the SPI bulge value. The DC3 originals were left untouched as the record of what was simulated for DC3/DC4.

## Notes
- **LMC_511, M31_511, Virgo_511:** the DC4 definitions were simulated outside cosi-sim and differ from the DC3 `*_Gaussian_511` files. Virgo_511 (reused) reuses the DC4 event file directly. LMC_511 and M31_511 (modified) are replaced by the alternative DC3 Gaussian definitions plus a small additional change, documented in their READMEs.
- Several DC4 maps and light curves are stored as `.dat.gz` in cosi-sim (thin-disk maps, magnetar light curves, including the copies in DC5/sources/Galactic/1RXSJ170849 and magnetar2). As for DC4, gunzip them in place before running the pipeline. All other DC5 files are used as-is.
- Science-team inputs (due Nov 15) will be added as a follow-up to this directory.
