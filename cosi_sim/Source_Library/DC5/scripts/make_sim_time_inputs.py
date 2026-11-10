"""
MEGAlib simulation inputs with normalized times for the DC5 GRBs and magnetar bursts (Request 7).

Usage: python3 make_sim_time_inputs.py <cosi-sim repo root> <orientation file>

<orientation file> is the 9-column orientation file with 1 s steps used for the DC4 GRB simulations,
DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth.ori (first time 1835487300.0); an excerpt holding
the rows around the bursts gives the same output. It has no livetime column (the SAA cut in cosipy uses
the 15 s file with livetime).

Large absolute unix times are hard for MEGAlib to simulate for short bursts, so every burst is simulated
in times relative to T_REF = 1835487300.0 (the first time of the orientation file). For each burst
directory in DC5/sources/GRBs/ this writes:

  <ori stem>_cut.ori          orientation rows covering the light curve (absolute times), at least 3 rows
  <ori stem>_cut_normed.ori   the same rows with time - T_REF (the file to give MEGAlib)
  <lc stem>_shifted.dat       the light curve with time - T_REF
  <name>.source               Lightcurve line pointing to the shifted light curve (nothing else changes)
  sim_time_reference.txt      T_REF and the absolute / shifted time windows (to shift simulated times back)

The original light curve stays in the directory for reference. The logic follows cut_ori.py and
shift_times.py (C. Karwin), with two generalisations:
  * bursts shorter than the orientation step have no orientation row inside the burst; the rows
    bracketing the burst are kept, plus more neighbours until there are at least 3 rows;
  * light-curve files without an "EN" footer (MGF180128A, MGF200415A) end with a data point, which is
    treated as data rather than as a footer line.
For bursts where cut_ori.py / shift_times.py run, the outputs are byte-identical to theirs.
Magnetar bursts that are kept unchanged (MGF*, MgtBurst*) are first copied from DC3/sources/GRBs.
"""
import os, re, sys, shutil
from pathlib import Path

T_REF = 1835487300.0
MAGNETAR_KEPT = ["MGF051103", "MGF180128A", "MGF200415A", "MgtBurst_bright_complex"]
REPO, ORI = Path(sys.argv[1]), Path(sys.argv[2])
LIB = REPO / "cosi_sim" / "Source_Library"
GRBDIR = LIB / "DC5" / "sources" / "GRBs"
ORI_STEM = ORI.stem          # DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth


def is_data(line):
    s = line.strip()
    return bool(s) and not s.startswith("#") and s.split()[0] == "DP"


def lc_layout(lines):
    """(header lines, data-region lines, footer lines) as in shift_times.py: first line is a header and the
    last line a footer, unless the last line is a data point (file without an EN footer)."""
    if len(lines) < 3:
        raise ValueError("light curve needs at least 3 lines")
    if is_data(lines[-1]):
        return lines[:1], lines[1:], []
    return lines[:1], lines[1:-1], lines[-1:]


def lc_window(path):
    _, data, _ = lc_layout(path.read_text().splitlines(keepends=True))
    t = []
    for line in data:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) != 3:
            raise ValueError(f"Expected 3 columns in {path}: {line!r}")
        t.append(float(p[1]))
    return (t[0], t[-1]) if t[0] <= t[-1] else (t[-1], t[0])


def shift_lc(path_in, path_out):
    header, data, footer = lc_layout(path_in.read_text().splitlines(keepends=True))
    with path_out.open("w") as f:
        f.writelines(header)
        for line in data:
            s = line.strip()
            if not s or s.startswith("#"):
                f.write(line); continue
            c1, t, c3 = s.split()
            f.write(f"{c1} {float(t) - T_REF:.6f} {c3}\n")
        f.writelines(footer)


ORI_LINES = ORI.read_text().splitlines(keepends=True)
ORI_ROWS = []                      # (line index, time) of data rows
for i, line in enumerate(ORI_LINES):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    tok = s.split()
    if len(tok) != 9:
        raise ValueError(f"Unexpected ORI row format (expected 9 columns): {line!r}")
    ORI_ROWS.append((i, float(tok[1])))
assert ORI_ROWS[0][1] >= T_REF, f"orientation file starts before the reference time {T_REF} ({ORI_ROWS[0][1]})"


def cut_ori(t_first, t_last, out_cut, out_norm):
    times = [t for _, t in ORI_ROWS]
    inr = [k for k, t in enumerate(times) if t_first <= t <= t_last]
    if inr:                                    # cut_ori.py: in-range rows plus one neighbour on each side
        keep = set(range(inr[0], inr[-1] + 1))
        if inr[0] - 1 >= 0: keep.add(inr[0] - 1)
        if inr[-1] + 1 < len(times): keep.add(inr[-1] + 1)
    else:                                      # burst inside one orientation step: the two bracketing rows
        before = max(k for k, t in enumerate(times) if t < t_first)
        after = min(k for k, t in enumerate(times) if t > t_last)
        keep = {before, after}
    while len(keep) < 3:                       # at least 3 orientation times
        hi = max(keep) + 1
        keep.add(hi if hi < len(times) else min(keep) - 1)
    keep_lines = {ORI_ROWS[k][0] for k in keep}
    with out_cut.open("w") as f:
        for i, line in enumerate(ORI_LINES):
            s = line.strip()
            if not s or s.startswith("#") or i in keep_lines:
                f.write(line)
    with out_cut.open() as fi, out_norm.open("w") as fo:   # write_shifted_ori() of cut_ori.py
        for line in fi:
            s = line.strip()
            if not s or s.startswith("#"):
                fo.write(line); continue
            t = s.split()
            fo.write(f"{t[0]} {float(t[1]) - T_REF:.6f} {t[2]} {t[3]} {t[4]} {t[5]} {t[6]} {t[7]} {t[8]}\n")
    kt = sorted(times[k] for k in keep)
    return kt[0], kt[-1], len(kt)


# Magnetar bursts kept unchanged: copy the DC3 directories into DC5 (source definitions unchanged)
for name in MAGNETAR_KEPT:
    d = GRBDIR / name
    if not d.exists():
        shutil.copytree(LIB / "DC3" / "sources" / "GRBs" / name, d)

for d in sorted(GRBDIR.iterdir()):
    name = d.name
    src = d / f"{name}.source"
    text = src.read_text()
    m = re.search(r"^(\s*\S+\.Lightcurve\s+File\s+\S+\s+)(\S+)(\s*)$", text, flags=re.M)
    lc_name = m.group(2)
    if lc_name.endswith("_shifted.dat"):                     # already processed: start from the original
        lc_name = lc_name[: -len("_shifted.dat")] + ".dat"
    lc = d / lc_name
    lc_shift = d / (lc.stem + "_shifted.dat")
    t_first, t_last = lc_window(lc)
    o_first, o_last, n = cut_ori(t_first, t_last, d / f"{ORI_STEM}_cut.ori", d / f"{ORI_STEM}_cut_normed.ori")
    shift_lc(lc, lc_shift)

    # source file: point to the shifted light curve, with a short note (comments only otherwise)
    note = (f"# Light-curve times are relative to t_ref = {T_REF} (unix s, first time of the orientation file).\n"
            f"# Simulate with {ORI_STEM}_cut_normed.ori and add t_ref to the simulated times afterwards.\n"
            f"# Original light curve (absolute unix times): {lc.name}; see sim_time_reference.txt.\n")
    text = re.sub(r"^# Light-curve times are relative to t_ref.*\n# .*\n# .*\n", "", text, flags=re.M)  # rerun-safe
    m = re.search(r"^(\s*\S+\.Lightcurve\s+File\s+\S+\s+)(\S+)(\s*)$", text, flags=re.M)
    text = text[: m.start()] + note + m.group(1) + lc_shift.name + m.group(3) + text[m.end():]
    src.write_text(text)

    (d / "sim_time_reference.txt").write_text(
        f"# MEGAlib simulation time reference for {name}\n"
        f"t_ref                      {T_REF}\n"
        f"lightcurve_original        {lc.name}\n"
        f"lightcurve_shifted         {lc_shift.name}\n"
        f"burst_start_absolute       {t_first:.6f}\n"
        f"burst_end_absolute         {t_last:.6f}\n"
        f"burst_start_shifted        {t_first - T_REF:.6f}\n"
        f"burst_end_shifted          {t_last - T_REF:.6f}\n"
        f"orientation_file           {ORI.name}\n"
        f"orientation_cut            {ORI_STEM}_cut.ori\n"
        f"orientation_cut_normed     {ORI_STEM}_cut_normed.ori\n"
        f"orientation_rows           {n}\n"
        f"orientation_start_shifted  {o_first - T_REF:.6f}\n"
        f"orientation_end_shifted    {o_last - T_REF:.6f}\n"
        f"# After the Cosima run, add t_ref to the simulated event times to recover the absolute times.\n")

    # README_DC5.md: add (or replace) the simulation-inputs section; magnetar bursts get a short README
    readme = d / "README_DC5.md"
    sec = (f"## MEGAlib simulation inputs (times relative to t_ref)\n\n"
           f"MEGAlib has trouble simulating short bursts at large absolute unix times, so this burst is simulated in times "
           f"relative to **t_ref = {T_REF}** (the first time of the DC4/DC5 orientation file):\n\n"
           f"- `{lc_shift.name}`: the light curve with time − t_ref; the source file points to it. "
           f"The original light curve with absolute times, `{lc.name}`, is kept for reference.\n"
           f"- `{ORI_STEM}_cut_normed.ori`: the {n} orientation rows covering the burst, time − t_ref "
           f"({o_first - T_REF:.0f}–{o_last - T_REF:.0f} s). This is the orientation file for the Cosima run. "
           f"`{ORI_STEM}_cut.ori` holds the same rows with absolute times.\n"
           f"- `sim_time_reference.txt`: t_ref and the burst window, absolute ({t_first:.3f}–{t_last:.3f}) and shifted "
           f"({t_first - T_REF:.3f}–{t_last - T_REF:.3f}).\n\n"
           f"After the Cosima run, add t_ref to the simulated event times to return to the absolute times of the "
           f"orientation file. Generated by `scripts/make_sim_time_inputs.py`.\n")
    if readme.exists():
        body = readme.read_text()
        body = re.sub(r"\n## MEGAlib simulation inputs.*?(?=\n## |\Z)", "\n", body, flags=re.S).rstrip() + "\n"
        if "\n## References" in body:
            body = body.replace("\n## References", "\n" + sec + "\n## References", 1)
        else:
            body += "\n" + sec
    else:
        body = (f"# {name} — DC5\n\n**DC5 status:** magnetar burst kept unchanged from DC4 (`DC3/sources/GRBs/{name}`); "
                f"only the simulation inputs below are new.  \n**Source:** select it in inputs.yaml as `DC5/sources/GRBs/{name}`\n\n"
                f"The spectral model, position, flux, polarization and light-curve shape are those of the DC3/DC4 definition. "
                f"Any other README in this directory describes that model.\n\n" + sec)
    readme.write_text(body)
    print(f"{name:25s} burst [{t_first - T_REF:.3f}, {t_last - T_REF:.3f}] s  ori [{o_first - T_REF:.0f}, {o_last - T_REF:.0f}] s  rows {n}")
