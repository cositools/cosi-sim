# E_DISTPAR0066 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/E_DISTPAR0066`

| Parameter | Value |
|---|---|
| Class | DISTPAR (distant bremsstrahlung) |
| Start / end (unix s) | 1835930666.579 / 1835930696.579 |
| Duration (s), light-curve shape | 30, fred |
| E0 (keV) | 100 |
| Peak precipitating flux (e/cm²/s, 300×300 km²) | 2900000.0 |
| Peak photon flux at COSI (ph/cm²/s) | 10.45 |
| Earth-central angle, limb azimuth from north (deg) | 10, 180 |
| Detector zenith, azimuth (deg) | 97.65, 243.63 |
| Rocking angle (deg, + = north) | -21.88 |
| Yaw (deg; change during the event) | 63.63 (2.47) |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 2000.0 |
| GRB-group template with the same parameters | `DistantBrems_E0100_L2_C10_Az180_T30_RS` |

## Model

Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a `FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file: the mean rocking angle and yaw over the event (the yaw changes by at most 20° during it).

## Simulation

The automation runs it in `acs` mode: one Cosima run with `PreTriggerMode EveryEventWithHits`, which keeps events with hits only in the BGO shields; its `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard trigger criteria through the full Compton chain.

The light curve is stored in times relative to **t_ref = 1835930666.0** (`*_lightcurve_shifted.dat`; the original with absolute times is kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
