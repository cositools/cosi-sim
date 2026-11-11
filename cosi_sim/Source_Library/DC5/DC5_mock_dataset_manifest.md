# DC5 mock dataset manifest

Every component of the DC5 mock dataset, its origin in the DC4 mock dataset, the cosi-sim source path, and what is needed to produce it.

| DC5 status | Component (DC4 mock name) | cosi-sim source path | Action |
|---|---|---|---|
| reused | CasAG16distribution | `DC4/sources/Nucleosynthesis/CasAG16distribution` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/CasAG16distribution_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| modified | cygX3 | `DC5/sources/Galactic/cygX3` | simulate DC5 source file |
| removed | GS1903 | `-` | not included in DC5 |
| removed | Kepler | `-` | not included in DC5 |
| removed | OrEr | `-` | not included in DC5 |
| modified | positron_annihilation_in_flight | `DC5/sources/511/Positrons_In_Flight_Annihilation` | simulate DC5 source file |
| reused | Positrons_Central_Source | `DC4/sources/511/Positrons_Central_Source` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/Positrons_Central_Source_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | positrons_thin_disk_cont | `DC4/sources/511/Positrons_Thin_Disk_cont` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/positrons_thin_disk_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | positrons_thin_disk_line | `DC4/sources/511/Positrons_Thin_Disk_line` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/positrons_thin_disk_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | SN1987A | `DC4/sources/Nucleosynthesis/SN1987A` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/SN1987A_unbinned_data_filtered_with_SAAcut.fits.gz |
| modified | Tycho | `DC5/sources/Nucleosynthesis/Tycho` | simulate DC5 source file |
| modified | USco | `DC5/sources/Nucleosynthesis/USco` | simulate DC5 source file |
| reused | VelaJr_44Ti | `DC4/sources/Nucleosynthesis/VelaJr_44Ti` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/VelaJr_44Ti_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| modified | LMC_511 | `DC5/sources/511/LMC_511` | simulate DC5 source file |
| modified | M31_511 | `DC5/sources/511/M31_511` | simulate DC5 source file |
| reused | Virgo_511 | `(no library file)` | reuse DC4 event file COSI-SMEX/DC4/Data/Sources/Virgo_511_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | NGC_1068 | `DC4/sources/Extragalactic/NGC_1068` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/NGC_1068_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| modified | NGC_4151 | `DC5/sources/Extragalactic/NGC_4151` | simulate DC5 source file |
| modified | 1RXSJ170849 | `DC5/sources/Galactic/1RXSJ170849` | simulate DC5 source file — light curve trimmed to whole pulse periods (period bug fixed in the DC5 file) — LC flux: correct (phase average) |
| modified | magnetar2 | `DC5/sources/Galactic/magnetar2` | simulate DC5 source file — light curve trimmed to whole pulse periods (period bug fixed in the DC5 file) — LC flux: correct (phase average) |
| reused | 4C71p07 | `DC4/sources/Extragalactic/4C71p07` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/4C71p07_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused (bug-fixed) | 3C454p3_low | `DC5/sources/Extragalactic/3C454p3_low` | re-simulate: same model, Flux keyword corrected to the time average over the light curve — LC flux: fixed, 3C454p3_low 0.00029 -> 0.0001884 ph/cm2/s (on-state flux x light-curve mean 0.6496) |
| reused (bug-fixed) | 3C454p3_high | `DC5/sources/Extragalactic/3C454p3_high` | re-simulate: same model, Flux keyword corrected to the time average over the light curve — LC flux: fixed, 3C454p3_high 0.00624 -> 0.002186 ph/cm2/s (on-state flux x light-curve mean 0.3504) |
| reused | CenA | `DC4/sources/Extragalactic/CenA` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/CenA_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Crab_DC4 | `DC4/sources/Galactic/Crab` | reuse DC4/DC3 event file COSI-SMEX/DC4/Data/Sources/Crab_DC4_3months_unbinned_data_filtered_with_SAAcut.fits.gz — LC flux: correct (phase average) |
| reused | Globular_Cluster_Tuc_47 | `DC3/sources/511/Globular_Cluster_Tuc_47` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_Tuc_47_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Globular_Cluster_Omega_Cen | `DC3/sources/511/Globular_Cluster_Omega_Cen` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_Omega_Cen_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Globular_Cluster_NGC_6397 | `DC3/sources/511/Globular_Cluster_NGC_6397` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_NGC_6397_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Globular_Cluster_NGC_6121 | `DC3/sources/511/Globular_Cluster_NGC_6121` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Globular_Cluster_NGC_6121_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Positrons_from_26Al_line | `DC3/sources/511/Positrons_from_26Al_line` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_26Al_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Positrons_from_26Al_cont | `DC3/sources/511/Positrons_from_26Al_cont` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_26Al_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Positrons_from_44Ti_line | `DC3/sources/511/Positrons_from_44Ti_line` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_44Ti_line_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | Positrons_from_44Ti_cont | `DC3/sources/511/Positrons_from_44Ti_cont` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/Positrons_from_44Ti_cont_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused (bug-fixed) | Narrow_Bulge_511 | `DC5/sources/511/NB_511` | re-simulate (511 keV map bug fixed) |
| modified | Broad_Bulge_511 | `DC5/sources/511/BB_511` | simulate DC5 source file |
| reused (bug-fixed) | Vela_SNR_511 | `DC5/sources/511/Vela_SNR_511` | re-simulate (511 keV map bug fixed) |
| reused (bug-fixed) | nova_co_511keV | `DC5/sources/Galactic/nova_co_511keV` | re-simulate: same model as DC4, Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model — LC flux: fixed, nova_co_511keV 0.01537 -> 3e-06 ph/cm2/s (time average of the Hernanz (2014) model) |
| reused (bug-fixed) | nova_co_continuum | `DC5/sources/Galactic/nova_co_continuum` | re-simulate: same model as DC4, Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model — LC flux: fixed, nova_co_cont 0.1221 -> 2.12e-05 ph/cm2/s (time average of the Hernanz (2014) model) |
| reused (bug-fixed) | nova_co_478keV | `DC5/sources/Galactic/nova_co_478keV` | re-simulate: same model as DC4, Flux keyword set to the time average of the Hernanz (2014) model, which should be the correct model — LC flux: fixed, nova_co_478keV 2.044e-06 -> 1.27e-06 ph/cm2/s (time average of the Hernanz (2014) model) |
| modified | 4C21p35_noflare | `DC5/sources/Extragalactic/4C21p35_noflare` | simulate DC5 source file — light curve: use the fixed time-chunk flux normalisation — LC flux: **CHECK**, not changed (see the light-curve flux table in README.md) |
| modified | 4C21p35_flare | `DC5/sources/Extragalactic/4C21p35_flare` | simulate DC5 source file — light curve: use the fixed time-chunk flux normalisation — LC flux: **CHECK**, not changed (see the light-curve flux table in README.md) |
| reused (bug-fixed) | PSRB1259 | `DC5/sources/Galactic/PSRB1259` | re-simulate: same model, Flux keyword corrected to the time average over the light curve — LC flux: fixed, PSRB1259 0.0006125 -> 0.0001988 ph/cm2/s (on-state flux x light-curve mean 0.3246) |
| modified | 1E1740_compow | `DC5/sources/Galactic/1E1740_twocompt` | simulate DC5 source file |
| modified | cygX1_hard | `DC5/sources/Galactic/cygX1_soft` | simulate DC5 source file |
| modified | GRS1758 | `DC5/sources/Galactic/GRS1758` | simulate DC5 source file |
| reused | LS5039 | `DC3/sources/Galactic/LS5039` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/LS5039_3months_unbinned_data_filtered_with_SAAcut.fits.gz — LC flux: correct (orbit average) |
| removed | PSRJ1846 | `-` | not included in DC5 |
| modified | MAXIJ1820 | `DC5/sources/Galactic/MAXIJ1820` | simulate DC5 source file — light curve: use the fixed time-chunk flux normalisation — LC flux: fixed, MAXIJ1820_0p1-0p4 0.09675 -> 0.06285 ph/cm2/s (on-state flux x light-curve mean 0.6496); MAXIJ1820_0p4-10 0.004174 -> 0.002712 ph/cm2/s (on-state flux x light-curve mean 0.6496) |
| removed | MAXIJ1348 | `-` | not included in DC5 |
| modified | 26Al_Cyg_Region | `DC5/sources/Nucleosynthesis/26Al_Cyg_Region` | simulate DC5 source file |
| reused | 26Al_NE2001 | `DC3/sources/Al26/26Al_NE2001` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/26Al_NE2001_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| reused | 60Fe_Cyg_Region | `DC3/sources/Fe60/60Fe_Cyg_Region` | reuse DC4/DC3 event file COSI-SMEX/DC3/Data/Sources/60Fe_Cyg_Region_3months_unbinned_data_filtered_with_SAAcut.fits.gz |
| modified | 60Fe_NE2001 | `DC5/sources/Nucleosynthesis/60Fe_NE2001` | simulate DC5 source file |
| new | 3C273 | `DC5/sources/Extragalactic/3C273` | simulate DC5 source file |
| new | 3C279_high | `DC5/sources/Extragalactic/3C279_high` | simulate DC5 source file |
| new | PSRB1509 | `DC5/sources/Galactic/PSRB1509` | simulate DC5 source file — LC flux: correct (phase average) |
| new | NGC_4945 | `DC5/sources/Extragalactic/NGC_4945` | simulate DC5 source file |
| new | IC_4329A | `DC5/sources/Extragalactic/IC_4329A` | simulate DC5 source file |
| new | GX339m4_hard | `DC5/sources/Galactic/GX339m4_hard` | simulate DC5 source file |
| new | 4U0142p61 | `DC5/sources/Galactic/4U0142p61` | simulate DC5 source file |
| new | 26Al_Carina_Region | `DC5/sources/Nucleosynthesis/26Al_Carina_Region` | simulate DC5 source file |
| new | Ti44_hidden_SNR | `DC5/sources/Nucleosynthesis/Ti44_hidden_SNR` | simulate DC5 source file |
| new | nova_one_22Na | `DC5/sources/Nucleosynthesis/nova_one_22Na` | simulate DC5 source file |
| new | Positrons_Point_Source | `DC5/sources/511/Positrons_Point_Source` | simulate DC5 source file |
| new | BHXB_hard_transient | `DC5/sources/Galactic/BHXB_hard_transient` | simulate DC5 source file |
| new | PWN_hard_source | `DC5/sources/Galactic/PWN_hard_source` | simulate DC5 source file |
| new | magnetar3 | `DC5/sources/Galactic/magnetar3` | simulate DC5 source file |
| new | MeV_blazar | `DC5/sources/Extragalactic/MeV_blazar` | simulate DC5 source file |
| new | Seyfert_new | `DC5/sources/Extragalactic/Seyfert_new` | simulate DC5 source file |
| new | 26Al_new_region | `DC5/sources/Nucleosynthesis/26Al_new_region` | simulate DC5 source file |
| new | Annihilation_eeg_NFW | `DC5/sources/DarkMatter/Annihilation_eeg_NFW` | simulate DC5 source file |
| GRB (modified) | GRB_bn081207680 | `DC5/sources/GRBs/bn081207680` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 4.15, off-axis 17.7 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn090424592 | `DC5/sources/GRBs/bn090424592` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 7.75, off-axis 1.2 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn100612726 | `DC5/sources/GRBs/bn100612726` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 5.58, off-axis 6.6 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn110605183 | `DC5/sources/GRBs/bn110605183` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 6.94, off-axis 22.7 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn131122490 | `DC5/sources/GRBs/bn131122490` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 6.85, off-axis 24.8 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn140329295 | `DC5/sources/GRBs/bn140329295` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 4.77, off-axis 7.7 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn161004964 | `DC5/sources/GRBs/bn161004964` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 4.85, off-axis 25.0 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn170405777 | `DC5/sources/GRBs/bn170405777` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 4.27, off-axis 15.5 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn180504136 | `DC5/sources/GRBs/bn180504136` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 5.71, off-axis 59.0 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn180703876 | `DC5/sources/GRBs/bn180703876` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 5.78, off-axis 23.2 deg) — LC flux: correct (burst average) |
| GRB (modified) | GRB_bn080802386_flux150 | `DC5/sources/GRBs/bn080802386` | simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day 7.85, off-axis 39.3 deg) — LC flux: correct (burst average) |
| magnetar burst (unchanged) | GRB_MGF051103 | `DC5/sources/GRBs/MGF051103` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF051103_3months_unbinned_data_filtered_with_SAAcut.fits.gz) — LC flux: correct (burst average) |
| removed | GRB_MGF070201 | `-` | magnetar burst not included in DC5 (half of the DC4 magnetar bursts kept) |
| removed | GRB_MGF070222 | `-` | magnetar burst not included in DC5 (half of the DC4 magnetar bursts kept) |
| magnetar burst (unchanged) | GRB_MGF180128A | `DC5/sources/GRBs/MGF180128A` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF180128A_3months_unbinned_data_filtered_with_SAAcut.fits.gz) — LC flux: correct (burst average) |
| magnetar burst (unchanged) | GRB_MGF200415A | `DC5/sources/GRBs/MGF200415A` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC3/Data/Sources/GRB_MGF200415A_3months_unbinned_data_filtered_with_SAAcut.fits.gz) — LC flux: correct (burst average) |
| removed | GRB_MGF231115A | `-` | magnetar burst not included in DC5 (half of the DC4 magnetar bursts kept) |
| magnetar burst (unchanged) | MgtBurst_bright_complex | `DC5/sources/GRBs/MgtBurst_bright_complex` | unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file COSI-SMEX/DC4/Data/Sources/MgtBurst_bright_complex_unbinned_data_filtered_with_SAAcut.fits.gz) — LC flux: correct (burst average) |
