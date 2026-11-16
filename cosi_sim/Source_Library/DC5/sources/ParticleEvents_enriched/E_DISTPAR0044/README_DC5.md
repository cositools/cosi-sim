# E_DISTPAR0044 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/E_DISTPAR0044`

| Parameter | Value |
|---|---|
| Class | DISTPAR (distant bremsstrahlung) |
| Start / end (unix s) | 1835752315.416 / 1835752345.416 |
| Duration (s), light-curve shape | 30, fred |
| E0 (keV) | 500 |
| Peak precipitating flux (e/cm²/s, 300×300 km²) | 9200.0 |
| Peak photon flux at COSI (ph/cm²/s) | 0.2546 |
| Earth-central angle, limb azimuth from north (deg) | 10, 270 |
| Detector zenith, azimuth (deg) | 117.22, 62.61 |
| Rocking angle (deg, + = north) | -21.88 |
| Yaw (deg; change during the event) | -39.31 (9.84) |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 80.0 |
| GRB-group template with the same parameters | `DistantBrems_E0500_L0_C10_Az270_T30_RS` |

## Model

Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a `FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file: the mean rocking angle and yaw over the event (the yaw changes by at most 20° during it).

## Simulation

The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard geometry through the full Compton chain.

The light curve is stored in times relative to **t_ref = 1835752305.0** (`*_lightcurve_shifted.dat`; the original with absolute times is kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
