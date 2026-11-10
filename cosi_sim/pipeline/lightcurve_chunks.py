"""
Time chunks for sources with light curves that do not repeat.

MEGAlib rescales a light curve so that its mean over the light curve's own time range is 1,
so the Flux keyword is the time-averaged flux over the light curve. When a source is split
into time chunks, each chunk therefore needs its own light curve (cut to the chunk) and its
own flux:

    Flux_chunk = Flux * (light-curve mean over the chunk) / (light-curve mean over the whole curve)

The chunk boundaries are chosen so that every chunk has the same expected number of photons
(summed over the components of the source), so the jobs take about the same time, and times
without emission get no chunk. Components without a light curve (steady) are given a flat
light curve over the chunk, so they also emit only inside it.

For each chunk this writes into <out_dir>:
    GalacticScan.ori              orientation rows covering the chunk (plus one row on each side)
    Sources/<source>.source       the source file with the chunk fluxes and light curves
    Sources/<light curve>         the light curve of each component cut to the chunk

The written orientation rows and light curves can be shifted to times t - t_shift. MEGAlib finds
the next emission time inside a light-curve bin with a quadratic in the absolute time, which
loses precision at unix times (~1.8e9 s) when photons arrive quickly; in t - t_ref it does not.
Add t_shift back to the simulated times afterwards (Simulate.modify_sim_times).
"""

import os
import re

import numpy as np

LIGHTCURVE = re.compile(r"^\s*(\S+)\.Lightcurve\s+File\s+(\S+)\s+(\S+)")
FLUX = re.compile(r"^(\s*)(\S+)\.Flux(\s+)(\S+)(.*)$")
NO_EMISSION_FLUX = 1e-30    # MEGAlib needs Flux > 0; with an all-zero light curve nothing is emitted


class LightCurveError(ValueError):
    pass


def read_points(path):
    x, y = [], []
    with open(path) as f:
        for line in f:
            s = line.split()
            if s[:1] == ["DP"]:
                x.append(float(s[1]))
                y.append(float(s[2]))
    if len(x) < 2:
        raise LightCurveError("%s has fewer than 2 DP lines" % path)
    return np.array(x), np.array(y)


class Curve:
    """Linear interpolation of a light curve, with its exact running integral."""

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.cum = np.concatenate([[0.0], np.cumsum(np.diff(x) * (y[1:] + y[:-1]) / 2)])
        self.mean = self.cum[-1] / (x[-1] - x[0])

    def value(self, t):
        return np.interp(t, self.x, self.y)

    def integral_to(self, t):
        """Integral from the first point to t (exact for the linear interpolation)."""
        t = np.clip(np.asarray(t, dtype=float), self.x[0], self.x[-1])
        i = np.clip(np.searchsorted(self.x, t, side="right") - 1, 0, len(self.x) - 2)
        return self.cum[i] + (t - self.x[i]) * (self.y[i] + self.value(t)) / 2


def components(source_file, lc_dir):
    """{name: {"flux": F, "lightcurve": path or None}} for the components with a Flux keyword."""
    comps = {}
    with open(source_file) as f:
        lines = [l for l in f if not l.lstrip().startswith("#")]
    for line in lines:
        m = FLUX.match(line.rstrip("\n"))
        if m:
            comps.setdefault(m.group(2), {})["flux"] = float(m.group(4))
    for line in lines:
        m = LIGHTCURVE.match(line)
        if m and m.group(1) in comps:
            if m.group(2).lower() == "true":
                raise LightCurveError("%s: repeating light curve; time chunks only handle light curves "
                                      "that do not repeat (use flux chunks)" % m.group(1))
            path = m.group(3) if os.path.isabs(m.group(3)) else os.path.join(lc_dir, m.group(3))
            comps[m.group(1)]["lightcurve"] = path
    for c in comps.values():
        c.setdefault("lightcurve", None)
    if not comps:
        raise LightCurveError("no .Flux keyword in %s" % source_file)
    return comps


def chunk_bounds(comps, curves, t0, t1, num_chunks):
    """Boundaries of num_chunks chunks with equal expected photons inside [t0, t1]."""
    grid = [np.array([t0, t1])] + [c.x[(c.x > t0) & (c.x < t1)] for c in curves.values()]
    grid = np.unique(np.concatenate(grid))

    def weight(t):              # expected photons per unit area from t0 to t
        w = np.zeros_like(np.asarray(t, dtype=float))
        for name, c in comps.items():
            if name in curves:
                cv = curves[name]
                w = w + c["flux"] / cv.mean * (cv.integral_to(t) - cv.integral_to(t0))
            else:
                w = w + c["flux"] * (np.asarray(t) - t0)
        return w

    wg = weight(grid)
    total = wg[-1]
    if total <= 0:
        raise LightCurveError("no emission inside the orientation file")
    start = grid[np.flatnonzero(wg > 0)[0] - 1] if wg[0] == 0 else t0      # first emission
    stop = grid[np.flatnonzero(wg >= total)[0]]                             # last emission
    targets = total * np.arange(1, num_chunks) / num_chunks
    hi = np.searchsorted(wg, targets)               # first grid point with weight >= target
    lo_t, hi_t = grid[hi - 1], grid[hi]
    for _ in range(60):                             # bisection with the exact weight
        mid = (lo_t + hi_t) / 2
        below = weight(mid) < targets
        lo_t, hi_t = np.where(below, mid, lo_t), np.where(below, hi_t, mid)
    bounds = np.unique(np.concatenate([[start], hi_t, [stop]]))
    return bounds, total


def cut_curve(curve, a, b):
    inside = (curve.x > a) & (curve.x < b)
    x = np.concatenate([[a], curve.x[inside], [b]])
    return x, curve.value(x)


def orientation_rows(ori_file):
    with open(ori_file) as f:
        lines = f.readlines()
    rows = [k for k, l in enumerate(lines) if l.split()[:1] in (["OG"], ["OR"])]
    if not rows:
        raise LightCurveError("no orientation rows in %s" % ori_file)
    times = np.array([float(lines[k].split()[1]) for k in rows])
    return lines, rows, times


def write_chunks(source_file, lc_dir, ori_file, num_chunks, out_dirs, t_shift=0.0):
    """Write the files of each chunk; out_dirs(k) gives the directory of chunk k.

    Times in the orientation file and light curves are in the same frame; the written chunk
    files are in times t - t_shift.

    Returns a summary dict: number of chunks, emission window, flux per component per chunk.
    """
    comps = components(source_file, lc_dir)
    curves = {n: Curve(*read_points(c["lightcurve"])) for n, c in comps.items() if c["lightcurve"]}
    if not curves:
        raise LightCurveError("%s has no light curve" % source_file)
    lines, rows, times = orientation_rows(ori_file)
    t0, t1 = times[0], times[-1]
    for n, cv in curves.items():
        if cv.x[0] > t0 + 1e-3 or cv.x[-1] < t1 - 1e-3:
            raise LightCurveError("%s: light curve [%.3f, %.3f] does not cover the orientation file [%.3f, %.3f]"
                                  % (n, cv.x[0], cv.x[-1], t0, t1))
    bounds, total = chunk_bounds(comps, curves, t0, t1, num_chunks)
    header = lines[:rows[0]]
    footer = lines[rows[-1] + 1:] or ["EN\n"]
    text = open(source_file).read()
    fluxes = {n: [] for n in comps}
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        d = out_dirs(k)
        os.makedirs(os.path.join(d, "Sources"), exist_ok=True)
        # Orientation rows covering [a, b]:
        i0 = max(0, np.searchsorted(times, a, side="right") - 1)
        i1 = min(len(times) - 1, np.searchsorted(times, b, side="left"))
        chunk_rows = []
        for i in range(i0, i1 + 1):
            tok = lines[rows[i]].split()
            chunk_rows.append("%s %.6f %s\n" % (tok[0], float(tok[1]) - t_shift, " ".join(tok[2:])))
        with open(os.path.join(d, "GalacticScan.ori"), "w") as f:
            f.writelines(header + chunk_rows + footer)
        # Light curves and fluxes:
        new = text
        for n, c in comps.items():
            if n in curves:
                cv = curves[n]
                x, y = cut_curve(cv, a, b)
                integral = cv.integral_to(b) - cv.integral_to(a)
                flux = c["flux"] * (integral / (b - a)) / cv.mean
                name = os.path.basename(c["lightcurve"])
            else:
                x, y = np.array([a, b]), np.array([1.0, 1.0])
                flux = c["flux"]
                name = "%s_flat.dat" % n
            lc_path = os.path.join(d, "Sources", name)
            with open(lc_path, "w") as f:
                f.write("IP LINLIN\n")
                f.writelines("DP %r %r\n" % (float(u) - t_shift, float(v)) for u, v in zip(x, y))
                f.write("EN\n")
            fluxes[n].append(flux)
            out_flux = flux if flux > 0 else NO_EMISSION_FLUX
            new = re.sub(r"^(\s*%s\.Flux\s+)\S+" % re.escape(n), lambda m: m.group(1) + "%.9e" % out_flux,
                         new, count=1, flags=re.M)
            if n in curves:
                new = re.sub(r"^(\s*%s\.Lightcurve\s+File\s+\S+\s+)\S+" % re.escape(n),
                             lambda m: m.group(1) + lc_path, new, count=1, flags=re.M)
            else:
                new = re.sub(r"^(\s*%s\.Flux\s+\S+.*)$" % re.escape(n),
                             lambda m: m.group(1) + "\n%s.Lightcurve File false %s" % (n, lc_path),
                             new, count=1, flags=re.M)
        with open(os.path.join(d, "Sources", os.path.basename(source_file)), "w") as f:
            f.write(new)
    return {"chunks": len(bounds) - 1, "start": float(bounds[0]), "stop": float(bounds[-1]),
            "photons_per_cm2": float(total), "fluxes": fluxes,
            "lengths": [float(v) for v in np.diff(bounds)]}
