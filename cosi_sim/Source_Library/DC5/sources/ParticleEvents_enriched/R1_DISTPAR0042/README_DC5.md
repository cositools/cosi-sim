# R1_DISTPAR0042 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set, realization 1; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/R1_DISTPAR0042`

| Parameter | Value |
|---|---|
| Class | DISTPAR (distant bremsstrahlung) |
| Start / end (unix s) | 1835912676.263 / 1835912706.263 |
| Duration (s), light-curve shape | 30, fred |
| E0 (keV) | 100 |
| Peak precipitating flux (e/cm²/s, 300×300 km²) | 5700000.0 |
| Peak photon flux at COSI (ph/cm²/s) | 1.945 |
| Earth-central angle, limb azimuth from north (deg) | 18, 180 |
| Detector zenith, azimuth start → end (deg) | 135.03, 218.85 → 218.85 |
| Rocking angle (deg, + = north) | 21.88 |
| Yaw start → end (deg) | 38.17 → 39.52 |
| Source components (pieces) | 1 |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 400.0 |
| GRB-group template with the same parameters | `DistantBrems_E0100_L1_C18_Az180_T30_RN` |

## Model

Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a `FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file. The yaw changes by less than 10° during the event, so it is one component.

## Simulation

The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard geometry through the full Compton chain.

The light curves are stored in times relative to **t_ref = 1835912670.0** (`*_lightcurve_shifted.dat`; the originals with absolute times are kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
