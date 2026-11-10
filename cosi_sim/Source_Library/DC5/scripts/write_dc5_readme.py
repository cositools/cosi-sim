"""Write DC5/README.md from the draw/build records. Usage: python3 write_dc5_readme.py <DC5 dir> <manifest rows json>"""
import json, os, sys
import numpy as np

ROOT = sys.argv[1]
rows = json.load(open(sys.argv[2]))
log = json.load(open(os.path.join(ROOT, "DC5_build_log.json")))
draw = json.load(open(os.path.join(ROOT, "DC5_draw.json")))
gd = json.load(open(os.path.join(ROOT, "DC5_grb_draw.json")))

def count(st): return sum(1 for r in rows if r[0] == st)
def tab(st): return "\n".join(f"| {r[1]} | `{r[2]}` | {r[3]} |" for r in rows if r[0] == st)

alias = {'1E1740_compow': '1E1740', 'cygX1_hard': 'cygX1', 'Narrow_Bulge_511': 'NB_511', 'Broad_Bulge_511': 'BB_511',
         'positron_annihilation_in_flight': 'Positrons_In_Flight_Annihilation', 'Crab_DC4': 'Crab'}
mod = [f"| {r[1]} | `{r[2]}` | {log[alias.get(r[1], r[1])]['change']} |" for r in rows if r[0] == "modified"]
new = []
for r in rows:
    if r[0] != "new": continue
    e = log[r[1]]; pos = f"l={e['l']}, b={e['b']}" if "l" in e else ""
    new.append(f"| {r[1]} | {e['status'].replace('new ', '')} | {pos} | {e['change']} |")
grb_removed = [r for r in rows if r[0] == "removed" and r[1].startswith(("GRB_MGF", "MgtBurst"))]
src_removed = [r for r in rows if r[0] == "removed" and r not in grb_removed]

n_reused = count("reused") + count("reused (bug-fixed)")
n_mod, n_rem = count("modified"), len(src_removed)
n_non = n_reused + n_mod + n_rem
n_new = len(new)

g_rows = []
for n, g in sorted(gd["grbs"].items(), key=lambda kv: kv[1]["dc5"]["t0"]):
    d4, d5 = g["dc4"], g["dc5"]
    if d5["spectrum"][0] == "Band":
        s4 = f"Band {float(d4['spectrum'][3]):.2f} / {float(d4['spectrum'][4]):.2f} / {float(d4['spectrum'][5]):.0f}"
        s5 = f"Band {float(d5['spectrum'][3]):.2f} / {float(d5['spectrum'][4]):.2f} / {float(d5['spectrum'][5]):.0f}"
    else:
        s4 = f"PL {float(d4['spectrum'][3]):.2f}"; s5 = f"PL {float(d5['spectrum'][3]):.2f}"
    g_rows.append(f"| {n} | {g['duration_s']:.1f} | {d4['day']:.2f} → **{d5['day']:.2f}** | **{d5['t_end']:.1f}** | "
                  f"({d4['l']:.1f}, {d4['b']:.1f}) → **({d5['l']:.1f}, {d5['b']:.1f})** | {d4['offaxis']:.1f} → **{d5['offaxis']:.1f}** | "
                  f"{d5['zenith']:.1f} | {d4['flux']:.3g} → **{d5['flux']:.3g}** | {s4} → **{s5}** | "
                  f"{d4['pol'][0]:.2f}, {d4['pol'][1]:.0f}° → **{d5['pol'][0]:.2f}, {d5['pol'][1]:.0f}°** |")
oa4 = np.sort([g["dc4"]["offaxis"] for g in gd["grbs"].values()])
oa5 = np.sort([g["dc5"]["offaxis"] for g in gd["grbs"].values()])
pf4 = np.sort([g["dc4"]["pol"][0] for g in gd["grbs"].values()])
pf5 = np.sort([g["dc5"]["pol"][0] for g in gd["grbs"].values()])
days5 = [g["dc5"]["day"] for g in gd["grbs"].values()]

txt = f"""# DC5 mock dataset — source definitions

> **Blind dataset.** This directory is the answer key for the DC5 mock dataset. It should not be shared with the COSI team or the community until the data challenge is unblinded.

The DC5 mock dataset starts from the DC4 mock dataset (3 months, same orbit, orientation and backgrounds) and changes the source content:

| | DC4 components | Fraction |
|---|---|---|
| Reused (same source files; 2 of these carry only the 511 keV bug fix) | {n_reused} | {n_reused/n_non:.0%} |
| Modified | {n_mod} | {n_mod/n_non:.0%} |
| Removed | {n_rem} | {n_rem/n_non:.0%} |
| **New** (relative to the ~71 DC4 components) | {n_new} | {n_new/71:.0%} |
| GRBs (`GRB_bn*`): new time, spectrum and polarization | {count('GRB (modified)')} | all |
| Magnetar bursts (`MGF*`, `MgtBurst*`): unchanged, half kept | {count('magnetar burst (unchanged)')} kept, {len(grb_removed)} removed | |

Percentages refer to the non-GRB DC4 components. DC5 therefore has {n_non - n_rem + n_new} non-GRB components, {count('GRB (modified)')} GRBs and {count('magnetar burst (unchanged)')} magnetar bursts.

**How the split was made.** Components that belong to one physical source (e.g. line + continuum maps, flare + quiescent states, the three nova components) were grouped, and the groups were shuffled with a random seed ({draw['seed']}, recorded in `DC5_draw.json`). Groups were assigned to *removed* (≈10% of files, only from sources that are not well-known detections: the Crab, Cyg X-1/X-3, Cen A, NGC 4151, the 511 keV bulge/disk, Galactic 26Al/60Fe, Cas A, etc. were protected), then *modified* (≈40%), with the rest *reused*. The modification applied to each drawn source was then chosen by hand from the literature (alternative library model where one exists, otherwise a simple flux/width/state change within the published range). Positions of the arbitrary new sources are drawn from the same seed. The GRB draw uses its own seed ({gd['seed']}, `DC5_grb_draw.json`). Running `scripts/draw_dc5.py` or `scripts/draw_dc5_grbs.py` without a seed gives a different realisation.

Files:
- `DC5_mock_dataset_src_list.txt` — the `src_list` for cosi-sim ({sum(1 for r in rows if r[0] != 'removed' and r[2].startswith('DC')) + sum(r[2].count(',') for r in rows if r[0] != 'removed' and r[2].startswith('DC'))} entries; checked with `Setup.setup_srcs()`).
- `DC5_mock_dataset_manifest.md` — every component with its status, source path and what to do (simulate / re-simulate / reuse the existing DC3/DC4 event file).
- `DC5_build_log.json`, `DC5_draw.json`, `DC5_grb_draw.json` — machine-readable record of the draws and of every change.
- `scripts/` — `draw_dc5.py` (random split), `build_dc5.py` (writes the non-GRB `sources/` for this draw), `fix_magnetar_lightcurves.py` (period bug fix), `draw_dc5_grbs.py` + `build_dc5_grbs.py` (GRBs), `make_sim_time_inputs.py` (time-shifted MEGAlib inputs for GRBs and magnetar bursts), `ori_tools.py` (orientation-file geometry), `mapflux.py` (integrates cosima 3D maps), `eq2gal.py` (RA/Dec → l, b), `write_manifest.py` (src_list, manifest and `manifest_rows.json`), `write_readmes.py` (per-source `README_DC5.md` for non-GRB sources), `write_dc5_readme.py` (this file), `dm/` (dark matter map and significance estimate). Order: draw_dc5 → build_dc5 → fix_magnetar_lightcurves → `python -m cosi_sim.pipeline.time_reference --ori <9-column ori> DC5/sources/Galactic/{{1RXSJ170849,magnetar2,PSRB1509}}` (repeating light curves in t − t_ref) → draw_dc5_grbs → build_dc5_grbs → make_sim_time_inputs → dm/run_dm_choice → dm/build_dc5_dm → write_manifest → write_readmes → write_dc5_readme.
- `sources/` — one directory per modified, bug-fixed or new source, each with a `README_DC5.md` describing the model, the change, and references.

## Reused sources (same source files)
| DC4 mock component | cosi-sim source path | Action |
|---|---|---|
{tab('reused')}
{tab('reused (bug-fixed)')}

## Modified sources
| DC4 mock component | DC5 source path | Modification |
|---|---|---|
{chr(10).join(mod)}

## Removed sources
| DC4 mock component |
|---|
{chr(10).join(f"| {r[1]} |" for r in src_removed)}

## New sources
| Name | Origin | Position | Model |
|---|---|---|---|
{chr(10).join(new)}

## Dark matter (Request 6)

New in the DC5 mock dataset: annihilating MeV dark matter, χχ → e⁺e⁻γ (final-state radiation), with an NFW halo (`DC5/sources/DarkMatter/Annihilation_eeg_NFW`). It is the DC4 model (not included in the DC4 mock dataset) with a new mass and cross section: **m = 17.3 MeV, ⟨σv⟩ = 3.9 × 10⁻²⁸ cm³ s⁻¹** (DC4: 30 MeV, 10⁻²⁵ cm³ s⁻¹), giving 5.9 × 10⁻⁴ ph cm⁻² s⁻¹ in 100 keV–10 MeV. The map keeps the DC4 spatial template and grid, with each energy node rescaled.

The expected significance in the 3-month dataset is **~5σ**. This is estimated from the DC4 total-background and Crab count spectra (effective exposure from the Crab, NFW-weighted exposure from the orientation file, Compton-cone ROI background fraction), calibrated against COSI's published 1809 keV line sensitivity, and is uncertain by about a factor of 2. It is statistics-only: the signal is ~0.07% of the background in the best ROI, so detecting it requires an accurate background model. Details, caveats and references are in the source's `README_DC5.md`. The scripts are in `scripts/dm/`.

## GRBs (Request 5)

All 11 DC4 `GRB_bn` bursts keep their light-curve shape and spectral model. Their trigger time, sky position, flux, spectral parameters and polarization are new. Sources: `DC5/sources/GRBs/<name>`; the light-curve files are the DC3 ones with every time stamp shifted to the new trigger time.

| GRB | Duration (s) | Day (DC4 → DC5) | DC5 end time (unix s) | (l, b) deg | Off-axis (deg) | Zenith (deg, DC5) | Flux 0.1–10 MeV (ph/cm²/s) | Spectrum α / β / Epeak (keV) | Pol. fraction, angle |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(g_rows)}

**Timing.** All DC5 GRBs fall on days {min(days5):.2f}–{max(days5):.2f}, i.e. 3–7 days after the start of the DC4 orientation file (unix {gd['orientation_start']:.0f}), within the first week covered by the ACS background simulations and after several days of activation build-up. Every burst, including a 5 min margin after its last light-curve time stamp, ends before {gd['t_end_max']:.1f} (start + 7 days); the latest burst ends at {max(g['dc5']['t_end'] for g in gd['grbs'].values()):.1f}. Consecutive bursts are at least 1 h apart, and each burst has livetime > 0 (no SAA) from 5 min before to 5 min after.

**Off-axis angles and field of view.** The off-axis angle is the angle between the COSI z-axis (from the orientation file, same column convention as `cosipy.spacecraftfile.SpacecraftHistory`) and the GRB position. DC4: {', '.join(f'{x:.1f}' for x in oa4)} deg (median {np.median(oa4):.1f}). DC5: {', '.join(f'{x:.1f}' for x in oa5)} deg (median {np.median(oa5):.1f}). Each DC5 burst is placed at a target angle (the DC4 set jittered by ±3 deg and randomly reassigned) from the z-axis at its trigger time, at a random azimuth around the z-axis. The off-axis angle stays ≤ 60 deg and the zenith angle ≤ 100 deg (Earth occultation sets in at ~113 deg) for the full burst, and there is no slew during the burst.

**Flux.** The time-averaged photon flux (100 keV–10 MeV) is the DC4 value times a log-uniform factor in [0.5, 2]. For bn090424592 and bn080802386, which DC3/DC4 had already made artificially bright (> 100 ph/cm²/s), the factor is in [0.5, 1] so they do not get brighter.

**Spectra.** Same spectral model as in DC4 (10 Band, 1 power law). Band parameters are drawn from the Fermi GBM 10-year spectral catalog (Poolakkil et al. 2021, fluence spectra): long bursts α ~ N(−0.84, 0.35) in [−1.5, −0.3], log Epeak ~ N(log 144 keV, 0.38 dex) in [60, 1200] keV; the short burst bn080802386 α ~ N(−0.46, 0.45), log Epeak ~ N(log 413 keV, 0.35 dex); β ~ N(−2.3, 0.3) in [−3.2, −1.95]. The power-law index of bn100612726 follows the high-energy slope distribution, N(2.3, 0.25) in [1.9, 2.9], because COSI only sees the spectrum above 100 keV.

**Polarization.** The DC4 polarization fractions are spread uniformly between 0 and 0.9 ({', '.join(f'{x:.1f}' for x in pf4)}). The DC5 fractions are drawn from the same distribution, stratified uniform on [0, 0.9] ({', '.join(f'{x:.2f}' for x in pf5)}). Angles are uniform in [0, 180) deg.

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
{tab('magnetar burst (unchanged)')}

Not included in DC5 (random draw, seed {gd['seed']}): {', '.join(r[1] for r in grb_removed)}. Four of the seven DC4 magnetar bursts are kept (half, rounded up).

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
"""
open(os.path.join(ROOT, "README.md"), "w").write(txt)
print("README written", len(txt.splitlines()), "lines")
