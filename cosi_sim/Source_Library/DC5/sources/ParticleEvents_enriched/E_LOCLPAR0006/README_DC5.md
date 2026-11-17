# E_LOCLPAR0006 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/E_LOCLPAR0006`

| Parameter | Value |
|---|---|
| Class | LOCLPAR (local electrons) |
| Start / end (unix s) | 1835529885.156 / 1835529945.156 |
| Duration (s), light-curve shape | 60, crossing |
| E0 (keV) | 30 |
| Peak I(>30 keV) at 90° pitch (e/cm²/s/sr) | 3500.0 |
| Pitch-angle distribution | sin^4 |
| Rocking angle (deg, + = north) | -21.88 |
| Yaw (deg; change during the event) | -65.51 (1.01) |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 80.0 |
| GRB-group template with the same parameters | `LocalElectrons_E030_L0_T60_RS` |

## Model

Quasi-trapped electrons hitting the spacecraft (ParticleType 3): dN/dE ∝ exp(−E/E0) from 50 keV to 10 MeV, a sin^4 pitch-angle distribution about a horizontal northward magnetic field (magnetic equator), written as a `FarFieldNormalizedEnergyBeamFluxFunction` beam over (φ, θ, energy) in the detector frame (`*_beam.dat.gz`; gunzip it before using `Setup.setup_srcs()` by hand, the automation does this). The light curve is a smooth sin² pass (the spacecraft crossing a drifting enhancement).

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file: the mean rocking angle and yaw over the event (the yaw changes by at most 20° during it).

## Simulation

The automation runs it in `acs` mode: one Cosima run with `PreTriggerMode EveryEventWithHits`, which keeps events with hits only in the BGO shields; its `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard trigger criteria through the full Compton chain.

The light curve is stored in times relative to **t_ref = 1835529885.0** (`*_lightcurve_shifted.dat`; the original with absolute times is kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
