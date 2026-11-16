"""Build Cosima source templates for local-electron and distant-bremsstrahlung
particle events, in cosi-sim Source_Library layout.

Local events: quasi-trapped electrons hitting the spacecraft (Cosima ParticleType 3),
pitch-angle distributed about the local magnetic field, written as a
FarFieldNormalizedEnergyBeamFluxFunction (theta, phi, energy) in the detector frame.

Distant events: atmospheric bremsstrahlung from electrons precipitating near the
limb (ParticleType 1), written as a FarFieldGaussian patch in the detector frame.

All directions are in the Cosima Local (detector) frame, one template per rocking
state. Geometry convention (see README.md): detector +z is the zenith tilted by the
rocking angle toward geographic north (north-rock, +22 deg) or south (south-rock,
-22 deg); detector +x lies in the north/up plane, rotated about +z toward east by
--yaw-deg; detector +y = z x x (right-handed, as in MEGAlib), i.e. west at yaw 0.

The builders are also used by place_events.py, which builds every DC5 event at the
rocking angle and yaw of its time.
"""

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

R_EARTH_KM = 6371.0
ALT_KM = 530.0
E_REF_KEV = 30.0          # intensities are quoted as I(>30 keV), as measured by POES MEPED
E_MIN_KEV = 50.0          # lower simulation bound; below this electrons cannot reach the ACS
E_MAX_KEV = 10000.0
Z_AIR = 7.3

# Brightest-panel peak ACS gamma rates (80-2000 keV, counts/s) from the pilot, north-rock,
# at I(>30 keV) = PILOT_I30 for local events and Q = PILOT_Q for distant events.
PILOT_I30 = 1e4
PILOT_LOCAL_CPS = {30: 228.0, 50: 1030.0, 100: 6040.0, 200: 29300.0, 500: 208000.0}
PILOT_Q = 1e4
PILOT_DISTANT_CPS = {10: {100: 6.88, 200: 20.2, 500: 86.9}, 18: {100: 0.707, 200: 2.21, 500: 9.1}}
TARGET_PEAK_CPS = [80.0, 400.0, 2000.0]

HORIZON_ZENITH_DEG = 180.0 - np.degrees(np.arcsin(R_EARTH_KM / (R_EARTH_KM + ALT_KM)))

RANGE_CUT_HEADER = """# Same range cuts as the DC3/DC4 sources (optimizes sim time):
DefaultRangeCut 0.005
Region Spacecraft
Spacecraft.Volume SCbody
Spacecraft.RangeCut 1.

Region Pipebody
Pipebody.Volume PIPbody
Pipebody.RangeCut 1.

DetectorTimeConstant 0.000002
"""


def detector_basis(rock_deg, yaw_deg):
    """Return detector x, y, z unit vectors expressed in the (North, East, Up) frame.

    Yaw is the angle of +x from the north/up plane toward east. (North, East, Up) is a
    left-handed frame, so np.cross in these components is minus the physical cross product.
    MEGAlib's detector frame is right-handed (y = z x x, MCOrientation), so at yaw 0 the
    detector +y points west.
    """
    r = np.radians(rock_deg)
    north, east, up = np.eye(3)
    z = np.cos(r) * up + np.sin(r) * north
    x0 = np.cos(r) * north - np.sin(r) * up
    y0 = np.cross(z, x0)                      # = east (the yaw direction, not the detector y)
    w = np.radians(yaw_deg)
    x = np.cos(w) * x0 + np.sin(w) * y0
    y = np.cross(x, z)                        # physical z x x in the left-handed (N, E, U) components
    return x, y, z


def to_detector_theta_phi(vec_neu, basis):
    x, y, z = basis
    v = vec_neu / np.linalg.norm(vec_neu)
    theta = np.degrees(np.arccos(np.clip(v @ z, -1, 1)))
    phi = np.degrees(np.arctan2(v @ y, v @ x)) % 360.0
    return theta, phi


def neu_direction(zenith_deg, azimuth_deg):
    """Unit vector toward a sky direction given zenith angle and azimuth (from north toward east)."""
    zr, ar = np.radians(zenith_deg), np.radians(azimuth_deg)
    return np.array([np.sin(zr) * np.cos(ar), np.sin(zr) * np.sin(ar), np.cos(zr)])


def lightcurve(shape, duration_s, n=200):
    """Unit-peak lightcurve on [0, duration]. Cosima renormalizes it to unit mean."""
    t = np.linspace(0.0, duration_s, n)
    if shape == "crossing":
        # Spacecraft crossing a drifting enhancement region: smooth symmetric pass.
        y = np.sin(np.pi * t / duration_s) ** 2
    elif shape == "fred":
        tr = 0.1 * duration_s
        y = np.where(t < tr, (t / tr) ** 2, np.exp(-(t - tr) / (0.25 * duration_s)))
    else:
        raise ValueError(shape)
    y = np.maximum(y, 1e-6)
    return t, y


def write_dp_file(path, x, y, comment):
    with open(path, "w") as f:
        f.write(f"# {comment}\nIP LIN\n")
        for a, b in zip(x, y):
            f.write(f"DP {a:.6g} {b:.6g}\n")
        f.write("EN\n")


# ---------------------------------------------------------------------------
# Local electrons
# ---------------------------------------------------------------------------

def electron_intensity(E, e0_kev, i30):
    """Differential intensity j(E) [e/cm2/s/sr/keV] at 90 deg pitch, exponential in E,
    normalized so that the integral above E_REF_KEV equals i30 [e/cm2/s/sr]."""
    return i30 / e0_kev * np.exp(-(E - E_REF_KEV) / e0_kev)


def build_local(out, name, e0_kev, i30_peak, pitch_n, rock_deg, yaw_deg, dip_deg,
                shape, duration_s):
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    basis = detector_basis(rock_deg, yaw_deg)
    # Field direction: horizontal northward at the magnetic equator, dipping by dip_deg.
    b_neu = np.array([np.cos(np.radians(dip_deg)), 0.0, -np.sin(np.radians(dip_deg))])
    x, y, z = basis
    b_det = np.array([b_neu @ x, b_neu @ y, b_neu @ z])

    t, lc = lightcurve(shape, duration_s)
    mean_over_peak = np.trapezoid(lc, t) / duration_s

    phi_ax = np.linspace(0, 360, 37)
    th_ax = np.linspace(0, 180, 19)
    e_ax = np.geomspace(E_MIN_KEV, E_MAX_KEV, 21)
    lines = []
    for k, E in enumerate(e_ax):
        jE = electron_intensity(E, e0_kev, i30_peak) * mean_over_peak
        for j, th in enumerate(th_ax):
            for i, ph in enumerate(phi_ax):
                tr, pr = np.radians(th), np.radians(ph)
                src = np.array([np.sin(tr) * np.cos(pr), np.sin(tr) * np.sin(pr), np.cos(tr)])
                # Particle velocity is -src; sin(pitch) is the same for +/- directions.
                sin_a = np.sqrt(max(0.0, 1.0 - (src @ b_det) ** 2))
                lines.append(f"AP {i} {j} {k} {jE * sin_a ** pitch_n:.6g}\n")
    beam = f"{name}_beam.dat"
    with open(d / beam, "w") as f:
        f.write("# Electron intensity [e/cm2/s/sr/keV], event-averaged; phi/theta in detector frame\n")
        f.write("PA " + " ".join(f"{v:g}" for v in phi_ax) + "\n")
        f.write("TA " + " ".join(f"{v:g}" for v in th_ax) + "\n")
        f.write("EA " + " ".join(f"{v:.6g}" for v in e_ax) + "\n")
        f.write("IP LIN\n")
        f.writelines(lines)
        f.write("EN\n")
    lcf = f"{name}_lightcurve.dat"
    write_dp_file(d / lcf, t, lc, "Relative time [s] vs unit-peak rate; shift to absolute time when placing")

    with open(d / f"{name}.source", "w") as f:
        f.write(RANGE_CUT_HEADER)
        f.write(f"""
# Local particle event: quasi-trapped electrons, exp(-E/{e0_kev:g} keV),
# peak I(>{E_REF_KEV:g} keV) = {i30_peak:.3g} e/cm2/s/sr at 90 deg pitch, sin^{pitch_n} pitch-angle distribution.
# Rocking {rock_deg:+g} deg, yaw {yaw_deg:g} deg, field dip {dip_deg:g} deg. Directions in detector frame.
DataChallenge.Source {name}
{name}.ParticleType 3
{name}.Beam FarFieldNormalizedEnergyBeamFluxFunction {beam}
{name}.Spectrum NormalizedEnergyBeamFluxFunction
{name}.Lightcurve File false {lcf}
""")
    return dict(event_class="LOCLPAR", species="electron", template=name, e0_kev=e0_kev,
                i30_peak=i30_peak, pitch_model=f"sin^{pitch_n}", rock_deg=rock_deg,
                yaw_deg=yaw_deg, dip_deg=dip_deg, shape=shape, duration_s=duration_s)


# ---------------------------------------------------------------------------
# Distant bremsstrahlung
# ---------------------------------------------------------------------------

def brems_photons_per_electron(e0_kev, k_cut_kev=50.0):
    """Approximate escaping (upward) photon spectrum per precipitating electron.

    Thick-target Kramers spectrum for an exponential electron spectrum gives
    dN/dk ~ exp(-k/E0)/k. It is normalized to the radiated energy fraction
    Y(E) = 6e-4 Z E / (1 + 6e-4 Z E) (E in MeV), half is emitted upward, and
    photons below ~k_cut are absorbed in the overlying atmosphere.
    Returns (k grid [keV], dN/dk per electron above E_MIN_KEV [1/keV])."""
    E = np.geomspace(E_MIN_KEV, E_MAX_KEV, 400)
    w = np.exp(-E / e0_kev)
    w /= np.trapezoid(w, E)
    y_rad = 6e-4 * Z_AIR * (E / 1e3) / (1 + 6e-4 * Z_AIR * (E / 1e3))
    e_rad = np.trapezoid(w * y_rad * E, E)

    k = np.geomspace(E_MIN_KEV, E_MAX_KEV, 200)
    shape = np.exp(-k / e0_kev) / k
    norm = e_rad / np.trapezoid(shape * k, k)
    escape = 1.0 - np.exp(-(k / k_cut_kev) ** 3)
    return k, 0.5 * norm * shape * escape


def build_distant(out, name, e0_kev, q_peak, area_km2, central_deg, az_deg, rock_deg,
                  yaw_deg, shape, duration_s):
    """q_peak: precipitating electron number flux above E_MIN_KEV [e/cm2/s] over area_km2."""
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    basis = detector_basis(rock_deg, yaw_deg)

    # Geometry of a patch at Earth-central angle `central_deg` from the sub-satellite point.
    rs = R_EARTH_KM + ALT_KM
    c = np.radians(central_deg)
    patch = R_EARTH_KM * np.array([np.sin(c), 0.0, np.cos(c)])
    sat = np.array([0.0, 0.0, rs])
    los = patch - sat
    dist_km = np.linalg.norm(los)
    zenith = np.degrees(np.arccos(los[2] / dist_km))
    if zenith < HORIZON_ZENITH_DEG:
        raise ValueError("patch is beyond the horizon")
    emission_cos = (-los / dist_km) @ (patch / R_EARTH_KM)
    theta, phi = to_detector_theta_phi(neu_direction(zenith, az_deg), basis)
    sigma_deg = np.degrees(np.sqrt(area_km2) / dist_km) / 2.0

    k, dndk = brems_photons_per_electron(e0_kev)
    n_ph = np.trapezoid(dndk, k)
    # Lambertian escape: dN/dOmega = Phi_e * A * n_ph * cos(emission) / pi.
    flux_peak = q_peak * area_km2 * 1e10 * n_ph * emission_cos / (np.pi * (dist_km * 1e5) ** 2)

    t, lc = lightcurve(shape, duration_s)
    flux_mean = flux_peak * np.trapezoid(lc, t) / duration_s

    spf, lcf = f"{name}_spectrum.dat", f"{name}_lightcurve.dat"
    write_dp_file(d / spf, k, dndk / dndk.max(), "Photon energy [keV] vs relative dN/dE")
    write_dp_file(d / lcf, t, lc, "Relative time [s] vs unit-peak rate; shift to absolute time when placing")
    with open(d / f"{name}.source", "w") as f:
        f.write(RANGE_CUT_HEADER)
        f.write(f"""
# Distant particle event: bremsstrahlung from electrons (exp(-E/{e0_kev:g} keV)) precipitating
# over {area_km2:g} km2 at {central_deg:g} deg Earth-central angle ({dist_km:.0f} km away, zenith {zenith:.1f} deg,
# azimuth {az_deg:g} deg from north). Peak precipitating flux {q_peak:.3g} e/cm2/s above {E_MIN_KEV:g} keV.
# Peak photon flux at COSI {flux_peak:.3g} ph/cm2/s; Flux below is the lightcurve-averaged value.
# Rocking {rock_deg:+g} deg, yaw {yaw_deg:g} deg. Direction in detector frame.
DataChallenge.Source {name}
{name}.ParticleType 1
{name}.Beam FarFieldGaussian {theta:.3f} {phi:.3f} {sigma_deg:.3f}
{name}.Spectrum File {spf}
{name}.Flux {flux_mean:.6g}
{name}.Lightcurve File false {lcf}
{name}.EarthOccultation false
""")
    return dict(event_class="DISTPAR", species="photon", template=name, e0_kev=e0_kev,
                q_peak=q_peak, area_km2=area_km2, central_deg=central_deg, az_deg=az_deg,
                dist_km=round(dist_km, 1), zenith_deg=round(zenith, 2), theta_det=round(theta, 2),
                phi_det=round(phi, 2), peak_flux=flux_peak, rock_deg=rock_deg, yaw_deg=yaw_deg,
                shape=shape, duration_s=duration_s)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=str(Path(__file__).parent / "templates"))
    p.add_argument("--yaw-deg", type=float, default=0.0)
    p.add_argument("--dip-deg", type=float, default=0.0)
    p.add_argument("--pilot", action="store_true", help="Small grid for the ACS pilot")
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    rocks = {"N": 22.0, "S": -22.0}
    if a.pilot:
        local_grid = dict(e0=[30, 50, 100, 200, 500], i30=[1e4], dur=[300])
        dist_grid = dict(e0=[100, 200, 500], q=[1e4], central=[10, 18], az=[90], dur=[120])
        rocks = {"N": 22.0}
    else:
        # Intensities are set from the ACS pilot (pilot_results.json) so that the brightest
        # panel peaks at TARGET_PEAK_CPS; rates scale linearly with intensity.
        local_grid = dict(e0=list(PILOT_LOCAL_CPS), level=range(len(TARGET_PEAK_CPS)), dur=[60, 300, 600])
        dist_grid = dict(e0=list(PILOT_DISTANT_CPS[10]), level=range(len(TARGET_PEAK_CPS)),
                         central=[10, 18], az=[0, 90, 180, 270], dur=[30, 300])

    rows = []
    if a.pilot:
        for (rk, rv), e0, i30, dur in itertools.product(rocks.items(), *local_grid.values()):
            name = f"LocalElectrons_E0{e0}_I{i30:.0e}_T{dur}_R{rk}".replace("+", "")
            rows.append(build_local(out, name, e0, i30, 4, rv, a.yaw_deg, a.dip_deg, "crossing", dur))
        for (rk, rv), e0, q, cen, az, dur in itertools.product(rocks.items(), *dist_grid.values()):
            name = f"DistantBrems_E0{e0}_Q{q:.0e}_C{cen}_Az{az}_T{dur}_R{rk}".replace("+", "")
            rows.append(build_distant(out, name, e0, q, 300.0 ** 2, cen, az, rv, a.yaw_deg, "fred", dur))
    else:
        for (rk, rv), e0, lv, dur in itertools.product(rocks.items(), *local_grid.values()):
            i30 = float(f"{PILOT_I30 * TARGET_PEAK_CPS[lv] / PILOT_LOCAL_CPS[e0]:.2g}")
            name = f"LocalElectrons_E0{e0}_L{lv}_T{dur}_R{rk}"
            row = build_local(out, name, e0, i30, 4, rv, a.yaw_deg, a.dip_deg, "crossing", dur)
            rows.append(dict(row, level=lv, expected_peak_cps=TARGET_PEAK_CPS[lv]))
        for (rk, rv), e0, lv, cen, az, dur in itertools.product(rocks.items(), *dist_grid.values()):
            q = float(f"{PILOT_Q * TARGET_PEAK_CPS[lv] / PILOT_DISTANT_CPS[cen][e0]:.2g}")
            name = f"DistantBrems_E0{e0}_L{lv}_C{cen}_Az{az}_T{dur}_R{rk}"
            row = build_distant(out, name, e0, q, 300.0 ** 2, cen, az, rv, a.yaw_deg, "fred", dur)
            rows.append(dict(row, level=lv, expected_peak_cps=TARGET_PEAK_CPS[lv]))

    with open(out / "templates.json", "w") as f:
        json.dump(rows, f, indent=1)
    print(f"Wrote {len(rows)} templates to {out}")


if __name__ == "__main__":
    main()
