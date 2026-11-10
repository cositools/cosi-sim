"""Write DC5 manifest files: DC5_mock_dataset_src_list.txt, DC5_mock_dataset_manifest.md and
scripts/manifest_rows.json (the summary rows used by write_dc5_readme.py).

Usage: python3 write_manifest.py <Source_Library/DC5 dir> <Source_Library/DC5/DC5_draw.json>
"""
import json, os, sys
ROOT = sys.argv[1]                       # .../Source_Library/DC5
draw = json.load(open(sys.argv[2]))
W4, W3 = "COSI-SMEX/DC4/Data/Sources/", "COSI-SMEX/DC3/Data/Sources/"
sfx = "_3months_unbinned_data_filtered_with_SAAcut.fits.gz"

# unit -> list of (DC4-mock label, DC4 library path, DC4 wasabi event file, has light curve)
U = {
 "CasAG16distribution": [("CasAG16distribution", "DC4/sources/Nucleosynthesis/CasAG16distribution", W4+"CasAG16distribution"+sfx, False)],
 "cygX3": [("cygX3", "DC4/sources/Galactic/cygX3", W4+"cygX3"+sfx, False)],
 "G1903": [("GS1903", "DC4/sources/Nucleosynthesis/G1903", W4+"GS1903_unbinned_data_filtered_with_SAAcut.fits.gz", False)],
 "Kepler": [("Kepler", "DC4/sources/Nucleosynthesis/Kepler", W4+"Kepler"+sfx, False)],
 "OrEr": [("OrEr", "DC4/sources/Nucleosynthesis/OrEr", W4+"OrEr"+sfx, False)],
 "Positrons_In_Flight_Annihilation": [("positron_annihilation_in_flight", "DC4/sources/511/Positrons_In_Flight_Annihilation", W4+"positron_annihilation_in_flight"+sfx, False)],
 "Positrons_Central_Source": [("Positrons_Central_Source", "DC4/sources/511/Positrons_Central_Source", W4+"Positrons_Central_Source"+sfx, False)],
 "Positrons_Thin_Disk": [("positrons_thin_disk_cont", "DC4/sources/511/Positrons_Thin_Disk_cont", W4+"positrons_thin_disk_cont"+sfx, False),
                         ("positrons_thin_disk_line", "DC4/sources/511/Positrons_Thin_Disk_line", W4+"positrons_thin_disk_line"+sfx, False)],
 "SN1987A": [("SN1987A", "DC4/sources/Nucleosynthesis/SN1987A", W4+"SN1987A_unbinned_data_filtered_with_SAAcut.fits.gz", False)],
 "Tycho": [("Tycho", "DC4/sources/Nucleosynthesis/Tycho", W4+"Tycho"+sfx, False)],
 "USco": [("USco", "DC4/sources/Nucleosynthesis/USco", W4+"USco"+sfx, False)],
 "VelaJr_44Ti": [("VelaJr_44Ti", "DC4/sources/Nucleosynthesis/VelaJr_44Ti", W4+"VelaJr_44Ti"+sfx, False)],
 "LMC_511": [("LMC_511", "(not in cosi-sim)", W4+"LMC_511"+sfx, False)],
 "M31_511": [("M31_511", "(not in cosi-sim)", W4+"M31_511"+sfx, False)],
 "Virgo_511": [("Virgo_511", "(not in cosi-sim)", W4+"Virgo_511"+sfx, False)],
 "NGC_1068": [("NGC_1068", "DC4/sources/Extragalactic/NGC_1068", W4+"NGC_1068"+sfx, False)],
 "NGC_4151": [("NGC_4151", "DC4/sources/Extragalactic/NGC_4151", W4+"NGC_4151"+sfx, False)],
 "1RXSJ170849": [("1RXSJ170849", "DC4/sources/Galactic/1RXSJ170849", W4+"1RXSJ170849"+sfx, True)],
 "magnetar2": [("magnetar2", "DC4/sources/Galactic/magnetar2", W4+"magnetar2"+sfx, True)],
 "4C71p07": [("4C71p07", "DC4/sources/Extragalactic/4C71p07", W4+"4C71p07"+sfx, False)],
 "3C454p3": [("3C454p3_low", "DC4/sources/Extragalactic/3C454p3_low", W4+"3C454p3_low"+sfx, True),
             ("3C454p3_high", "DC4/sources/Extragalactic/3C454p3_high", W4+"3C454p3_high"+sfx, True)],
 "CenA": [("CenA", "DC4/sources/Extragalactic/CenA", W4+"CenA"+sfx, False)],
 "Crab": [("Crab_DC4", "DC4/sources/Galactic/Crab", W4+"Crab_DC4"+sfx, True)],
 "GC_Tuc_47": [("Globular_Cluster_Tuc_47", "DC3/sources/511/Globular_Cluster_Tuc_47", W3+"Globular_Cluster_Tuc_47"+sfx, False)],
 "GC_Omega_Cen": [("Globular_Cluster_Omega_Cen", "DC3/sources/511/Globular_Cluster_Omega_Cen", W3+"Globular_Cluster_Omega_Cen"+sfx, False)],
 "GC_NGC_6397": [("Globular_Cluster_NGC_6397", "DC3/sources/511/Globular_Cluster_NGC_6397", W3+"Globular_Cluster_NGC_6397"+sfx, False)],
 "GC_NGC_6121": [("Globular_Cluster_NGC_6121", "DC3/sources/511/Globular_Cluster_NGC_6121", W3+"Globular_Cluster_NGC_6121"+sfx, False)],
 "Positrons_from_26Al": [("Positrons_from_26Al_line", "DC3/sources/511/Positrons_from_26Al_line", W3+"Positrons_from_26Al_line"+sfx, False),
                         ("Positrons_from_26Al_cont", "DC3/sources/511/Positrons_from_26Al_cont", W3+"Positrons_from_26Al_cont"+sfx, False)],
 "Positrons_from_44Ti": [("Positrons_from_44Ti_line", "DC3/sources/511/Positrons_from_44Ti_line", W3+"Positrons_from_44Ti_line"+sfx, False),
                         ("Positrons_from_44Ti_cont", "DC3/sources/511/Positrons_from_44Ti_cont", W3+"Positrons_from_44Ti_cont"+sfx, False)],
 "NB_511": [("Narrow_Bulge_511", "DC3/sources/511/NB_511", W3+"Narrow_Bulge_511"+sfx, False)],
 "BB_511": [("Broad_Bulge_511", "DC3/sources/511/BB_511", W3+"Broad_Bulge_511"+sfx, False)],
 "Vela_SNR_511": [("Vela_SNR_511", "DC3/sources/511/Vela_SNR_511", W3+"Vela_SNR_511"+sfx, False)],
 "nova_co": [("nova_co_511keV", "DC3/sources/Galactic/nova_co_511keV", W3+"nova_co_511keV"+sfx, True),
             ("nova_co_continuum", "DC3/sources/Galactic/nova_co_continuum", W3+"nova_co_continuum"+sfx, True),
             ("nova_co_478keV", "DC3/sources/Galactic/nova_co_478keV", W3+"nova_co_478keV"+sfx, True)],
 "4C21p35": [("4C21p35_noflare", "DC3/sources/Extragalactic/4C21p35_noflare", W3+"4C21p35_noflare"+sfx, True),
             ("4C21p35_flare", "DC3/sources/Extragalactic/4C21p35_flare", W3+"4C21p35_flare"+sfx, True)],
 "PSRB1259": [("PSRB1259", "DC3/sources/Galactic/PSRB1259", W3+"PSRB1259"+sfx, True)],
 "1E1740_compow": [("1E1740_compow", "DC3/sources/Galactic/1E1740_compow", W3+"1E1740_compow"+sfx, False)],
 "cygX1_hard": [("cygX1_hard", "DC3/sources/Galactic/cygX1_hard", W3+"cygX1_hard"+sfx, False)],
 "GRS1758": [("GRS1758", "DC3/sources/Galactic/GRS1758", W3+"GRS1758"+sfx, False)],
 "LS5039": [("LS5039", "DC3/sources/Galactic/LS5039", W3+"LS5039"+sfx, True)],
 "PSRJ1846": [("PSRJ1846", "DC3/sources/Galactic/PSRJ1846", W3+"PSRJ1846"+sfx, True)],
 "MAXIJ1820": [("MAXIJ1820", "DC3/sources/Galactic/MAXIJ1820", W3+"MAXIJ1820"+sfx, True)],
 "MAXIJ1348": [("MAXIJ1348", "DC3/sources/Galactic/MAXIJ1348", W3+"MAXIJ1348"+sfx, True)],
 "26Al_Cyg_Region": [("26Al_Cyg_Region", "DC3/sources/Al26/26Al_Cyg_Region", W3+"26Al_Cyg_Region"+sfx, False)],
 "26Al_NE2001": [("26Al_NE2001", "DC3/sources/Al26/26Al_NE2001", W3+"26Al_NE2001"+sfx, False)],
 "60Fe_Cyg_Region": [("60Fe_Cyg_Region", "DC3/sources/Fe60/60Fe_Cyg_Region", W3+"60Fe_Cyg_Region"+sfx, False)],
 "60Fe_NE2001": [("60Fe_NE2001", "DC3/sources/Fe60/60Fe_NE2001", W3+"60Fe_NE2001"+sfx, False)],
}
assert set(U) == set(draw["removed"] + draw["modified"] + draw["reused"]), set(U) ^ set(draw["removed"] + draw["modified"] + draw["reused"])

# DC5 paths of modified / bug-fixed units
D5 = {
 "Positrons_In_Flight_Annihilation": ["DC5/sources/511/Positrons_In_Flight_Annihilation"],
 "BB_511": ["DC5/sources/511/BB_511"], "NB_511": ["DC5/sources/511/NB_511"], "Vela_SNR_511": ["DC5/sources/511/Vela_SNR_511"],
 "LMC_511": ["DC5/sources/511/LMC_511"], "M31_511": ["DC5/sources/511/M31_511"],
 "1E1740_compow": ["DC5/sources/Galactic/1E1740_twocompt"], "cygX1_hard": ["DC5/sources/Galactic/cygX1_soft"],
 "cygX3": ["DC5/sources/Galactic/cygX3"], "GRS1758": ["DC5/sources/Galactic/GRS1758"],
 "1RXSJ170849": ["DC5/sources/Galactic/1RXSJ170849"], "magnetar2": ["DC5/sources/Galactic/magnetar2"],
 "MAXIJ1820": ["DC5/sources/Galactic/MAXIJ1820"],
 "nova_co": ["DC5/sources/Galactic/nova_co_511keV", "DC5/sources/Galactic/nova_co_continuum", "DC5/sources/Galactic/nova_co_478keV"],
 "4C21p35": ["DC5/sources/Extragalactic/4C21p35_noflare", "DC5/sources/Extragalactic/4C21p35_flare"],
 "NGC_4151": ["DC5/sources/Extragalactic/NGC_4151"],
 "26Al_Cyg_Region": ["DC5/sources/Nucleosynthesis/26Al_Cyg_Region"], "60Fe_NE2001": ["DC5/sources/Nucleosynthesis/60Fe_NE2001"],
 "Tycho": ["DC5/sources/Nucleosynthesis/Tycho"], "USco": ["DC5/sources/Nucleosynthesis/USco"],
}
NEW = ["DC5/sources/Extragalactic/3C273", "DC5/sources/Extragalactic/3C279_high", "DC5/sources/Galactic/PSRB1509",
       "DC5/sources/Extragalactic/NGC_4945", "DC5/sources/Extragalactic/IC_4329A", "DC5/sources/Galactic/GX339m4_hard",
       "DC5/sources/Galactic/4U0142p61", "DC5/sources/Nucleosynthesis/26Al_Carina_Region",
       "DC5/sources/Nucleosynthesis/Ti44_hidden_SNR", "DC5/sources/Nucleosynthesis/nova_one_22Na", "DC5/sources/511/Positrons_Point_Source",
       "DC5/sources/Galactic/BHXB_hard_transient", "DC5/sources/Galactic/PWN_hard_source", "DC5/sources/Galactic/magnetar3",
       "DC5/sources/Extragalactic/MeV_blazar", "DC5/sources/Extragalactic/Seyfert_new", "DC5/sources/Nucleosynthesis/26Al_new_region",
       "DC5/sources/DarkMatter/Annihilation_eeg_NFW"]
GRB_BN = [("GRB_bn081207680", "bn081207680"), ("GRB_bn090424592", "bn090424592"), ("GRB_bn100612726", "bn100612726"),
       ("GRB_bn110605183", "bn110605183"), ("GRB_bn131122490", "bn131122490"), ("GRB_bn140329295", "bn140329295"),
       ("GRB_bn161004964", "bn161004964"), ("GRB_bn170405777", "bn170405777"), ("GRB_bn180504136", "bn180504136"),
       ("GRB_bn180703876", "bn180703876"), ("GRB_bn080802386_flux150", "bn080802386")]
MAGNETAR = [("GRB_MGF051103", "MGF051103", W3), ("GRB_MGF070201", "MGF070201", W3), ("GRB_MGF070222", "MGF070222", W3),
       ("GRB_MGF180128A", "MGF180128A", W3), ("GRB_MGF200415A", "MGF200415A", W3), ("GRB_MGF231115A", "MGF231115A", W3),
       ("MgtBurst_bright_complex", "MgtBurst_bright_complex", W4)]
grbdraw = json.load(open(os.path.join(ROOT, "DC5_grb_draw.json")))

# Light-curve bugs (cosi-data-challenges bug report):
#  - time-chunk normalisation bug: nova_co (x3), 3C454p3 (low/high), 4C21p35 (flare/noflare), PSRB1259, MAXIJ1820, MAXIJ1348
#  - period bug (light curve not a whole number of rotations): 1RXSJ170849, magnetar2
LC_TIMECHUNK = {"nova_co", "3C454p3", "4C21p35", "PSRB1259", "MAXIJ1820", "MAXIJ1348"}
LC_PERIOD = {"1RXSJ170849", "magnetar2"}
# Repeating pulsar light curves shorter than ~0.86 s: at absolute times MEGAlib's repeat count
# overflows (MFunction::FindX); the library now has them in t - t_ref (cosi_sim.pipeline.time_reference).
LC_REPEAT_OVERFLOW = {"Crab"}

rows = []   # (status, dc4 label, dc5 src_list path, action)
for u, comps in U.items():
    note = ""
    if u in LC_TIMECHUNK: note = " — light curve: use the fixed time-chunk flux normalisation"
    if u in LC_PERIOD: note = " — light curve trimmed to whole pulse periods (period bug fixed in the DC5 file)"
    if u in draw["removed"]:
        for lab, p, w, lc in comps: rows.append(("removed", lab, "-", "not included in DC5"))
    elif u in draw["modified"]:
        paths = D5[u]
        if len(paths) == len(comps):
            for (lab, p, w, lc), q in zip(comps, paths): rows.append(("modified", lab, q, "simulate DC5 source file" + note))
        else:
            rows.append(("modified", " + ".join(c[0] for c in comps), ", ".join(paths), "simulate DC5 source file" + note))
    else:
        for lab, p, w, lc in comps:
            if u in ("NB_511", "Vela_SNR_511"):
                rows.append(("reused (bug-fixed)", lab, D5[u][0], "re-simulate (511 keV map bug fixed)"))
            elif u in LC_TIMECHUNK:
                rows.append(("reused", lab, p, "re-simulate with the same source file (time-chunk light-curve bug)"))
            elif u in LC_REPEAT_OVERFLOW:
                rows.append(("reused", lab, p, "re-simulate with the same source file (pulsar light curves now in "
                                               "t - t_ref; at absolute times MEGAlib's repeat count overflows)"))
            elif p.startswith("("):
                rows.append(("reused", lab, "(no library file)", f"reuse DC4 event file {w}"))
            else:
                rows.append(("reused", lab, p, f"reuse DC4/DC3 event file {w}"))
for q in NEW: rows.append(("new", os.path.basename(q), q, "simulate DC5 source file"))
for lab, d in GRB_BN:
    g = grbdraw["grbs"][d]["dc5"]
    rows.append(("GRB (modified)", lab, "DC5/sources/GRBs/" + d,
                 f"simulate DC5 source file with the time-shifted inputs, t_ref = 1835487300.0 (day {g['day']:.2f}, off-axis {g['offaxis']:.1f} deg)"))
for lab, d, w in MAGNETAR:
    if d in grbdraw["magnetar_kept"]:
        ev = f"{w}{lab}{sfx}" if w == W3 else f"{W4}MgtBurst_bright_complex_unbinned_data_filtered_with_SAAcut.fits.gz"
        rows.append(("magnetar burst (unchanged)", lab, "DC5/sources/GRBs/" + d,
                     f"unchanged model; simulate with the time-shifted DC5 inputs (or reuse event file {ev})"))
    else:
        rows.append(("removed", lab, "-", "magnetar burst not included in DC5 (half of the DC4 magnetar bursts kept)"))

srcs = [r[2] for r in rows if r[0] not in ("removed",) and r[2].startswith("DC")]
srcs = [x for r in srcs for x in r.split(", ")]
with open(os.path.join(ROOT, "DC5_mock_dataset_src_list.txt"), "w") as f:
    f.write("# DC5 mock dataset: cosi-sim src_list entries (one simulation per entry, as for DC3/DC4).\n")
    f.write("# Virgo_511 has no library file: its DC4 event file is reused directly (see DC5_mock_dataset_manifest.md).\n")
    f.write("[\n" + ",\n".join(f"'{s}'" for s in srcs) + "\n]\n")
with open(os.path.join(ROOT, "DC5_mock_dataset_manifest.md"), "w") as f:
    f.write("# DC5 mock dataset manifest\n\nEvery component of the DC5 mock dataset, its origin in the DC4 mock dataset, the cosi-sim source path, and what is needed to produce it.\n\n")
    f.write("| DC5 status | Component (DC4 mock name) | cosi-sim source path | Action |\n|---|---|---|---|\n")
    for r in rows: f.write(f"| {r[0]} | {r[1]} | `{r[2]}` | {r[3]} |\n")
from collections import Counter
c = Counter(r[0] for r in rows); print(c, "src_list entries:", len(srcs))
json.dump(rows, open(os.path.join(ROOT, "scripts", "manifest_rows.json"), "w"))   # input to write_dc5_readme.py
