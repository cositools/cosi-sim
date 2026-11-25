"""Write DC5/README.md from the draw/build records. Usage: python3 write_dc5_readme.py <DC5 dir> <manifest rows json>"""
import csv, json, os, sys
import numpy as np

ROOT = sys.argv[1]
rows = json.load(open(sys.argv[2]))
log = json.load(open(os.path.join(ROOT, "DC5_build_log.json")))
draw = json.load(open(os.path.join(ROOT, "DC5_draw.json")))
gd = json.load(open(os.path.join(ROOT, "DC5_grb_draw.json")))
redrawn = "; ".join(f"{n}: {g['dc5']['epeak_cosima_redraw_from']:.0f} → {float(g['dc5']['spectrum'][5]):.0f} keV"
                    for n, g in gd["grbs"].items() if "epeak_cosima_redraw_from" in g["dc5"]) or "none"
lcf = json.load(open(os.path.join(ROOT, "lc_flux_check.json")))

def lcrow(r):
    if r["verdict"] == "fixed":
        return f"| `{r['source']}` | {r['component']} | **fixed** | {r['flux_old']:.4g} → {r['flux_new']:.4g} | {r['note']} |"
    if r["verdict"] == "check":
        return f"| `{r['source']}` | {r['component']} | **CHECK** | not changed | {r['note']} |"
    return f"| `{r['source']}` | {r['component']} | correct | not changed | {r['note']} |"
lc_bursts = [r for r in lcf if r["source"].startswith("DC5/sources/GRBs/")]
lc_table = "\n".join(lcrow(r) for r in lcf if r not in lc_bursts)
lc_table += f"\n| `DC5/sources/GRBs/*` ({len(lc_bursts)} bursts) | all | correct | not changed | {lc_bursts[0]['note']} |"
n_lc_fix = sum(1 for r in rows if r[0] == "reused (bug-fixed)" and "Flux keyword" in r[3])

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
n_mod, n_rem, n_repl = count("modified"), len(src_removed), count("replaced")
n_non = n_reused + n_mod + n_rem + n_repl
n_new = len(new)

g_rows = []
for n, g in sorted(gd["grbs"].items(), key=lambda kv: kv[1]["dc5"]["t0"]):
    d4, d5 = g["dc4"], g["dc5"]
    if d5["spectrum"][0] == "Band":
        s4 = f"Band {float(d4['spectrum'][3]):.2f} / {float(d4['spectrum'][4]):.2f} / {(2 + float(d4['spectrum'][3])) * float(d4['spectrum'][5]):.0f}"
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

ti = json.load(open(os.path.join(ROOT, "DC5_ti44_draw.json")))
ti_rows = "\n".join(f"| {r['snr']} | {r['l']:.2f} | {r['b']:.2f} | {r['flux']:.3g} | `{r['spectrum']}` | {r['centroid_keV']:.1f} |"
                    for r in ti["snrs"])
ti_replaced = ", ".join(r[1] for r in rows if r[0] == "replaced")

pe_dir = os.path.join(ROOT, "sources", "ParticleEvents")
pe = list(csv.DictReader(open(os.path.join(pe_dir, "events.csv")), delimiter="\t"))
pe_place = json.load(open(os.path.join(pe_dir, "placement.json")))
pe_enr = list(csv.DictReader(open(os.path.join(ROOT, "sources", "ParticleEvents_enriched", "events.csv")), delimiter="\t"))
pe_rows = [f"| {r['Event']} | {(float(r['Start time (s)']) - gd['orientation_start']) / 86400 + 1:.2f} | {r['Start time (s)']} | "
           f"{r['Lightcurve duration (s)']} | {r['E0 (keV)']} | {float(r['Peak I(>30 keV) (e/cm^2/s/sr)']):.2g} | "
           f"{float(r['Expected peak ACS gamma (cps)']):.0f} | {float(r['Rocking (deg)']):+.1f} | "
           f"{float(r['Yaw (deg)']):.0f} ({float(r['Yaw change (deg)']):.0f}) |" for r in pe]
pe_enr_place = json.load(open(os.path.join(ROOT, "sources", "ParticleEvents_enriched", "placement.json")))

txt = f"""# DC5 mock dataset — source definitions

The DC5 mock dataset starts from the DC4 mock dataset (3 months, same orbit, orientation and backgrounds) and changes the source content:

| | DC4 components | Fraction |
|---|---|---|
| Reused (same source files; {count('reused (bug-fixed)')} of these carry only a bug fix: {count('reused (bug-fixed)') - n_lc_fix} for the 511 keV map, {n_lc_fix} for the light-curve Flux keyword) | {n_reused} | {n_reused/n_non:.0%} |
| Modified | {n_mod} | {n_mod/n_non:.0%} |
| Removed | {n_rem} | {n_rem/n_non:.0%} |
| Replaced by the 44Ti SNR population (Request 14) | {n_repl} | {n_repl/n_non:.0%} |
| **New** (relative to the ~71 DC4 components) | {n_new} | {n_new/71:.0%} |
| GRBs (`GRB_bn*`): new time, spectrum and polarization | {count('GRB (modified)')} | all |
| Magnetar bursts (`MGF*`, `MgtBurst*`): unchanged, half kept | {count('magnetar burst (unchanged)')} kept, {len(grb_removed)} removed | |
| Particle events for the ACS (`ParticleEvents/`): new | {len(pe)} | |

Percentages refer to the non-GRB DC4 components. DC5 therefore has {n_non - n_rem - n_repl + n_new} non-GRB components, {count('GRB (modified)')} GRBs and {count('magnetar burst (unchanged)')} magnetar bursts.

**How the split was made.** Components that belong to one physical source (e.g. line + continuum maps, flare + quiescent states, the three nova components) were grouped, and the groups were shuffled with a random seed ({draw['seed']}, recorded in `DC5_draw.json`). Groups were assigned to *removed* (≈10% of files, only from sources that are not well-known detections: the Crab, Cyg X-1/X-3, Cen A, NGC 4151, the 511 keV bulge/disk, Galactic 26Al/60Fe, Cas A, etc. were protected), then *modified* (≈40%), with the rest *reused*. The modification applied to each drawn source was then chosen by hand from the literature (alternative library model where one exists, otherwise a simple flux/width/state change within the published range). Positions of the arbitrary new sources are drawn from the same seed. The GRB draw uses its own seed ({gd['seed']}, `DC5_grb_draw.json`). Running `scripts/draw_dc5.py` or `scripts/draw_dc5_grbs.py` without a seed gives a different realisation.

Files:
- `DC5_mock_dataset_src_list.txt` — the `src_list` for cosi-sim ({sum(1 for r in rows if r[0] not in ('removed', 'replaced') and r[2].startswith('DC')) + sum(r[2].count(',') for r in rows if r[0] not in ('removed', 'replaced') and r[2].startswith('DC'))} entries; checked with `Setup.setup_srcs()`).
- `DC5_mock_dataset_manifest.md` — every component with its status, source path and what to do.
- `DC5_build_log.json`, `DC5_draw.json`, `DC5_grb_draw.json`, `DC5_ti44_draw.json` — machine-readable record of the draws and of every change.
- `scripts/` — `draw_dc5.py` (random split), `build_dc5.py` (writes the non-GRB `sources/` for this draw), `fix_magnetar_lightcurves.py` (period bug fix), `fix_lightcurve_fluxes.py` (light-curve Flux keywords; writes `lc_flux_check.json`), `draw_dc5_grbs.py` + `build_dc5_grbs.py` (GRBs; `grb_band.py` holds cosima's Band E0 rule, applied to the committed draw with `apply_grb_band_rule.py`), `make_sim_time_inputs.py` (time-shifted MEGAlib inputs for GRBs and magnetar bursts), `ori_tools.py` (orientation-file geometry), `mapflux.py` (integrates cosima 3D maps), `eq2gal.py` (RA/Dec → l, b), `write_manifest.py` (src_list, manifest and `manifest_rows.json`), `write_readmes.py` (per-source `README_DC5.md` for non-GRB sources), `write_dc5_readme.py` (this file), `dm/` (dark matter map and significance estimate), `particle_events/` (particle events for the ACS: the GRB group's generator with the frame fix, `place_events.py`, the ACS pilot), `ti44/` (44Ti SNR population: A. Anaya's population-synthesis maps and spectra, `build_ti44_population.py`). Order: draw_dc5 → build_dc5 → fix_magnetar_lightcurves → fix_lightcurve_fluxes → `python -m cosi_sim.pipeline.time_reference --ori <9-column ori> DC5/sources/Galactic/{{1RXSJ170849,magnetar2,PSRB1509}}` (repeating light curves in t − t_ref) → draw_dc5_grbs → build_dc5_grbs → make_sim_time_inputs → dm/run_dm_choice → dm/build_dc5_dm → ti44/build_ti44_population → particle_events/place_events.py (blind set, then enriched set; commands in `sources/ParticleEvents/README.md`) → write_manifest → write_readmes → write_dc5_readme.
- `sources/` — one directory per modified, bug-fixed or new source, each with a `README_DC5.md` describing the model, the change, and references.

## Reused sources (same source files)
All components are simulated for DC5, the reused ones included: DC5 needs the L2 data (the mimrec `.tra` outputs), which are not available for the DC3/DC4 simulations. The DC3/DC4 event files are listed for comparison.

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

## 44Ti SNR population (Request 14)

The 44Ti supernova remnants come from a population synthesis by A. Anaya (`DC5/sources/Nucleosynthesis/Ti44_SNR_population`, one point-source component per SNR). One of the 19 population-synthesis maps was drawn at random (**`{ti['map']}`**, seed {ti['seed']}; `DC5_ti44_draw.json`). Its {ti['n_snr']} SNRs are the 5 known young SNRs at their real positions with population-synthesis fluxes and {ti['n_snr'] - 5} SNRs at random positions; some may be below the detection threshold. Each SNR has a different 1157 keV line profile, drawn from the 48 population-synthesis spectra; Flux is the line flux over the spectrum range (1110–1205 keV). Total: {ti['total_flux']:.3g} ph/cm²/s.

| SNR | l (deg) | b (deg) | Flux (ph/cm²/s) | Spectrum | Centroid (keV) |
|---|---|---|---|---|---|
{ti_rows}

The DC4 models of {ti_replaced} are not used (the known SNRs other than Cas A were below the detection threshold in the DC4 analysis). Cas A is the DC4 model, reused (`CasAG16distribution`). The template files and the script are in `scripts/ti44/`.

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

**Spectra.** Same spectral model as in DC4 (10 Band, 1 power law). Band parameters are drawn from the Fermi GBM 10-year spectral catalog (Poolakkil et al. 2021, fluence spectra): long bursts α ~ N(−0.84, 0.35) in [−1.5, −0.3], log Epeak ~ N(log 144 keV, 0.38 dex) in [60, 1200] keV; the short burst bn080802386 α ~ N(−0.46, 0.45), log Epeak ~ N(log 413 keV, 0.35 dex); β ~ N(−2.3, 0.3) in [−3.2, −1.95]. The power-law index of bn100612726 follows the high-energy slope distribution, N(2.3, 0.25) in [1.9, 2.9], because COSI only sees the spectrum above 100 keV. cosima's `Band` keyword takes E0 = Epeak/(2+α), not Epeak, and requires E0 above the 100 keV lower bound of the spectrum: the source files give E0, and where E0 would have been lower, Epeak was drawn again from the same distribution ({redrawn}). cosima also reads the value in the DC3/DC4 files as E0, so the DC4 Epeaks in the table are (2+α)·E0.

**Polarization.** The DC4 polarization fractions are spread uniformly between 0 and 0.9 ({', '.join(f'{x:.1f}' for x in pf4)}). The DC5 fractions are drawn from the same distribution, stratified uniform on [0, 0.9] ({', '.join(f'{x:.2f}' for x in pf5)}). Angles are uniform in [0, 180) deg.

**MEGAlib simulation inputs (Request 7).** MEGAlib has trouble simulating short bursts at large times, so every GRB and magnetar-burst directory holds inputs in times relative to its own **t_ref**, the first orientation row kept for the burst (at or just before its start; given in `sim_time_reference.txt`). The bursts then start within the first second. cosima finds the next photon time in a sloped light-curve bin by solving a quadratic in absolute time (ns); at large times the solution falls on a coarse grid, and a bright burst then emits photon after photon at the same time without advancing (bn090424592 at t − 1835487300 s, for example):
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

## Particle events for the ACS (Request 13)

New in DC5, from the COSI GRB group: magnetospheric particle events, to test transient classification on the ACS (BGO shield) light curves. The blind dataset has the default population of **local electron events** (`LOCLPAR`, quasi-trapped electrons hitting the spacecraft): {pe_place['args']['local_per_day']:g} per day over the {pe_place['rate_days']:.2f}-day orbit, i.e. {pe_place['args']['local_per_day'] * pe_place['rate_days']:.1f} expected; the Poisson draw (seed {pe_place['seed']}) gave {len(pe)}. Distant events (bremsstrahlung from precipitating electrons) are only in the enriched set. The ACS background covers the first week only, so the events are placed on days {pe_place['args']['window_days'][0] + 1:g}–{pe_place['args']['window_days'][1] + 1:g}, as the GRBs are.

| Event | Day | Start (unix s) | Duration (s) | E0 (keV) | Peak I(>30 keV) (e/cm²/s/sr) | Expected peak ACS gamma (cps) | Rocking (deg) | Yaw (deg; change during the event) |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(pe_rows)}

**Placement.** Each event starts at a random time in the window and must end, with a 5 min margin, before {gd['t_end_max']:.1f}. Required: livetime > 0 (no SAA) from 5 min before to 5 min after the event, no slew (one rocking state), a yaw change of at most 20° during the event, and at least 1 h from every GRB, magnetar burst and other event.

**Attitude.** The sources are defined in the detector frame (no `Orientation` line), so each event is built for the mean rocking angle and yaw over its time, read from the orientation file. The yaw (angle of detector +x from north toward east, about the pointing axis) swings by ~150° every orbit and passes yaw 0 at up to ~0.6°/s, so long events are only placed where the yaw changes by ≤ 20° (directions within ~10° of the true ones); they do not start during the fast swing. The GRB group's detector frame was left-handed (its +y pointed east at yaw 0); MEGAlib's is right-handed (+y west at yaw 0). This is fixed in the vendored generator. Its directions agree with the orientation file to 0.02°.

**Simulation.** The events are in the src_list and are run in the automation's `acs` mode: one Cosima run per event with `PreTriggerMode EveryEventWithHits`, which keeps events with hits only in the BGO shields; its `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` in the pipeline config, every event is also simulated with the standard trigger criteria through the full Compton chain, so it is in the germanium data too. Each event directory holds the inputs in times relative to its own t_ref (`sim_time_reference.txt`), made from the 1 s orientation file like the GRB inputs (`DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth.ori`; an excerpt of its rows around the events gives the same files). The placement and attitude use the 15 s file with livetime, whose rows are identical to the 1 s ones at the same times.

**Truth catalog and enriched set.** `sources/ParticleEvents/events.csv` lists every event with its parameters. `sources/ParticleEvents_enriched/` holds an enriched set that is not part of the blind dataset: the first week at 10× the default rates (local and distant events), with as many events as fit ({len(pe_enr)} of the {pe_enr_place['drawn']} drawn; names start with `E_`). See `sources/ParticleEvents/README.md` and `scripts/particle_events/`.

## Light-curve bugs — what needs to be re-simulated
From the [bug report](https://github.com/cositools/cosi-data-challenges/blob/develop/README.md#bug-report):

- **Time-chunk normalisation bug:** nova_co (all three components), 3C454p3 (low/high), 4C21p35 (flare/no flare), PSRB1259, MAXIJ1820, MAXIJ1348. In DC5, 3C454p3, PSRB1259 and nova_co keep their DC4 models and are re-simulated from DC5 copies whose only change is the Flux keyword (see below; for the nova, the Hernanz 2014 model). 4C21p35 and MAXIJ1820 are modified, so they are simulated anyway. MAXIJ1348 is removed. Any light-curve source simulated in time chunks must use the corrected normalisation.
- **Period bug:** 1RXSJ170849 and magnetar2 (both modified in DC5). Their light curves repeat periodically, but the DC4 files covered a non-whole number of rotations (235528.7 periods over 30 days and 109913.4 over 7 days), so the pulse phase jumped at every repeat. The DC5 copies are cut at 235528 and 109913 whole periods, ending on the phase-0 value (`scripts/fix_magnetar_lightcurves.py`). The time-averaged light curve stays at 1.000000, so the Flux keyword is unchanged in meaning.
- **Not affected:** the Crab (all components), LS5039 and PSRJ1846 (simulated by splitting the flux), and all GRBs and magnetar bursts (no splitting).
- **Repeating light curves in t − t_ref:** the repeating sources of the DC4 and DC5 sets (the Crab, LS5039, 1RXSJ170849, magnetar2, PSRB1509, and PSRJ1846 in DC4) have a `sim_time_reference.txt` with t_ref = 1835487300.0: they are simulated with the orientation file in t − t_ref, and t_ref is added back to the simulated times. Their light curves hold one cycle starting at 0 and are used as they are, so the first cycle starts at t_ref, as in DC4. MEGAlib counts the repeats of a light curve with a 32-bit integer (`MFunction::FindX`), which overflows at absolute times for periods below ~0.9 s.

## Light-curve fluxes
MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the `Flux` keyword must be the time-averaged flux over that range (as the bug report states). Every DC5 component with a light curve was checked against its README, spectrum file and the literature (`scripts/fix_lightcurve_fluxes.py`, results in `lc_flux_check.json`). Where the DC3/DC4 value was the flux while the source is on (on/off light curves) or the peak flux (nova), the DC5 file has `Flux` = that flux × the light-curve mean, so the intended flux at every time is unchanged. The changed `Flux` lines carry a comment with the calculation. **CHECK** marks values that could not be settled from the README or the literature; they are left unchanged for review.

| Source | Component | Verdict | Flux (ph/cm2/s) | Basis |
|---|---|---|---|---|
{lc_table}

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
- **LMC_511, M31_511, Virgo_511:** the DC4 definitions were simulated outside cosi-sim and differ from the DC3 `*_Gaussian_511` files. Virgo_511 (reused) is simulated from the DC3 library model `DC3/sources/511/Virgo_Gaussian_511` (2.7° Gaussian at (l, b) = (284°, 74°), 511 keV line, 4.63e-7 ph/cm²/s). LMC_511 and M31_511 (modified) are replaced by the alternative DC3 Gaussian definitions plus a small additional change, documented in their READMEs.
- Several DC4 maps and light curves are stored as `.dat.gz` in cosi-sim (thin-disk maps, magnetar light curves, including the copies in DC5/sources/Galactic/1RXSJ170849 and magnetar2), and so are the beam files of the local particle events. As for DC4, gunzip them in place before running the pipeline. All other DC5 files are used as-is.
- Science-team inputs (due Nov 15) will be added as a follow-up to this directory.
"""
open(os.path.join(ROOT, "README.md"), "w").write(txt)
print("README written", len(txt.splitlines()), "lines")
