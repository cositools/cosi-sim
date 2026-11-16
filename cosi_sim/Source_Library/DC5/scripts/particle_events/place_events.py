"""Draw a population of local and distant particle events, place it on the DC5 orientation,
and write one cosi-sim source directory per event plus the truth catalog events.csv.

Each event is built for the spacecraft attitude at its time: the rocking angle (sign and
size) and the yaw (angle of detector +x from the north/up plane toward east) are read from
the orientation file, and the beam (local events) or source direction (distant events) is
computed in the detector frame for them (make_particle_templates.py). The event parameters
(E0, brightness level, duration, and for distant events the Earth-central angle and limb
azimuth) are drawn from the grid and weights of the GRB-group template library.

A detector-frame source keeps one direction for the whole event, so an event is only placed
where the attitude is steady. An event is accepted only if
  * it starts and ends inside the window, with LIVE_MARGIN_S to spare before the window end;
  * the livetime is > 0 (no SAA) from LIVE_MARGIN_S before to LIVE_MARGIN_S after it;
  * the spacecraft is in one rocking state during it (no slew), and the yaw changes by at most
    YAW_TOL_DEG; the event is built at the mean yaw, so its directions are within about
    YAW_TOL_DEG / 2 of the true ones. (The yaw swings by ~150 deg every orbit and passes yaw 0
    at up to ~0.6 deg/s, so long events do not start during that swing.)
  * it is at least SPACING_S from every burst, every other event, and every event of the
    catalogs given with --avoid-events.

Usage (DC5, see DC5/sources/ParticleEvents/README.md):

    python place_events.py --ori <15 s orientation file with livetime> \\
        --sim-ori <orientation file for the Cosima runs> --out <dir> --window-days 3 7 \\
        --local-per-day 0.1 --distant-per-day 0 [--enriched] \\
        [--avoid-bursts <burst dirs>] [--avoid-events <events.csv>] [--seed S]

The rates are per day of the full orientation file (--rate-days, default its length), and the
expected count is placed in the window. Events that do not fit (the window is full) are left
out, and their number is recorded in placement.json. With --sim-ori, every event directory is
prepared for simulations in times relative to its own t_ref (cosi_sim.pipeline.time_reference).
Running it again with the same seed gives the same files.
"""

import argparse
import csv
import gzip
import json
import os
import re
import secrets
import shutil
import sys
from itertools import product
from pathlib import Path

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.append(os.path.abspath(os.path.join(HERE, *[os.pardir] * 5)))   # cosi-sim repo (if not installed)
import make_particle_templates as mpt  # noqa: E402
from ori_tools import load_ori, unit  # noqa: E402

LOCAL_E0_WEIGHTS = {30: 0.35, 50: 0.30, 100: 0.20, 200: 0.10, 500: 0.05}
LOCAL_DURATIONS = [60, 300, 600]
DISTANT_GRID = dict(e0=[100, 200, 500], central=[10, 18], az=[0, 90, 180, 270], dur=[30, 300])
LEVEL_FALLOFF = 3.0
PITCH_N, DIP_DEG, AREA_KM2 = 4, 0.0, 300.0 ** 2

SPACING_S = 3600.0        # minimum gap between an event and any burst or other event
LIVE_MARGIN_S = 300.0     # livetime > 0 this long before and after an event
ROCK_TOL_DEG = 0.1        # |rocking angle| within this of the nominal value: not slewing
YAW_TOL_DEG = 20.0        # maximum yaw change during an event
MAX_TRIES = 20000
NCP_GALACTIC = (122.93191857, 27.12825120)    # celestial north pole (l, b), deg
EVENT_DIR = re.compile(r"^(E_)?(LOCLPAR|DISTPAR)\d{4}$")


class Attitude:
    """Rocking angle, yaw and livetime at each row of an orientation file with livetime.

    Rocking angle: angle of detector +z from the zenith (Earth-zenith columns) toward
    geographic north (positive) or south. Yaw: angle of detector +x from the north/up
    plane toward east, as in make_particle_templates.detector_basis().
    """

    def __init__(self, path):
        ori = load_ori(path)
        self.t, self.live = ori["t"], ori["live"]
        x, z, up = unit(ori["xl"], ori["xb"]), unit(ori["zl"], ori["zb"]), unit(ori["el"], ori["eb"])
        dot = lambda a, b: np.sum(a * b, axis=1)  # noqa: E731
        pole = unit(*NCP_GALACTIC)
        north = pole - dot(up, pole[None])[:, None] * up
        north /= np.linalg.norm(north, axis=1)[:, None]
        self.rock = np.degrees(np.arctan2(dot(z, north), dot(z, up)))
        x0 = north - dot(north, z)[:, None] * z
        x0 /= np.linalg.norm(x0, axis=1)[:, None]
        yaw = np.degrees(np.arctan2(dot(x, np.cross(x0, z)), dot(x, x0)))
        self.yaw_unwrapped = np.degrees(np.unwrap(np.radians(yaw)))
        self.rock_nominal = float(np.median(np.abs(self.rock)))

    def rows(self, ta, tb):
        """Indices of the rows covering [ta, tb] (the row at or before ta to the row at or after tb)."""
        i0 = max(int(np.searchsorted(self.t, ta, side="right")) - 1, 0)
        i1 = min(int(np.searchsorted(self.t, tb, side="left")), len(self.t) - 1)
        return slice(i0, i1 + 1)

    def live_ok(self, ta, tb):
        return bool(np.all(self.live[self.rows(ta - LIVE_MARGIN_S, tb + LIVE_MARGIN_S)] > 0))

    def yaw_samples(self, ta, tb):
        """Yaw (deg, unwrapped) every second over [ta, tb], interpolated between the rows."""
        return np.interp(np.linspace(ta, tb, int(tb - ta) + 2), self.t, self.yaw_unwrapped)

    def steady(self, ta, tb):
        """One rocking state (no slew) and a yaw change <= YAW_TOL_DEG over [ta, tb]."""
        rock = self.rock[self.rows(ta, tb)]
        return bool(np.all(np.abs(np.abs(rock) - self.rock_nominal) < ROCK_TOL_DEG) and len(set(np.sign(rock))) == 1
                    and np.ptp(self.yaw_samples(ta, tb)) <= YAW_TOL_DEG)

    def mean(self, ta, tb):
        """Mean rocking angle and yaw (deg) over [ta, tb], and the yaw change."""
        yaw = self.yaw_samples(ta, tb)
        return (float(np.mean(self.rock[self.rows(ta, tb)])), float((np.mean(yaw) + 180.0) % 360.0 - 180.0),
                float(np.ptp(yaw)))


def burst_windows(dirs):
    windows = []
    for d in dirs:
        ref = {}
        for line in open(os.path.join(d, "sim_time_reference.txt")):
            s = line.split()
            if len(s) == 2 and not s[0].startswith("#"):
                ref[s[0]] = s[1]
        windows.append((float(ref["burst_start_absolute"]), float(ref["burst_end_absolute"])))
    return windows


def catalog_windows(paths):
    windows = []
    for path in paths:
        with open(path) as f:
            for r in csv.DictReader(f, delimiter="\t"):
                windows.append((float(r["Start time (s)"]), float(r["End time (s)"])))
    return windows


def local_grid():
    rows = []
    for e0, lv, dur in product(LOCAL_E0_WEIGHTS, range(len(mpt.TARGET_PEAK_CPS)), LOCAL_DURATIONS):
        i30 = float(f"{mpt.PILOT_I30 * mpt.TARGET_PEAK_CPS[lv] / mpt.PILOT_LOCAL_CPS[e0]:.2g}")
        rows.append(dict(cls="LOCLPAR", e0=e0, level=lv, dur=dur, i30=i30,
                         weight=LOCAL_E0_WEIGHTS[e0] * LEVEL_FALLOFF ** -lv))
    return rows


def distant_grid():
    rows = []
    for e0, lv, cen, az, dur in product(DISTANT_GRID["e0"], range(len(mpt.TARGET_PEAK_CPS)),
                                        DISTANT_GRID["central"], DISTANT_GRID["az"], DISTANT_GRID["dur"]):
        q = float(f"{mpt.PILOT_Q * mpt.TARGET_PEAK_CPS[lv] / mpt.PILOT_DISTANT_CPS[cen][e0]:.2g}")
        rows.append(dict(cls="DISTPAR", e0=e0, level=lv, central=cen, az=az, dur=dur, q=q,
                         weight=LEVEL_FALLOFF ** -lv))
    return rows


def pick(rng, rows):
    w = np.array([r["weight"] for r in rows])
    return dict(rows[rng.choice(len(rows), p=w / w.sum())])


def place_time(rng, ev, att, t_lo, t_hi, taken):
    """Random start time (ms precision) satisfying all constraints, or None."""
    dur = ev["dur"]
    for _ in range(MAX_TRIES):
        t0 = round(float(rng.uniform(t_lo, t_hi - LIVE_MARGIN_S - dur)), 3)
        t1 = t0 + dur
        if any(t0 < b + SPACING_S and a < t1 + SPACING_S for a, b in taken):
            continue
        if att.live_ok(t0, t1) and att.steady(t0, t1):
            return t0
    return None


def shift_lightcurve(path, t0):
    lines = []
    for ln in path.read_text().splitlines():
        if ln.startswith("# Relative time"):
            ln = "# Time [s] (same clock as the orientation file) vs unit-peak rate"
        elif ln.startswith("DP"):
            _, t, v = ln.split()
            ln = f"DP {t0 + float(t):.6f} {v}"
        lines.append(ln)
    path.write_text("\n".join(lines) + "\n")


def build(out, ev):
    """Write the event directory; returns the catalog row."""
    name, t0, dur, rk = ev["name"], ev["t0"], ev["dur"], "N" if ev["rock"] > 0 else "S"
    if ev["cls"] == "LOCLPAR":
        row = mpt.build_local(out, name, ev["e0"], ev["i30"], PITCH_N, ev["rock"], ev["yaw"], DIP_DEG,
                              "crossing", dur)
        template = f"LocalElectrons_E0{ev['e0']}_L{ev['level']}_T{dur}_R{rk}"
        beam = out / name / f"{name}_beam.dat"           # 0.3 MB; stored gzipped like other library files
        with open(beam, "rb") as fin, gzip.GzipFile(str(beam) + ".gz", "wb", mtime=0) as fout:
            shutil.copyfileobj(fin, fout)
        beam.unlink()
    else:
        row = mpt.build_distant(out, name, ev["e0"], ev["q"], AREA_KM2, ev["central"], ev["az"], ev["rock"],
                                ev["yaw"], "fred", dur)
        template = f"DistantBrems_E0{ev['e0']}_L{ev['level']}_C{ev['central']}_Az{ev['az']}_T{dur}_R{rk}"
    shift_lightcurve(out / name / f"{name}_lightcurve.dat", t0)
    return {
        "Event": name, "Class": ev["cls"], "Species": row["species"],
        "Start time (s)": f"{t0:.3f}", "End time (s)": f"{t0 + dur:.3f}",
        "Lightcurve duration (s)": dur, "Lightcurve shape": row["shape"], "E0 (keV)": ev["e0"],
        "Peak I(>30 keV) (e/cm^2/s/sr)": row.get("i30_peak", ""),
        "Peak precipitating flux (e/cm^2/s)": row.get("q_peak", ""),
        "Peak photon flux (ph/cm^2/s)": f"{row['peak_flux']:.4g}" if "peak_flux" in row else "",
        "Pitch-angle model": row.get("pitch_model", ""),
        "Earth-central angle (deg)": row.get("central_deg", ""),
        "Limb azimuth (deg)": row.get("az_deg", ""),
        "Zenith (deg)": row.get("theta_det", ""), "Azimuth (deg)": row.get("phi_det", ""),
        "Rocking (deg)": ev["rock"], "Yaw (deg)": ev["yaw"], "Yaw change (deg)": ev["yaw_change"],
        "Expected peak ACS gamma (cps)": mpt.TARGET_PEAK_CPS[ev["level"]],
        "Template": template,
    }


def write_readme(d, r, blind):
    """README_DC5.md of one event, from its catalog row (and sim_time_reference.txt if present)."""
    name, local = r["Event"], r["Class"] == "LOCLPAR"
    category = d.parent.name
    where = "blind dataset" if blind else "enriched set; not part of the blind dataset"
    rows = [("Class", f"{r['Class']} ({'local electrons' if local else 'distant bremsstrahlung'})"),
            ("Start / end (unix s)", f"{r['Start time (s)']} / {r['End time (s)']}"),
            ("Duration (s), light-curve shape", f"{r['Lightcurve duration (s)']}, {r['Lightcurve shape']}"),
            ("E0 (keV)", r["E0 (keV)"])]
    if local:
        rows += [("Peak I(>30 keV) at 90° pitch (e/cm²/s/sr)", r["Peak I(>30 keV) (e/cm^2/s/sr)"]),
                 ("Pitch-angle distribution", r["Pitch-angle model"])]
    else:
        rows += [("Peak precipitating flux (e/cm²/s, 300×300 km²)", r["Peak precipitating flux (e/cm^2/s)"]),
                 ("Peak photon flux at COSI (ph/cm²/s)", r["Peak photon flux (ph/cm^2/s)"]),
                 ("Earth-central angle, limb azimuth from north (deg)", f"{r['Earth-central angle (deg)']}, {r['Limb azimuth (deg)']}"),
                 ("Detector zenith, azimuth (deg)", f"{r['Zenith (deg)']}, {r['Azimuth (deg)']}")]
    rows += [("Rocking angle (deg, + = north)", r["Rocking (deg)"]),
             ("Yaw (deg; change during the event)", f"{r['Yaw (deg)']} ({r['Yaw change (deg)']})"),
             ("Expected brightest-panel peak ACS gamma rate (cps, pilot)", r["Expected peak ACS gamma (cps)"]),
             ("GRB-group template with the same parameters", f"`{r['Template']}`")]
    if local:
        model = (f"Quasi-trapped electrons hitting the spacecraft (ParticleType 3): dN/dE ∝ exp(−E/E0) from 50 keV to 10 MeV, "
                 f"a {r['Pitch-angle model']} pitch-angle distribution about a horizontal northward magnetic field (magnetic "
                 f"equator), written as a `FarFieldNormalizedEnergyBeamFluxFunction` beam over (φ, θ, energy) in the detector "
                 f"frame (`*_beam.dat.gz`; gunzip it before using `Setup.setup_srcs()` by hand, the automation does this). "
                 f"The light curve is a smooth sin² pass (the spacecraft crossing a drifting enhancement).")
    else:
        model = ("Bremsstrahlung from electrons precipitating into the atmosphere just inside the Earth's limb (ParticleType 1): "
                 "a thick-target spectrum exp(−k/E0)/k (`*_spectrum.dat`) from a 300×300 km patch, written as a "
                 "`FarFieldGaussian` in the detector frame, with a fast-rise exponential-decay light curve. `EarthOccultation` "
                 "is off, since the patch is below the horizon. The GRB group considers events this bright unlikely: a stress test.")
    ref = d / "sim_time_reference.txt"
    sim = ""
    if ref.exists():
        t_ref = [ln.split()[1] for ln in ref.read_text().splitlines() if ln.startswith("t_ref")][0]
        sim = (f"\nThe light curve is stored in times relative to **t_ref = {t_ref}** (`*_lightcurve_shifted.dat`; the "
               f"original with absolute times is kept), with `*_cut_normed.ori`, the orientation rows covering the event in "
               f"t − t_ref; see `sim_time_reference.txt`. The automation adds t_ref back to the simulated times.\n")
    text = (f"# {name} — DC5 particle event\n\n"
            f"**DC5 status:** new: particle event for the ACS, from the COSI GRB group ({where})  \n"
            f"**Source:** select it in inputs.yaml as `DC5/sources/{category}/{name}`\n\n"
            f"| Parameter | Value |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in rows) +
            f"\n## Model\n\n{model}\n\n"
            f"All directions are in the detector frame (no `Orientation` line), built for the spacecraft attitude at the "
            f"event time from the DC5 orientation file: the mean rocking angle and yaw over the event (the yaw changes by "
            f"at most {YAW_TOL_DEG:g}° during it).\n\n"
            f"## Simulation\n\n"
            f"The automation runs it in `acs` mode: one Cosima run with the BGO-readout geometry (`bgo_geometry_file`), "
            f"whose `.sim.gz` file is the input for the ACS light curves. With `particle_germanium: true` it is also "
            f"simulated with the standard geometry through the full Compton chain.\n{sim}\n"
            f"Population, placement and generation: `DC5/sources/{category}/README.md` and `DC5/scripts/particle_events/`.\n")
    (d / "README_DC5.md").write_text(text)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ori", required=True, help="orientation file with livetime (10 columns, 15 s)")
    p.add_argument("--sim-ori", help="orientation file for the Cosima runs; prepares the t_ref inputs")
    p.add_argument("--out", required=True)
    p.add_argument("--window-days", type=float, nargs=2, required=True,
                   help="placement window, days after the first orientation time")
    p.add_argument("--local-per-day", type=float, default=0.1)
    p.add_argument("--distant-per-day", type=float, default=0.01)
    p.add_argument("--rate-days", type=float, default=None, help="days the rates apply to (default: the orientation file)")
    p.add_argument("--enriched", action="store_true",
                   help="enriched set (not in the blind dataset): event names start with E_")
    p.add_argument("--avoid-bursts", nargs="*", default=[], help="burst directories with sim_time_reference.txt")
    p.add_argument("--avoid-events", nargs="*", default=[], help="events.csv of other event sets")
    p.add_argument("--seed", type=int, default=None)
    a = p.parse_args(argv)

    seed = a.seed if a.seed is not None else secrets.randbits(32)
    rng = np.random.default_rng(seed)
    att = Attitude(a.ori)
    t_lo = max(att.t[0] + a.window_days[0] * 86400, att.t[0] + LIVE_MARGIN_S)
    t_hi = att.t[0] + a.window_days[1] * 86400
    rate_days = a.rate_days or (att.t[-1] - att.t[0]) / 86400
    grids = {"LOCLPAR": local_grid(), "DISTPAR": distant_grid()}
    rates = {"LOCLPAR": a.local_per_day, "DISTPAR": a.distant_per_day}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for d in out.iterdir():                              # rerun: replace the earlier events
        if d.is_dir() and EVENT_DIR.match(d.name):
            shutil.rmtree(d)

    # Draw the population, then place it in random order; events that no longer fit are left out.
    events = []
    for cls, rate in rates.items():
        events += [pick(rng, grids[cls]) for _ in range(rng.poisson(rate * rate_days))]
    events = [events[i] for i in rng.permutation(len(events))]
    taken = burst_windows(a.avoid_bursts) + catalog_windows(a.avoid_events)
    placed, left_out = [], []
    for ev in events:
        ev["t0"] = place_time(rng, ev, att, t_lo, t_hi, taken)
        if ev["t0"] is None:
            left_out.append(f"{ev['cls']} {ev['dur']} s")
            continue
        taken.append((ev["t0"], ev["t0"] + ev["dur"]))
        rock, yaw, change = att.mean(ev["t0"], ev["t0"] + ev["dur"])
        ev["rock"], ev["yaw"], ev["yaw_change"] = round(rock, 2), round(yaw, 2), round(change, 2)
        placed.append(ev)

    catalog = []
    for n, ev in enumerate(sorted(placed, key=lambda e: e["t0"])):
        ev["name"] = f"{'E_' if a.enriched else ''}{ev['cls']}{n:04d}"
        catalog.append(build(out, ev))

    fields = list(catalog[0]) if catalog else ["Event"]
    with open(out / "events.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        wr.writeheader()
        wr.writerows(catalog)
    args = dict(vars(a), ori=os.path.basename(a.ori), sim_ori=a.sim_ori and os.path.basename(a.sim_ori),
                avoid_bursts=[os.path.basename(os.path.normpath(d)) for d in a.avoid_bursts],
                avoid_events=[os.path.relpath(f, a.out) for f in a.avoid_events], seed=seed)
    del args["out"]
    record = dict(seed=seed, args=args, rate_days=rate_days, window=[t_lo, t_hi],
                  rock_nominal_deg=att.rock_nominal, spacing_s=SPACING_S, live_margin_s=LIVE_MARGIN_S,
                  rock_tol_deg=ROCK_TOL_DEG, yaw_tol_deg=YAW_TOL_DEG, drawn=len(events),
                  counts={cls: sum(1 for r in catalog if r["Class"] == cls) for cls in rates},
                  left_out=left_out)
    (out / "placement.json").write_text(json.dumps(record, indent=1) + "\n")

    if a.sim_ori:
        from cosi_sim.pipeline.time_reference import normalize_source
        for r in catalog:
            normalize_source(str(out / r["Event"]), a.sim_ori)
    for r in catalog:
        write_readme(out / r["Event"], r, blind=not a.enriched)
    print(f"Drew {len(events)} events, placed {len(catalog)} ({record['counts']}), {len(left_out)} did not fit; "
          f"days {a.window_days[0]:g}-{a.window_days[1]:g} after the orientation start, seed {seed}: {out}")


if __name__ == "__main__":
    main()
