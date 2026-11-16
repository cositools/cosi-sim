# DC5 particle events: enriched set (not in the blind dataset)

A larger set of particle events for developing and testing ACS transient classification. It is not part of the blind DC5 dataset and is not in `DC5_mock_dataset_src_list.txt`. The events are built and placed exactly as the blind set (see `../ParticleEvents/README.md`), with these differences:

- **Rates:** 10 times the defaults, 1 local and 0.1 distant event per day over the 92.36-day orbit, all placed in the first week (days 1–8, the time covered by the ACS background).
- **As many as fit.** The draw gave 91 events. They were placed in random order, and the events that no longer fit (with at least 1 h between events) were left out: 2 local events of 600 s. The set has **89 events: 80 local and 9 distant**. The seed and the events left out are in `placement.json`.
- **Spacing:** every event is at least 1 h from the other enriched events, the DC5 GRBs, the magnetar bursts and the blind-set events, so the set can be combined with the blind dataset.
- **Names** start with `E_` (e.g. `E_LOCLPAR0000`).
- **Distant events** (`DISTPAR`) are included. The GRB group notes that distant events this bright probably cannot happen at COSI's latitudes, so treat them as a stress test.
  - Parameters: E0 = 100, 200 or 500 keV; three brightness levels; Earth-central angle 10° or 18°; limb azimuth 0°, 90°, 180° or 270° from north; duration 30 or 300 s.

## Simulation

Simulate these events the same way as the blind set: `acs` mode for the ACS, and `particle_germanium: true` to add them to the germanium data. Use a separate `sim_root` and `products_dir` from the blind dataset. The ACS `.sim.gz` files go to `<products_dir>/ACS/ParticleEvents_enriched/`.

## Regenerating

From `cosi_sim/Source_Library/DC5`, after the blind set:

```bash
python scripts/particle_events/place_events.py --enriched \
    --ori DC4_final_530km_3_month_with_slew_15sbins_GalacticEarth_SAA.ori \
    --sim-ori DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth.ori \
    --out sources/ParticleEvents_enriched --window-days 0 7 --local-per-day 1 --distant-per-day 0.1 \
    --avoid-bursts sources/GRBs/* --avoid-events sources/ParticleEvents/events.csv \
    --seed <seed from placement.json>
```
