"""ACS pilot: simulate each template at constant (lightcurve-mean) flux with the DC3
mass model in BGO-readout mode, then convert to peak ACS count rates per panel and
compare with the measured ACS background.

Requires MEGAlib (source bin/source-megalib.sh) and the massmodel-cosi-dc3 repository.
"""

import argparse
import gzip
import json
import shutil
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

BGO_DETECTOR_TYPE = "8"
GAMMA_BAND = (80.0, 2000.0)
SIDE_WALL_CUT_CM = 21.0
# Median background counts per 50 ms bin from the scaled-background ACS data (gamma, proton).
BACKGROUND_50MS = {"x+": (33.3, 13.1), "x-": (32.1, 13.1), "y+": (38.0, 16.6),
                   "y-": (39.2, 17.8), "bot+": (29.7, 15.5), "bot-": (28.5, 14.3)}


def panel_of(x, y):
    if max(abs(x), abs(y)) > SIDE_WALL_CUT_CM:
        return ("x+" if x > 0 else "x-") if abs(x) >= abs(y) else ("y+" if y > 0 else "y-")
    return "bot+" if x > 0 else "bot-"


def run_template(tdir, workdir, geometry, sim_time):
    name = tdir.name
    wd = workdir / name
    if wd.exists():
        shutil.rmtree(wd)
    shutil.copytree(tdir, wd)
    body = [ln for ln in (wd / f"{name}.source").read_text().splitlines()
            if not ln.startswith(("DataChallenge.Source", f"{name}.Lightcurve"))]
    run = [f"Version 1", f"Geometry {geometry}", "PhysicsListEM LivermorePol",
           "StoreSimulationInfo init-only", "Run Pilot", "Pilot.FileName pilot",
           f"Pilot.Time {sim_time:g}", f"Pilot.Source {name}"] + body
    (wd / "pilot.source").write_text("\n".join(run) + "\n")
    with open(wd / "pilot.log", "w") as log:
        subprocess.run(["cosima", "-z", "pilot.source"], cwd=wd, stdout=log, stderr=subprocess.STDOUT, check=True)
    return wd


def analyze(wd):
    counts = defaultdict(lambda: np.zeros(2))
    t_obs, n_events = None, 0
    for sim in sorted(wd.glob("pilot*.sim.gz")):
        with gzip.open(sim, "rt") as f:
            panel_e = defaultdict(float)
            for line in f:
                if line.startswith("SE") or line.startswith("EN"):
                    for p, e in panel_e.items():
                        if GAMMA_BAND[0] <= e < GAMMA_BAND[1]:
                            counts[p][0] += 1
                        elif e >= GAMMA_BAND[1]:
                            counts[p][1] += 1
                    panel_e.clear()
                    n_events += line.startswith("SE")
                elif line.startswith("HTsim"):
                    det, rest = line[5:].split(";", 1)
                    if det.strip() == BGO_DETECTOR_TYPE:
                        v = rest.split(";")
                        panel_e[panel_of(float(v[0]), float(v[1]))] += float(v[3])
                elif line.startswith("TE"):
                    t_obs = float(line.split()[1])
    return {p: c / t_obs for p, c in counts.items()}, t_obs, n_events


def peak_over_mean(lc_file):
    t, y = [], []
    for ln in lc_file.read_text().splitlines():
        if ln.startswith("DP"):
            _, a, b = ln.split()
            t.append(float(a)); y.append(float(b))
    t, y = np.array(t), np.array(y)
    return y.max() / (np.trapezoid(y, t) / (t[-1] - t[0]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("templates", help="directory produced by make_particle_templates.py")
    p.add_argument("--workdir", default="/tmp/cosipilot")
    p.add_argument("--geometry", default=str(Path.home() / "Software/massmodel-cosi-dc3/COSISMEX.sim_BGOreading.geo.setup"))
    p.add_argument("--time", type=float, default=1e-5, help="initial simulated seconds per template")
    p.add_argument("--max-time", type=float, default=300.0, help="cap on simulated seconds per template")
    p.add_argument("--target-events", type=int, default=2000, help="triggered events to aim for")
    p.add_argument("--jobs", type=int, default=6)
    a = p.parse_args()

    tdirs = sorted(d for d in Path(a.templates).iterdir() if (d / f"{d.name}.source").exists())
    workdir = Path(a.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    def adaptive(d):
        t = a.time
        while True:
            wd = run_template(d, workdir, a.geometry, t)
            _, _, n_ev = analyze(wd)
            if n_ev >= a.target_events or t >= a.max_time:
                return wd
            t = min(a.max_time, t * min(1000.0, 1.5 * a.target_events / max(n_ev, 1)))

    with ThreadPoolExecutor(a.jobs) as ex:
        wds = list(ex.map(adaptive, tdirs))

    results = {}
    for d, wd in zip(tdirs, wds):
        rates, t_obs, n_ev = analyze(wd)
        scale = peak_over_mean(d / f"{d.name}_lightcurve.dat")
        meta = json.loads((Path(a.templates) / "templates.json").read_text())
        dur = next(r["duration_s"] for r in meta if r["template"] == d.name)
        out = {"t_sim_s": t_obs, "events": n_ev, "peak_over_mean": scale, "panels": {}}
        for panel, (bg_g, bg_p) in BACKGROUND_50MS.items():
            g, pr = rates.get(panel, np.zeros(2)) * scale
            bg_rate = bg_g / 0.05
            # Peak-rate SNR on 1.024 s, and an event-integrated SNR over the full duration
            snr_1s = g * 1.024 / np.sqrt(bg_rate * 1.024)
            snr_full = g / scale * dur / np.sqrt(bg_rate * dur)
            out["panels"][panel] = dict(peak_gamma_cps=g, peak_proton_cps=pr,
                                        bg_gamma_cps=bg_rate, bg_proton_cps=bg_p / 0.05,
                                        snr_gamma_1s=snr_1s, snr_gamma_full=snr_full)
        results[d.name] = out
        best = max(out["panels"].items(), key=lambda kv: kv[1]["snr_gamma_1s"])
        print(f"{d.name}: {n_ev} events in {t_obs:.3g} s; brightest panel {best[0]}: "
              f"peak gamma {best[1]['peak_gamma_cps']:.3g} cps (bg {best[1]['bg_gamma_cps']:.0f}), "
              f"peak proton {best[1]['peak_proton_cps']:.3g} cps, SNR 1 s {best[1]['snr_gamma_1s']:.2f}, "
              f"SNR full {best[1]['snr_gamma_full']:.2f}")
    (Path(a.templates) / "pilot_results.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
