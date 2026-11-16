# R2_DISTPAR0022 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set, realization 2; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/R2_DISTPAR0022`

| Parameter | Value |
|---|---|
| Class | DISTPAR (distant bremsstrahlung) |
| Start / end (unix s) | 1835709364.110 / 1835709664.110 |
| Duration (s), light-curve shape | 300, fred |
| E0 (keV) | 500 |
| Peak precipitating flux (e/cm²/s, 300×300 km²) | 9200.0 |
| Peak photon flux at COSI (ph/cm²/s) | 0.2546 |
| Earth-central angle, limb azimuth from north (deg) | 10, 180 |
| Detector zenith, azimuth start → end (deg) | 141.41, 178.32 → 191.96 |
| Rocking angle (deg, + = north) | 21.88 |
| Yaw start → end (deg) | -5.08 → 15.33 |
| Source components (pieces) | 3 |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 80.0 |
| GRB-group template with the same parameters | `DistantBrems_E0500_L0_C10_Az180_T300_RN` |

## Model

Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a `FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file. The yaw changes during the event, so it is split into 3 consecutive pieces (components `R2_DISTPAR0022_p1` …), each built at the attitude of its time span (yaw change ≤ 10° per piece) with its part of the light curve and its mean intensity; together they make up the event.

## Simulation

The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard geometry through the full Compton chain.

The light curves are stored in times relative to **t_ref = 1835709360.0** (`*_lightcurve_shifted.dat`; the originals with absolute times are kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
