# E_DISTPAR0011 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/E_DISTPAR0011`

| Parameter | Value |
|---|---|
| Class | DISTPAR (distant bremsstrahlung) |
| Start / end (unix s) | 1835561636.703 / 1835561666.703 |
| Duration (s), light-curve shape | 30, fred |
| E0 (keV) | 500 |
| Peak precipitating flux (e/cm²/s, 300×300 km²) | 88000.0 |
| Peak photon flux at COSI (ph/cm²/s) | 0.2306 |
| Earth-central angle, limb azimuth from north (deg) | 18, 0 |
| Detector zenith, azimuth (deg) | 91.27, 331.78 |
| Rocking angle (deg, + = north) | 21.88 |
| Yaw (deg; change during the event) | -28.22 (1.66) |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 80.0 |
| GRB-group template with the same parameters | `DistantBrems_E0500_L0_C18_Az0_T30_RN` |

## Model

Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a `FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file: the mean rocking angle and yaw over the event (the yaw changes by at most 20° during it).

## Simulation

The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard geometry through the full Compton chain.

The light curve is stored in times relative to **t_ref = 1835561625.0** (`*_lightcurve_shifted.dat`; the original with absolute times is kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
