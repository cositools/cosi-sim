"""
Simulating sources in times relative to a reference time (normalized light curves).

MEGAlib has trouble with light curves at large absolute times (unix times ~1.8e9 s):
short bursts are hard to simulate, and for a repeating light curve the number of
repeats since the light-curve start is cast to a 32-bit integer (MFunction::FindX),
which overflows for periods below ~0.86 s (e.g. the Crab and other pulsars). Such
sources are therefore simulated in times t - t_ref, and t_ref is added back to the
simulated times afterwards (Simulate.modify_sim_times).

A source directory in the library that uses normalized times contains:

    sim_time_reference.txt        t_ref and how the files were made
    <light curve>_shifted.dat     bursts only: light curve in t - t_ref; the .source file
                                  points to it (the original light curve is kept)
    *_cut.ori, *_cut_normed.ori   bursts only: the orientation rows covering the burst,
                                  in absolute times and in t - t_ref

Burst light curves are shifted: every time becomes t - t_ref. Repeating light curves
(Lightcurve File true) hold one cycle starting at 0 and are used as they are: with the
orientation file in t - t_ref, the first cycle starts at t_ref.

Usage (writes the files above into library source directories):

    python -m cosi_sim.pipeline.time_reference --ori <orientation file> [--t-ref T] <source dir> ...

t_ref defaults to the first time of the orientation file.

check_lightcurves() is used by Setup.setup_srcs() and the automation: a light curve that
does not repeat must have the same start and stop times as the orientation file (or, for
bursts, lie inside it), and a repeating light curve must not repeat more than 2^31 times
before the end of the orientation file.
"""

import argparse
import gzip
import os
import re
import sys

TIME_REFERENCE_FILE = "sim_time_reference.txt"
TOLERANCE = 1e-3            # s, allowed difference between light-curve and orientation times
MAX_REPEATS = 2 ** 31 - 1   # MFunction::FindX stores the number of repeats in an int


# ---------------------------------------------------------------------------
# Reading files
# ---------------------------------------------------------------------------

def open_text(path, mode="rt"):
    return gzip.open(path, mode) if path.endswith(".gz") else open(path, mode.replace("t", ""))


def existing(path):
    """path, or path.gz if only the compressed file exists (library maps and light curves)."""
    if os.path.exists(path):
        return path
    if os.path.exists(path + ".gz"):
        return path + ".gz"
    raise FileNotFoundError(path)


def is_data(line):
    split = line.split()
    return bool(split) and split[0] == "DP"


def lightcurve_layout(lines):
    """(header, data region, footer), as in shift_times.py: the first line is a header and the last
    line a footer, unless the last line is a data point (a file without an EN footer)."""
    if len(lines) < 3:
        raise ValueError("a light curve needs at least 3 lines")
    if is_data(lines[-1]):
        return lines[:1], lines[1:], []
    return lines[:1], lines[1:-1], lines[-1:]


def lightcurve_points(path):
    """Times and values of the DP lines."""
    times, values = [], []
    with open_text(existing(path)) as f:
        for line in f:
            split = line.split()
            if split and split[0] == "DP":
                times.append(float(split[1]))
                values.append(float(split[2]))
    if len(times) < 2:
        raise ValueError("%s has fewer than 2 DP lines" % path)
    return times, values


def lightcurve_time_range(path):
    times, _ = lightcurve_points(path)
    return min(times[0], times[-1]), max(times[0], times[-1])


def orientation_time_range(path):
    """First and last time of the OG (or OR) rows, reading only the start and the end of the file."""
    def row_time(line):
        split = line.split()
        if len(split) >= 2 and split[0] in ("OG", "OR"):
            return float(split[1])
        return None

    first = None
    with open_text(path) as f:
        for line in f:
            first = row_time(line)
            if first is not None:
                break
    last = None
    if path.endswith(".gz"):
        with open_text(path) as f:
            for line in f:
                t = row_time(line)
                if t is not None:
                    last = t
    else:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size, block = f.tell(), 65536
            while last is None:
                start = max(0, size - block)
                f.seek(start)
                lines = f.read().decode("utf-8", errors="replace").splitlines()
                for line in reversed(lines[1:] if start > 0 else lines):
                    last = row_time(line)
                    if last is not None:
                        break
                if block >= size:
                    break
                block *= 4
    if first is None or last is None:
        raise ValueError("no orientation rows in %s" % path)
    return first, last


# ---------------------------------------------------------------------------
# Source files
# ---------------------------------------------------------------------------

LIGHTCURVE_LINE = re.compile(r"^(\s*(\S+)\.Lightcurve\s+File\s+(\S+)\s+)(\S+)(\s*)$")


def lightcurves(source_file):
    """[(component, repeats, file name)] for every active Lightcurve line of a .source file."""
    out = []
    with open(source_file) as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue
            m = LIGHTCURVE_LINE.match(line.rstrip("\n"))
            if m:
                out.append((m.group(2), m.group(3).lower() == "true", m.group(4)))
    return out


def read_time_reference(source_dir):
    """t_ref from sim_time_reference.txt in a source directory, or None."""
    path = os.path.join(source_dir, TIME_REFERENCE_FILE)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for line in f:
            split = line.split()
            if len(split) >= 2 and split[0] == "t_ref":
                return float(split[1])
    return None


# ---------------------------------------------------------------------------
# Check: light-curve times against the orientation file
# ---------------------------------------------------------------------------

def check_lightcurves(source_file, ori_range, burst=False, lc_dir=None):
    """Problems (list of strings) with the light curves of one source file.

    A light curve that does not repeat must start and stop at the same times as the
    orientation file used for the simulation (ori_range = (first, last)); for bursts it
    must lie inside it. A repeating light curve must not repeat more than 2^31 times
    between its start and the orientation times (otherwise MEGAlib's repeat count overflows).
    """
    lc_dir = lc_dir or os.path.dirname(os.path.abspath(source_file))
    o0, o1 = ori_range
    problems = []
    for component, repeats, name in lightcurves(source_file):
        try:
            t0, t1 = lightcurve_time_range(os.path.join(lc_dir, name))
        except (OSError, ValueError) as err:
            problems.append("%s: cannot read light curve %s (%s)" % (component, name, err))
            continue
        if repeats:
            period = t1 - t0
            repeats_needed = max(abs(o1 - t1), abs(t0 - o0)) / period if period > 0 else float("inf")
            if repeats_needed > MAX_REPEATS:
                problems.append("%s: light curve %s (period %.6g s) would repeat %.3g times to reach the "
                                "orientation times [%.3f, %.3f] s, more than MEGAlib can count (2^31); "
                                "simulate in times relative to the orientation start (see %s)"
                                % (component, name, period, repeats_needed, o0, o1, __name__))
            continue
        if burst:
            if t0 < o0 - TOLERANCE or t1 > o1 + TOLERANCE:
                problems.append("%s: light curve %s covers [%.3f, %.3f] s, outside the orientation file "
                                "[%.3f, %.3f] s" % (component, name, t0, t1, o0, o1))
        elif abs(t0 - o0) > TOLERANCE or abs(t1 - o1) > TOLERANCE:
            problems.append("%s: light curve %s covers [%.3f, %.3f] s, but the orientation file covers "
                            "[%.3f, %.3f] s; the start and stop times must match"
                            % (component, name, t0, t1, o0, o1))
    return problems


# ---------------------------------------------------------------------------
# Writing normalized files
# ---------------------------------------------------------------------------

def shifted_name(name):
    """X.dat -> X_shifted.dat (unchanged if already shifted)."""
    stem, ext = os.path.splitext(name)
    return name if stem.endswith("_shifted") else stem + "_shifted" + ext


def original_name(name):
    stem, ext = os.path.splitext(name)
    return stem[: -len("_shifted")] + ext if stem.endswith("_shifted") else name


def shift_lightcurve(lc_in, lc_out, t_ref):
    """Light curve with every time t -> t - t_ref (shift_times.py), other lines unchanged."""
    with open_text(lc_in) as f:
        header, data, footer = lightcurve_layout(f.readlines())
    with open_text(lc_out, "wt") as f:
        f.writelines(header)
        for line in data:
            s = line.strip()
            if not s or s.startswith("#"):
                f.write(line)
                continue
            split = s.split()
            if len(split) != 3:
                raise ValueError("Expected 3 columns in %s: %r" % (lc_in, line))
            f.write("%s %.6f %s\n" % (split[0], float(split[1]) - t_ref, split[2]))
        f.writelines(footer)


def write_shifted_orientation(ori_in, ori_out, t_ref):
    """Orientation file with every row time t -> t - t_ref (write_shifted_ori of cut_ori.py)."""
    with open_text(ori_in) as fin, open_text(ori_out, "wt") as fout:
        for line in fin:
            s = line.strip()
            if not s or s.startswith("#"):
                fout.write(line)
                continue
            tok = s.split()
            if len(tok) < 2 or tok[0] not in ("OG", "OR"):
                fout.write(line)
                continue
            fout.write("%s %.6f %s\n" % (tok[0], float(tok[1]) - t_ref, " ".join(tok[2:])))


def cut_orientation(ori_in, t_first, t_last, out_cut, out_norm, t_ref):
    """Orientation rows covering [t_first, t_last] (cut_ori.py): the rows inside, plus one on each side.

    A burst shorter than the orientation step has no row inside; then the two rows around it are kept.
    At least 3 rows are written. Returns (first time, last time, number of rows).
    """
    with open_text(ori_in) as f:
        lines = f.readlines()
    rows = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        tok = s.split()
        if len(tok) < 9:
            raise ValueError("Unexpected ORI row format (expected at least 9 columns): %r" % line)
        rows.append((i, float(tok[1])))
    times = [t for _, t in rows]
    inside = [k for k, t in enumerate(times) if t_first <= t <= t_last]
    if inside:
        keep = set(range(inside[0], inside[-1] + 1))
        if inside[0] > 0:
            keep.add(inside[0] - 1)
        if inside[-1] + 1 < len(times):
            keep.add(inside[-1] + 1)
    else:
        before = [k for k, t in enumerate(times) if t < t_first]
        after = [k for k, t in enumerate(times) if t > t_last]
        if not before or not after:
            raise ValueError("[%s, %s] is not inside the orientation file %s" % (t_first, t_last, ori_in))
        keep = {before[-1], after[0]}
    while len(keep) < 3:
        hi = max(keep) + 1
        keep.add(hi if hi < len(times) else min(keep) - 1)
    keep_lines = {rows[k][0] for k in keep}
    with open(out_cut, "w") as f:
        for i, line in enumerate(lines):
            s = line.strip()
            if not s or s.startswith("#") or i in keep_lines:
                f.write(line)
    write_shifted_orientation(out_cut, out_norm, t_ref)
    kept = sorted(times[k] for k in keep)
    return kept[0], kept[-1], len(kept)


NOTE = re.compile(r"^# (Light-curve times are|Simulated in times) relative to t_ref.*\n# .*\n# .*\n", re.M)


def normalize_source(source_dir, ori_file, t_ref=None):
    """Mark a source directory for simulations in t - t_ref and write the files this needs.

    Bursts: shifted light curves and cut orientation files; the .source Lightcurve lines point to
    the shifted light curves. Repeating light curves are used as they are. The .source file also
    gets a 3-line note. Running it again gives the same files.
    """
    name = os.path.basename(os.path.normpath(source_dir))
    source_file = os.path.join(source_dir, name + ".source")
    if t_ref is None:
        t_ref = orientation_time_range(ori_file)[0]
    ori_stem = os.path.splitext(os.path.basename(ori_file[:-3] if ori_file.endswith(".gz") else ori_file))[0]
    entries = lightcurves(source_file)
    if not entries:
        raise ValueError("%s has no light curve" % source_file)

    done, burst_window = [], None
    for component, repeats, lc in entries:
        orig = original_name(lc)
        src_path = existing(os.path.join(source_dir, orig))
        if repeats:
            t0, t1 = lightcurve_time_range(src_path)
            done.append((component, orig, orig, "repeating", t0, t1))
        else:
            out_name = shifted_name(orig)
            out_path = os.path.join(source_dir, out_name + (".gz" if src_path.endswith(".gz") else ""))
            shift_lightcurve(src_path, out_path, t_ref)
            t0, t1 = lightcurve_time_range(src_path)
            burst_window = (min(t0, burst_window[0]), max(t1, burst_window[1])) if burst_window else (t0, t1)
            done.append((component, orig, out_name, "shifted", t0, t1))

    ori_info = None
    if burst_window:
        o0, o1, n = cut_orientation(ori_file, burst_window[0], burst_window[1],
                                    os.path.join(source_dir, ori_stem + "_cut.ori"),
                                    os.path.join(source_dir, ori_stem + "_cut_normed.ori"), t_ref)
        ori_info = (o0, o1, n)

    # Source file: burst Lightcurve lines point to the shifted files; a note before the first one.
    text = NOTE.sub("", open(source_file).read())
    lines = text.splitlines(keepends=True)
    first = True
    for k, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        m = LIGHTCURVE_LINE.match(line.rstrip("\n"))
        if not m:
            continue
        repeating = m.group(3).lower() == "true"
        lc_name = original_name(m.group(4)) if repeating else shifted_name(original_name(m.group(4)))
        new = m.group(1) + lc_name + m.group(5) + "\n"
        if first:
            if ori_info:
                how = "Simulate with %s_cut_normed.ori and add t_ref to the simulated times afterwards." % ori_stem
                what = "Original light curve%s (absolute unix times): %s" % (
                    "s" if len(done) > 1 else "", ", ".join(d[1] for d in done))
            else:
                how = "Simulate with the orientation file in t - t_ref and add t_ref to the simulated times afterwards."
                what = "The repeating light curve starts its first cycle at t_ref"
            head = "Light-curve times are relative to" if ori_info else "Simulated in times relative to"
            new = ("# %s t_ref = %r (unix s, first time of the orientation file).\n"
                   "# %s\n"
                   "# %s; see %s.\n"
                   % (head, t_ref, how, what, TIME_REFERENCE_FILE)) + new
            first = False
        lines[k] = new
    with open(source_file, "w") as f:
        f.writelines(lines)

    # sim_time_reference.txt
    out = ["# MEGAlib simulation time reference for %s" % name, "%-26s %r" % ("t_ref", t_ref)]
    for component, orig, shifted, kind, a, b in done:
        if kind == "shifted":
            out += ["%-26s %s" % ("lightcurve_original", orig), "%-26s %s" % ("lightcurve_shifted", shifted),
                    "%-26s %.6f" % ("burst_start_absolute", a), "%-26s %.6f" % ("burst_end_absolute", b),
                    "%-26s %.6f" % ("burst_start_shifted", a - t_ref), "%-26s %.6f" % ("burst_end_shifted", b - t_ref)]
        else:
            out += ["%-26s %s" % ("lightcurve_repeating", orig), "%-26s %r" % ("repeat_period", b - a)]
    out.append("%-26s %s" % ("orientation_file", os.path.basename(ori_file)))
    if ori_info:
        o0, o1, n = ori_info
        out += ["%-26s %s" % ("orientation_cut", ori_stem + "_cut.ori"),
                "%-26s %s" % ("orientation_cut_normed", ori_stem + "_cut_normed.ori"),
                "%-26s %d" % ("orientation_rows", n),
                "%-26s %.6f" % ("orientation_start_shifted", o0 - t_ref),
                "%-26s %.6f" % ("orientation_end_shifted", o1 - t_ref)]
    else:
        out.append("# Repeating light curve(s), used as they are: simulate over the orientation file in t - t_ref.")
    out.append("# After the Cosima run, add t_ref to the simulated event times to recover the absolute times.")
    with open(os.path.join(source_dir, TIME_REFERENCE_FILE), "w") as f:
        f.write("\n".join(out) + "\n")
    return done, ori_info


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ori", required=True, help="orientation file used for the simulations")
    p.add_argument("--t-ref", type=float, default=None, help="reference time (default: first time of --ori)")
    p.add_argument("source_dirs", nargs="+", help="library source directories")
    args = p.parse_args(argv)
    t_ref = args.t_ref if args.t_ref is not None else orientation_time_range(args.ori)[0]
    for d in args.source_dirs:
        done, ori_info = normalize_source(d, args.ori, t_ref)
        what = ", ".join("%s %s" % (kind, out) for _, _, out, kind, _, _ in done)  # e.g. "shifted X_shifted.dat"
        extra = ", orientation rows %d" % ori_info[2] if ori_info else ""
        print("%-45s %s%s" % (os.path.basename(os.path.normpath(d)), what, extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
