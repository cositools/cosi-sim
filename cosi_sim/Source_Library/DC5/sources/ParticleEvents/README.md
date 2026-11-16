# DC5 particle events (blind dataset)

Magnetospheric particle events from the COSI GRB group, for testing transient classification on the ACS (BGO shield) light curves. This directory is the set in the blind DC5 dataset; `../ParticleEvents_enriched/` is a larger set outside it.

## Population

- **Local electron events only** (`LOCLPAR`: quasi-trapped electrons hitting the spacecraft). Distant events (bremsstrahlung from precipitating electrons) are only in the enriched set.
- **Rate:** the GRB group's default, 0.1 per day over the 92.36-day orbit (9.2 expected). The number is a Poisson draw; the seed is in `placement.json`.
- **Parameters:** drawn from the GRB group's template grid with their weights: E0 = 30, 50, 100, 200, 500 keV (weights 0.35, 0.30, 0.20, 0.10, 0.05); three brightness levels aimed at brightest-panel peak ACS gamma rates of 80, 400 and 2000 counts/s (weights falling by 3 per level); durations 60, 300 and 600 s.
- **Times:** the ACS background covers only the first week, so the events are placed in days 4–8 (3–7 days after the orientation start), like the GRBs. Each event:
  - starts at a random time and ends, with a 5 min margin, before 1836092100.0;
  - has livetime > 0 (no SAA) from 5 min before to 5 min after it;
  - has no slew (one rocking state), and the yaw changes by at most 20° during it (see below);
  - is at least 1 h from every DC5 GRB, magnetar burst and other event.

## Attitude

The sources are in the detector frame (no `Orientation` line), and a source keeps one direction for the whole event. Each event is built for the mean rocking angle (±21.9°) and yaw (angle of detector +x from north toward east) over its time, read from the orientation file.

The yaw swings by ~150° every orbit and passes yaw 0 at up to ~0.6°/s. Events are therefore only placed where the yaw changes by at most 20°, so their directions are within ~10° of the true ones. Every event is simulated in full; long events just do not start during the fast swing through yaw 0. Short events can start almost any time.

The detector frame is MEGAlib's: right-handed, with +y = z × x, which points west at yaw 0. The axes built for an event agree with the orientation file to 0.02° outside slews.

## Files

- `events.csv`: the truth catalog, tab-separated, one row per event. Columns:
  - start and end time (unix s, the clock of the orientation file);
  - class, species, light-curve duration and shape, E0;
  - peak I(>30 keV) (local) or peak precipitating and photon flux (distant);
  - pitch-angle model; Earth-central angle and limb azimuth (distant);
  - detector zenith and azimuth (distant);
  - rocking angle, yaw, and the yaw change during the event;
  - expected brightest-panel peak ACS gamma rate (from the GRB group's pilot at north rock, yaw 0);
  - the GRB-group template with the same parameters.
- `placement.json`: the seed, arguments and constraints of the draw.
- `<event>/`: one cosi-sim source per event.
  - `<event>.source` and the beam files (`*_beam.dat.gz`) or spectrum files.
  - Light curves: the originals in absolute time, plus `*_shifted.dat` in t − t_ref.
  - `*_cut.ori` and `*_cut_normed.ori`, and `sim_time_reference.txt` (each event has its own t_ref, from the 15 s orientation file).
  - `README_DC5.md`.

## Simulation

The events are in `DC5_mock_dataset_src_list.txt`. The automation (`cosi_sim/automation`) runs sources under `ParticleEvents*` in `acs` mode:

- One Cosima run per event with the BGO-readout geometry (`bgo_geometry_file` in the pipeline config, `COSISMEX.sim_BGOreading.geo.setup`).
- Its `.sim.gz` file, with absolute times, goes to `<products_dir>/ACS/ParticleEvents/`. It is the input for the ACS light curves.
- With `particle_germanium: true` in the pipeline config, each event is also simulated with the standard geometry through the full Compton chain, so it is in the germanium data too. For DC5 this is on.

## Regenerating

From `cosi_sim/Source_Library/DC5`:

```bash
python scripts/particle_events/place_events.py \
    --ori DC4_final_530km_3_month_with_slew_15sbins_GalacticEarth_SAA.ori \
    --sim-ori DC3_final_530km_3_month_with_slew_15sbins_GalacticEarth.ori \
    --out sources/ParticleEvents --window-days 3 7 --local-per-day 0.1 --distant-per-day 0 \
    --avoid-bursts sources/GRBs/* --seed <seed from placement.json>
```

- `--ori` is the 10-column orientation file with livetime. It gives the attitude and the SAA.
- `--sim-ori` is the 9-column file used for the MEGAlib runs (the same rows).
- Without `--seed` the draw is new. Afterwards, regenerate the enriched set (see its README), then run `write_manifest.py` and `write_dc5_readme.py`, and update `master_source_list.txt`.
