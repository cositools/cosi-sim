# R1_LOCLPAR0016 — DC5 particle event

**DC5 status:** new: particle event for the ACS, from the COSI GRB group (enriched set, realization 1; not part of the blind dataset)  
**Source:** select it in inputs.yaml as `DC5/sources/ParticleEvents_enriched/R1_LOCLPAR0016`

| Parameter | Value |
|---|---|
| Class | LOCLPAR (local electrons) |
| Start / end (unix s) | 1835654954.267 / 1835655554.267 |
| Duration (s), light-curve shape | 600, crossing |
| E0 (keV) | 50 |
| Peak I(>30 keV) at 90° pitch (e/cm²/s/sr) | 780.0 |
| Pitch-angle distribution | sin^4 |
| Rocking angle (deg, + = north) | 21.88 |
| Yaw start → end (deg) | 43.86 → 61.37 |
| Source components (pieces) | 2 |
| Expected brightest-panel peak ACS gamma rate (cps, pilot) | 80.0 |
| GRB-group template with the same parameters | `LocalElectrons_E050_L0_T600_RN` |

## Model

Quasi-trapped electrons hitting the spacecraft (ParticleType 3): dN/dE ∝ exp(−E/E0) from 50 keV to 10 MeV, a sin^4 pitch-angle distribution about a horizontal northward magnetic field (magnetic equator), written as a `FarFieldNormalizedEnergyBeamFluxFunction` beam over (φ, θ, energy) in the detector frame (`*_beam.dat.gz`; gunzip it before using `Setup.setup_srcs()` by hand, the automation does this). The light curve is a smooth sin² pass (the spacecraft crossing a drifting enhancement).

All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the event time from the DC5 orientation file. The yaw changes during the event, so it is split into 2 consecutive pieces (components `R1_LOCLPAR0016_p1` …), each built at the attitude of its time span (yaw change ≤ 10° per piece) with its part of the light curve and its mean intensity; together they make up the event.

## Simulation

The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also simulated with the standard geometry through the full Compton chain.

The light curves are stored in times relative to **t_ref = 1835654940.0** (`*_lightcurve_shifted.dat`; the originals with absolute times are kept), with `*_cut_normed.ori`, the orientation rows covering the event in t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.

Population, placement and generation: `DC5/sources/ParticleEvents_enriched/README.md` and `DC5/scripts/particle_events/`.
