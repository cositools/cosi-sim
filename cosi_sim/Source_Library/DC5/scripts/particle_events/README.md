# Local and distant particle events for the COSI ACS

Cosima sources for magnetospheric particle events, from the COSI GRB group, for injection into the DC5 mock data to test transient classification against the ACS (BGO shield) light curves. The placed DC5 events are in `DC5/sources/ParticleEvents/` (blind dataset) and `DC5/sources/ParticleEvents_enriched/`.

| Class | Physical picture | Cosima source |
|---|---|---|
| `LOCLPAR` | Quasi-trapped electrons hitting the spacecraft (equatorial "forbidden-zone" electrons, drift-loss-cone electrons) | `ParticleType 3`, `FarFieldNormalizedEnergyBeamFluxFunction` beam file over (phi, theta, energy) |
| `DISTPAR` | Bremsstrahlung from electrons precipitating into the atmosphere, seen just inside the Earth's limb | `ParticleType 1`, `FarFieldGaussian` patch with a spectrum file |

## Files

- `make_particle_templates.py`: the source builders (`build_local`, `build_distant`), and a template library for fixed rocking states (`python make_particle_templates.py --out <dir>`; not needed for DC5).
- `place_events.py`: draws a population, places it on the DC5 orientation, builds every event for the attitude at its time, writes one cosi-sim source directory per event and the truth catalog `events.csv`, and prepares the inputs in t − t_ref. Usage is in its docstring and in `DC5/sources/ParticleEvents/README.md`.
- `run_pilot.py`: the ACS pilot. Simulates templates with the DC3 mass model in BGO-readout mode and converts the hits to ACS gamma (80–2000 keV) and >2 MeV rates per panel.

## Conventions

- **Frame.** All directions are in the Cosima `Local` (detector) frame, so the sources carry no `Orientation` line.
  - Detector +z is the zenith tilted by the rocking angle toward geographic north (positive) or south.
  - Yaw is the angle of detector +x from the north/up plane toward east.
  - Detector +y = z × x (right-handed, as in MEGAlib's `MCOrientation`), so +y points west at yaw 0.
  - `place_events.py` reads the rocking angle and yaw from the orientation file (Earth-zenith columns and the celestial pole). The axes it builds agree with the orientation file to 0.02° outside slews.
  - DC5 rocks ±21.9°, and the yaw swings between about −74° and +74° every orbit, passing yaw 0 at up to ~0.6°/s. A detector-frame source keeps one direction for the whole event, so events are only placed where the yaw changes by ≤ 20°, and built at the mean yaw.
- **Magnetic field.** Horizontal and northward (dip 0), which is right at the magnetic equator. COSI's 0° geographic orbit crosses magnetic latitudes of about ±11°.
- **Light curves.**
  - Cosima rescales a light curve to unit mean, so each `Flux` (or beam-file intensity) is the mean over its light curve; the peak values are in the comments and the catalog.
  - Placed events have absolute times (the clock of the orientation file); the `*_shifted.dat` copies are in t − t_ref.
- **Range cuts and detector time constant** are copied from the DC3/DC4 sources.
- **ACS readout.** Run the sims with `COSISMEX.sim_BGOreading.geo.setup`, which turns the BGO vetoes into triggers so shield-only events are kept (automation: `acs` mode, `bgo_geometry_file`).

## Physics

- **Local electrons:** `dN/dE ∝ exp(−E/E0)` with E0 = 30, 50, 100, 200, 500 keV, simulated from 50 keV to 10 MeV.
  - Intensity is quoted as the peak I(>30 keV) at 90° pitch (the POES MEPED convention), with a sin⁴(pitch) angular distribution.
  - The time profile is a smooth sin² pass of 60, 300 or 600 s, mimicking the spacecraft crossing a drifting enhancement.
- **Distant bremsstrahlung:** thick-target spectrum `exp(−k/E0)/k` from an exponential electron spectrum (E0 = 100, 200, 500 keV).
  - The radiated fraction is 6e−4·Z·E for air. Half of it is emitted upward, it is absorbed below about 50 keV, and it escapes like a Lambertian surface.
  - The source is a 300×300 km patch at 10° or 18° Earth-central angle (1,270–2,140 km away, about 113–120° from zenith), at four azimuths.
  - The time profile is a FRED of 30 or 300 s. `EarthOccultation` is off, since the patch is below the horizon.

## Intensity levels from the pilot

The ACS pilot (north rock, yaw 0, DC3 mass model) measured these brightest-panel peak gamma rates. Rates scale linearly with intensity, so the grid sets three levels per spectrum (L0–L2), aimed at brightest-panel peaks of 80, 400 and 2,000 counts/s. The background is about 570–780 counts/s per panel, so L0 is about 3σ in 1 s and L2 is about 3× background. At other yaws the light spreads differently over the panels, so the catalog's expected rate is nominal.

| Local E0 | Peak cps at I(>30 keV)=1e4 | | Distant E0 | Peak cps at Q=1e4, 10° | at 18° |
|---|---|---|---|---|---|
| 30 keV | 228 | | 100 keV | 6.9 | 0.7 |
| 50 keV | 1,030 | | 200 keV | 20 | 2.2 |
| 100 keV | 6,040 | | 500 keV | 87 | 9.1 |
| 200 keV | 29,300 | | | | |
| 500 keV | 208,000 | | | | |

Local events hit mainly the two bottom panels. Only E0 = 500 keV puts counts in the >2 MeV channel.

## Caveats

- **Distant events probably can't happen at this brightness.** Visible distant events need about 10⁴–3×10⁷ e/cm²/s of precipitating electrons, which is implausible at the latitudes COSI can see from a 0° orbit. Treat `DISTPAR` as a stress test, not a population.
- **Hard, bright local events are not physical.** Forbidden-zone enhancements reach I(>30 keV) ≳ 1e5 but are soft (>100 keV electrons often don't rise). E0 ≥ 200 keV only makes sense at low intensity (inner-belt or transmitter-induced electrons), and the grid reflects that.
- **Default rates are guesses:** 0.1 local and 0.01 distant events per day, with soft spectra and low levels favored. Forbidden-zone events cluster after midnight local time, near solstices, and toward solar minimum; none of that is modeled.
- **Simplified response.** Pile-up and deadtime in the ACS are not modeled.
