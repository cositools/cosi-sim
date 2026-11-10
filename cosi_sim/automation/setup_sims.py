#!/usr/bin/env python3
"""
Set up cosi-sim simulation directories for a list of library sources.

    python setup_sims.py -c pipeline_config.yaml DC5/sources/Galactic/cygX3 ...
    python setup_sims.py -c pipeline_config.yaml --list sources.txt
    python setup_sims.py -c pipeline_config.yaml --list sources.txt --dry-run

Run it in the environment where cosi_sim is installed (the MEGAlib environment).
A source list file has one library path per line, optionally followed by a mode
(time, flux or grb) to override the automatic choice; '#' starts a comment.

For each source this writes <sim_root>/<class>/<name>/ with:
    inputs.yaml, cosipy_inputs.yaml   from your templates, with the per-source keys set
    Sources/                          from Setup.setup_srcs() (= run_sim_setup.py)
    Simulations/sim_<i>/              one directory per job, as run_parallel_sims.py
    Output/<name>.inc1.id1.tra.gz     list of the per-job tra files, as run_parallel_sims.py
    run_sims.py                       cosima + revan for one job
    slurm_array_job.sh | grb_job.sh   the simulation job
    post_megalib.py, post_cosipy.py   mimrec + overflow filter; cosipy + SAA cut
    post_plots.py                     spectrum, light curve and image plots
    postprocess.sh                    runs run_pipeline.py finish
    automation.json                   settings and progress, used by run_pipeline.py

Modes (chosen automatically):
    grb   source under a GRBs/ category: one run with the time-shifted (normed)
          orientation file in the source directory.
    flux  source with a repeating light curve: num_sims parallel runs over the full
          exposure, every .Flux in the copied source file divided by num_sims (flux chunks).
    time  everything else: the exposure split into num_sims time chunks
          (cosi_sim.pipeline.make_orientation_bins, as run_parallel_sims.py).
          A light curve that does not repeat is cut into the chunks
          (cosi_sim.pipeline.lightcurve_chunks): each chunk gets its own light curve and
          flux (Flux x chunk mean / mean of the light curve), and the chunks are chosen
          with equal expected photons, so times without emission get no chunk.

Sources with normalized times (a sim_time_reference.txt in the library
directory, see cosi_sim.pipeline.time_reference) are simulated in times t - t_ref
in every mode: GRBs with their own normed orientation file, other sources with the
template orientation file shifted by t_ref (written once to <sim_root>). Each job
then adds t_ref back with modify_sim_times and runs revan on fixed_times.

A light curve that does not repeat must have the same start and stop times as the
orientation file (bursts: lie inside it), and a repeating light curve must not need more
than 2^31 repeats to reach the orientation times; otherwise the source is skipped with an error.

Then submit with:  python run_pipeline.py submit <sim_root or run dirs>
"""

import argparse
import glob
import gzip
import json
import os
import re
import shutil
import sys

import yaml

import cosi_sim
from cosi_sim.pipeline.sim_setup import Setup
from cosi_sim.pipeline.make_orientation_bins import make_bins
from cosi_sim.pipeline.lightcurve_chunks import LightCurveError, write_chunks
from cosi_sim.pipeline.time_reference import (check_lightcurves, orientation_time_range,
                                             read_time_reference, write_shifted_orientation)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_pipeline import STATE_FILE, AUTOMATION_DIR, now, load_state, save_state, POST_PLOTS_PY  # noqa: E402

LIBRARY = os.path.join(os.path.dirname(cosi_sim.__file__), "Source_Library")

REQUIRED_CONFIG = ["sim_root", "products_dir", "inputs_template", "cosipy_template",
                   "megalib_env", "cosipy_env", "revan_geometry", "overflow_filter", "num_sims"]
SLURM_DEFAULTS = {"extra_directives": [], "sim_time": "0:55:00", "sim_mem": "3G",
                  "flux_time": "0:55:00", "flux_mem": "3G", "grb_time": "2:00:00", "grb_mem": "8G",
                  "post_time": "12:00:00", "post_mem": "32G", "start_jitter": 60,
                  "array_throttle": None, "max_retries": 2, "max_jobs": None}


class SetupError(Exception):
    pass


# ---------------------------------------------------------------------------
# Config and inputs
# ---------------------------------------------------------------------------

def load_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)
    missing = [k for k in REQUIRED_CONFIG if cfg.get(k) in (None, "")]
    if missing:
        sys.exit("Config %s is missing: %s" % (path, ", ".join(missing)))
    cfg.setdefault("output_label", "{source}_3months_unbinned_data_filtered")
    cfg.setdefault("grb_output_label", "{source}_unbinned_data_filtered")
    cfg.setdefault("grb_orientation_file", None)
    cfg.setdefault("grb_time_reference", None)
    cfg.setdefault("class_map", {})
    cfg["class_map"] = cfg["class_map"] or {}
    cfg.setdefault("orchestrator_python", "python3")
    slurm = dict(SLURM_DEFAULTS)
    slurm.update(cfg.get("slurm") or {})
    cfg["slurm"] = slurm
    for key in ["sim_root", "products_dir", "inputs_template", "cosipy_template", "megalib_env",
                "cosipy_env", "revan_geometry", "overflow_filter", "grb_orientation_file"]:
        if cfg.get(key):
            cfg[key] = os.path.abspath(os.path.expanduser(cfg[key]))
    return cfg


def check_paths(cfg, template):
    """Fail early on paths that do not exist (before writing 1000 directories)."""
    problems = []
    for key in ["inputs_template", "cosipy_template", "megalib_env", "cosipy_env",
                "revan_geometry", "overflow_filter"]:
        if not os.path.exists(cfg[key]):
            problems.append("config %s: %s" % (key, cfg[key]))
    for key in ["geometry_file", "orientation_file"]:
        if not os.path.exists(str(template.get(key))):
            problems.append("inputs template %s: %s" % (key, template.get(key)))
    for key in ["revan_config", "mimrec_config"]:
        value = str(template.get(key))
        if value != "none" and not os.path.exists(value):
            problems.append("inputs template %s: %s" % (key, value))
    with open(cfg["cosipy_template"]) as f:
        ori = yaml.safe_load(f).get("ori_file")
    if not os.path.exists(str(ori)):
        problems.append("cosipy template ori_file: %s" % ori)
    if problems:
        sys.exit("These paths do not exist:\n  " + "\n  ".join(problems))
    if template.get("run_nuc"):
        sys.exit("inputs template has run_nuc: True. The nuclearizer (2016 balloon data) is not part of "
                 "this automated workflow; set run_nuc: False.")


def read_source_list(args):
    entries = [(s, None) for s in args.sources]
    if args.list:
        with open(args.list) as f:
            for line in f:
                line = line.split("#")[0].strip()
                if not line:
                    continue
                parts = line.split()
                mode = parts[1] if len(parts) > 1 else None
                entries.append((parts[0], mode))
    for src, mode in entries:
        if mode not in (None, "time", "flux", "grb"):
            sys.exit("Unknown mode '%s' for %s (use time, flux or grb)." % (mode, src))
    return [(src.strip("/"), mode) for src, mode in entries]


def yaml_value(value):
    if isinstance(value, bool):
        return "True" if value else "False"
    return json.dumps(value)      # JSON strings, numbers and lists are valid YAML


def set_yaml_keys(text, values):
    """Set top-level keys in a YAML text, keeping comments and layout."""
    for key, value in values.items():
        pattern = re.compile(r"^(%s:[ \t]*)([^#\n]*?)([ \t]*#.*)?$" % re.escape(key), re.M)
        if pattern.search(text):
            text = pattern.sub(lambda m: m.group(1) + yaml_value(value) + (m.group(3) or ""), text, count=1)
        else:
            text = text.rstrip("\n") + "\n%s: %s\n" % (key, yaml_value(value))
    loaded = yaml.load(text, Loader=yaml.FullLoader)
    for key, value in values.items():
        if loaded.get(key) != value:
            raise SetupError("could not set %s in yaml (got %r)" % (key, loaded.get(key)))
    return text


# ---------------------------------------------------------------------------
# Source inspection
# ---------------------------------------------------------------------------

def library_source_file(src):
    return os.path.join(LIBRARY, src, os.path.basename(src) + ".source")


def active_lines(path):
    with open(path) as f:
        return [l for l in f if l.strip() and not l.lstrip().startswith("#")]


def lightcurve_flags(path):
    """Repeat flags (True/False) of the active Lightcurve lines of a source file."""
    flags = []
    for line in active_lines(path):
        m = re.match(r"\s*\S+\.Lightcurve\s+File\s+(\S+)", line)
        if m:
            flags.append(m.group(1).lower() == "true")
    return flags


def detect_mode(src):
    parts = src.split("/")
    if "GRBs" in parts[:-1]:
        return "grb"
    if any(lightcurve_flags(library_source_file(src))):
        return "flux"
    return "time"


def class_name(src, cfg):
    parts = src.split("/")
    if "sources" in parts[:-1]:
        category = parts[parts.index("sources") + 1]
    else:
        category = parts[-2] if len(parts) > 1 else "Other"
    if category == os.path.basename(src):
        category = "Other"
    return cfg["class_map"].get(category, category)


def referenced_files(src):
    """Data files a library source file points to (spectra, maps, light curves)."""
    files = []
    for line in active_lines(library_source_file(src)):
        split = line.split()
        if len(split) < 3:
            continue
        if split[0].endswith(".Spectrum") and split[1] == "File":
            files.append(split[2])
        elif split[0].endswith(".Beam") and split[1] in ("FarFieldNormalizedEnergyBeamFluxFunction",
                                                         "FarFieldFileZenithDependent"):
            files.append(split[2])
        elif split[0].endswith(".Lightcurve") and len(split) >= 4:
            files.append(split[3])
    return files


def gunzip_library_files(src, dry_run=False):
    """Some library maps and light curves are stored as .dat.gz; setup_srcs needs them unzipped."""
    done = []
    for name in referenced_files(src):
        path = os.path.join(LIBRARY, src, name)
        if os.path.exists(path):
            continue
        if not os.path.exists(path + ".gz"):
            raise SetupError("library file %s does not exist" % path)
        if not dry_run:
            try:
                with gzip.open(path + ".gz", "rb") as fin, open(path, "wb") as fout:
                    shutil.copyfileobj(fin, fout)
            except OSError as err:
                raise SetupError("cannot gunzip %s.gz in the library (%s); gunzip it by hand" % (path, err))
        done.append(name)
    return done


def grb_inputs(src, cfg):
    lib_dir = os.path.join(LIBRARY, src)
    normed = sorted(glob.glob(os.path.join(lib_dir, "*_normed.ori")))
    if len(normed) == 1:
        ori = normed[0]
    elif cfg["grb_orientation_file"]:
        ori = cfg["grb_orientation_file"]
    else:
        raise SetupError("no *_normed.ori in %s and no grb_orientation_file in the config" % lib_dir)
    t_ref = read_time_reference(lib_dir)
    if t_ref is None:
        t_ref = cfg["grb_time_reference"]
    if t_ref is None:
        raise SetupError("no t_ref in %s/sim_time_reference.txt and no grb_time_reference in the config" % lib_dir)
    return ori, float(t_ref)


def normed_orientation(template_ori, t_ref, sim_root, dry_run=False):
    """The template orientation file shifted by t_ref, shared by all normalized sources of a sim_root."""
    stem = os.path.splitext(os.path.basename(template_ori))[0]
    tag = "%d" % t_ref if t_ref == int(t_ref) else repr(t_ref)
    path = os.path.join(sim_root, "%s_normed_%s.ori" % (stem, tag))
    if dry_run:
        return path
    expected = orientation_time_range(template_ori)[0] - t_ref
    if os.path.exists(path) and abs(orientation_time_range(path)[0] - expected) < 1e-3:
        return path
    os.makedirs(sim_root, exist_ok=True)
    tmp = path + ".tmp%d" % os.getpid()
    write_shifted_orientation(template_ori, tmp, t_ref)
    os.replace(tmp, path)
    print("    wrote %s (orientation file in t - t_ref)" % path)
    return path


def scale_fluxes(sources_dir, num_sims):
    """Divide every .Flux in the copied source files by num_sims (flux chunks)."""
    changes = []
    pattern = re.compile(r"^(\s*)(\S+\.Flux)(\s+)(\S+)(.*)$")
    for path in sorted(glob.glob(os.path.join(sources_dir, "*.source"))):
        lines = open(path).readlines()
        for k, line in enumerate(lines):
            m = pattern.match(line.rstrip("\n"))
            if not m or line.lstrip().startswith("#"):
                continue
            old = float(m.group(4))
            new = old / num_sims
            lines[k] = "%s%s%s%.6e%s\n" % (m.group(1), m.group(2), m.group(3), new, m.group(5))
            changes.append({"file": os.path.basename(path), "keyword": m.group(2), "flux": old, "scaled": new})
        with open(path, "w") as f:
            f.writelines(lines)
    if not changes:
        raise SetupError("flux mode, but no .Flux keyword found in %s" % sources_dir)
    return changes


# ---------------------------------------------------------------------------
# Generated scripts
# ---------------------------------------------------------------------------

def sbatch_header(cfg, job_name, time, mem, log_name, array=None):
    lines = ["#!/bin/bash",
             "#SBATCH --time=%s" % time,
             "#SBATCH -o logs/%s" % log_name.replace("KIND", "output"),
             "#SBATCH -e logs/%s" % log_name.replace("KIND", "error")]
    if array:
        lines.append("#SBATCH --array=%s" % array)
    lines += ["#SBATCH --job-name=%s" % job_name,
              "#SBATCH --ntasks=1",
              "#SBATCH --mem-per-cpu=%s" % mem]
    lines += ["#SBATCH %s" % d for d in cfg["slurm"]["extra_directives"]]
    return "\n".join(lines) + "\n"


def source_env(env_script):
    env_dir, env_file = os.path.split(env_script)
    return "cd %s\nsource %s\n" % (env_dir, env_file)


def run_sims_py(cfg, t_ref, file_name, chunk_sources=False):
    text = ("# Simulation job (cosima + revan), written by setup_sims.py.\n"
            "import os, random\n"
            "from cosi_sim.pipeline.simulate import Simulate\n\n"
            "instance = Simulate(\"inputs.yaml\")\n")
    if chunk_sources:
        text += ("# Light-curve time chunk: use this chunk's Sources/ (its own light curve and flux):\n"
                 "instance.run_dir = os.getcwd()\n")
    text += ("seed = random.randint(0, 2**31 - 1)\n"
            "with open(\"cosima_seed.txt\", \"w\") as f:\n"
            "    f.write(\"%d\\n\" % seed)\n"
            "instance.define_sim()\n"
            "instance.run_cosima(seed=seed)\n")
    if t_ref is not None:
        text += ("\n# Shift the sim times back to absolute times (the run used t - t_ref):\n"
                 "instance.modify_sim_times(\"%s.inc1.id1.sim.gz\", %r)\n"
                 "instance.name = \"fixed_times\"\n\n" % (file_name, t_ref))
    text += ("revan_geo = %s\n"
             "instance.run_revan(geo_file=revan_geo)\n" % json.dumps(cfg["revan_geometry"]))
    return text


def post_megalib_py(cfg, sim_name):
    return ("# Post-processing step 1 (MEGAlib environment), written by setup_sims.py.\n"
            "import os, sys\n"
            "from cosi_sim.pipeline.simulate import Simulate\n\n"
            "revan_geo = %s\n"
            "extracted = \"Output/%s.inc1.id1.extracted.tra.gz\"\n"
            "filtered = \"Output/%s.inc1.id1.extracted.filtered.tra.gz\"\n\n"
            "# Remove outputs of an earlier run, so a failed mimrec cannot leave a stale file:\n"
            "for old in (extracted, filtered):\n"
            "    if os.path.exists(old):\n"
            "        os.remove(old)\n\n"
            "instance = Simulate(\"inputs.yaml\")\n"
            "instance.name = %s\n"
            "instance.run_mimrec(extract_root=True, geo_file=revan_geo)\n"
            "if not os.path.isfile(extracted) or os.path.getsize(extracted) == 0:\n"
            "    sys.exit(\"mimrec did not write \" + extracted)\n\n"
            "os.chdir(\"Output\")\n"
            "code = os.system(f\"python %s -f %s.inc1.id1.extracted.tra.gz -g {revan_geo}\")\n"
            "os.chdir(\"../\")\n"
            "sys.exit(1 if code else 0)\n"
            % (json.dumps(cfg["revan_geometry"]), sim_name, sim_name, json.dumps(sim_name),
               cfg["overflow_filter"], sim_name))


def post_cosipy_py(label):
    return ("# Post-processing step 2 (cosipy environment), written by setup_sims.py.\n"
            "from cosipy import UnBinnedData\n\n"
            "analysis = UnBinnedData(\"cosipy_inputs.yaml\")\n"
            "savefile = %s\n"
            "analysis.read_tra(output_name=savefile)\n"
            "analysis.cut_SAA_events(output_name=savefile + \"_with_SAAcut\")\n" % json.dumps(label))


def write_job_scripts(run_dir, cfg, state):
    slurm = cfg["slurm"]
    name = state["source_name"]
    files = {}
    if state["mode"] == "grb":
        files["grb_job.sh"] = (
            sbatch_header(cfg, name, slurm["grb_time"], slurm["grb_mem"], "sim_KIND.%j")
            + "\n#The MEGAlib environment first needs to be sourced:\n" + source_env(cfg["megalib_env"])
            + "\n#Run the simulation in the source directory:\n"
            + "cd %s\nexport MPLBACKEND=Agg\npython run_sims.py\n" % run_dir)
    else:
        mode_time = slurm["flux_time"] if state["mode"] == "flux" else slurm["sim_time"]
        mode_mem = slurm["flux_mem"] if state["mode"] == "flux" else slurm["sim_mem"]
        jitter = int(slurm["start_jitter"] or 0)
        files["slurm_array_job.sh"] = (
            sbatch_header(cfg, name, mode_time, mode_mem, "sim_KIND.%A_%a", "0-%d" % (state["njobs"] - 1))
            + ("\n#Need to delay job start times by random number to prevent overloading system:\n"
               "sleep `expr $RANDOM %% %d`\n" % jitter if jitter > 0 else "")
            + "\n#The MEGAlib environment first needs to be sourced:\n" + source_env(cfg["megalib_env"])
            + "\n#Change to the source directory and run job\n"
            + "cd %s\n" % run_dir
            + "cp run_sims.py inputs.yaml Simulations/sim_$SLURM_ARRAY_TASK_ID\n"
            + "cd Simulations/sim_$SLURM_ARRAY_TASK_ID\n"
            + "export MPLBACKEND=Agg\npython run_sims.py\n")
    files["postprocess.sh"] = (
        sbatch_header(cfg, name + "_post", slurm["post_time"], slurm["post_mem"], "post_KIND.%j")
        + "\n# Check the sims (resubmitting failures), then mimrec, overflow filter,\n"
        + "# cosipy and copy of the final file. Safe to rerun by hand.\n"
        + "cd %s\n" % run_dir
        + "%s %s finish %s\n" % (cfg["orchestrator_python"], os.path.join(AUTOMATION_DIR, "run_pipeline.py"), run_dir))
    files["run_sims.py"] = run_sims_py(cfg, state.get("t_ref"), state["file_name"], bool(state.get("lightcurve_chunks")))
    files["post_megalib.py"] = post_megalib_py(cfg, state["sim_name"])
    files["post_cosipy.py"] = post_cosipy_py(state["output_label"])
    files["post_plots.py"] = POST_PLOTS_PY
    for fname, text in files.items():
        path = os.path.join(run_dir, fname)
        with open(path, "w") as f:
            f.write(text)
        if fname.endswith(".sh"):
            os.chmod(path, 0o755)


# ---------------------------------------------------------------------------
# Main per-source setup
# ---------------------------------------------------------------------------

def make_sim_dirs(run_dir, state, extra_files):
    """Simulations/sim_<i> with inputs.yaml, run_sims.py and (time chunks) GalacticScan.ori.

    For light-curve time chunks the directories already hold GalacticScan.ori and Sources/.
    """
    sims = os.path.join(run_dir, "Simulations")
    if not state.get("lightcurve_chunks"):
        if os.path.isdir(sims):
            shutil.rmtree(sims)
        os.makedirs(sims)
    for i in range(state["njobs"]):
        d = os.path.join(sims, "sim_%d" % i)
        os.makedirs(d, exist_ok=True)
        for fname in ("inputs.yaml", "run_sims.py"):
            shutil.copy2(os.path.join(run_dir, fname), d)
        if extra_files:
            os.replace(extra_files(i), os.path.join(d, "GalacticScan.ori"))


def write_combined_tra(run_dir, state):
    """Output/<name>.inc1.id1.tra.gz listing the per-job tra files (as run_parallel_sims.py)."""
    out = os.path.join(run_dir, "Output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "%s.inc1.id1.tra.gz" % state["sim_name"])
    with gzip.open(path, "wt") as f:
        f.write("TYPE TRA\n\n")
        for i in range(state["njobs"]):
            f.write("IN %s\n" % os.path.join(run_dir, "Simulations", "sim_%d" % i, "Output",
                                             "%s.inc1.id1.tra.gz" % state["sim_name"]))
        f.write("EN")


def setup_source(src, mode, cfg, template_text, template, force=False, dry_run=False):
    lib_file = library_source_file(src)
    if not os.path.isfile(lib_file):
        raise SetupError("not in the source library (%s not found)" % lib_file)
    with open(os.path.join(LIBRARY, "master_source_list.txt")) as f:
        if src not in eval(f.read()):
            raise SetupError("not in Source_Library/master_source_list.txt")

    mode = mode or detect_mode(src)
    name = os.path.basename(src)
    cls = class_name(src, cfg)
    run_dir = os.path.join(cfg["sim_root"], cls, name)
    num_sims = int(cfg["num_sims"])

    if os.path.isfile(os.path.join(run_dir, STATE_FILE)):
        existing = load_state(run_dir)
        if existing["source"] != src:
            # Never let one library source replace another (e.g. DC2 and DC4 Galactic/Crab):
            raise SetupError("%s is already used by %s; use another sim_root or class_map for this source"
                             % (run_dir, existing["source"]))
        if not force:
            raise SetupError("already set up in %s (stage: %s); use --force to redo it"
                             % (run_dir, existing["stage"]))

    # Times relative to t_ref (normalized light curves) and the orientation file of the sims:
    t_ref, grb_ori = None, None
    if mode == "grb":
        grb_ori, t_ref = grb_inputs(src, cfg)
        ori_range = orientation_time_range(grb_ori)
    else:
        t_ref = read_time_reference(os.path.join(LIBRARY, src))
        o0, o1 = orientation_time_range(template["orientation_file"])
        ori_range = (o0 - t_ref, o1 - t_ref) if t_ref is not None else (o0, o1)

    lc_flags = lightcurve_flags(lib_file)
    if mode == "time" and any(lc_flags):
        raise SetupError("time chunks cannot split a repeating light curve; use flux mode")

    # Light curves that do not repeat must match the orientation file (bursts: lie inside it):
    problems = check_lightcurves(lib_file, ori_range, burst=(mode == "grb"))
    if problems:
        raise SetupError("light curve check failed: " + "; ".join(problems))

    if dry_run:
        gz = gunzip_library_files(src, dry_run=True)
        note = "  (times - t_ref %r)" % t_ref if t_ref is not None else ""
        print("%-50s %-5s -> %s%s%s" % (src, mode, run_dir, note,
                                      "  (gunzip %s)" % ", ".join(gz) if gz else ""))
        return

    unzipped = gunzip_library_files(src)
    for name_gz in unzipped:
        print("    gunzipped %s in the source library" % name_gz)

    os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
    for old in ("Output", "Orientation_Bins"):
        if os.path.isdir(os.path.join(run_dir, old)):
            shutil.rmtree(os.path.join(run_dir, old))

    # inputs.yaml:
    keys = {"run_dir": run_dir, "src_list": [src], "num_sims": num_sims,
            "parallel_time_sims": mode == "time", "lightcurve": False,
            "mcosima": False, "clear_sims": True}
    if mode == "grb":
        local_ori = os.path.join(run_dir, os.path.basename(grb_ori))
        shutil.copy2(grb_ori, local_ori)
        keys["orientation_file"] = local_ori
    elif t_ref is not None:
        keys["orientation_file"] = normed_orientation(template["orientation_file"], t_ref, cfg["sim_root"])
    with open(os.path.join(run_dir, "inputs.yaml"), "w") as f:
        f.write(set_yaml_keys(template_text, keys))
    file_name = template["name"]
    sim_name = "fixed_times" if t_ref is not None else file_name

    # cosipy_inputs.yaml:
    with open(cfg["cosipy_template"]) as f:
        cosipy_text = f.read()
    filtered = "Output/%s.inc1.id1.extracted.filtered.tra.gz" % sim_name
    with open(os.path.join(run_dir, "cosipy_inputs.yaml"), "w") as f:
        f.write(set_yaml_keys(cosipy_text, {"data_file": filtered}))

    # Sources/ (same as run_sim_setup.py):
    home = os.getcwd()
    try:
        os.chdir(run_dir)
        Setup("inputs.yaml").setup_srcs()
    except SystemExit:
        raise SetupError("Setup.setup_srcs() failed")
    finally:
        os.chdir(home)

    flux_scaling = scale_fluxes(os.path.join(run_dir, "Sources"), num_sims) if mode == "flux" else []

    # Number of jobs (time chunks get one more if the orientation file does not divide evenly):
    extra_files, lc_chunks = None, None
    if mode == "time" and lc_flags:
        sims = os.path.join(run_dir, "Simulations")
        if os.path.isdir(sims):
            shutil.rmtree(sims)
        # The chunks run in times t - t_ref (t_ref: first orientation time), as GRBs do:
        lc_ori = keys.get("orientation_file", template["orientation_file"])
        shift = 0.0
        if t_ref is None:
            t_ref = shift = orientation_time_range(lc_ori)[0]
            sim_name = "fixed_times"
            filtered = "Output/%s.inc1.id1.extracted.filtered.tra.gz" % sim_name
            with open(os.path.join(run_dir, "cosipy_inputs.yaml"), "w") as f:
                f.write(set_yaml_keys(cosipy_text, {"data_file": filtered}))
        try:
            lc_chunks = write_chunks(os.path.join(run_dir, "Sources", name + ".source"), os.path.join(run_dir, "Sources"),
                                     lc_ori, num_sims, lambda k: os.path.join(sims, "sim_%d" % k), t_shift=shift)
        except (LightCurveError, OSError) as err:
            raise SetupError("light-curve time chunks: %s" % err)
        njobs = lc_chunks["chunks"]
        lc_chunks = {k: lc_chunks[k] for k in ("chunks", "start", "stop", "photons_per_cm2")}
    elif mode == "time":
        try:
            os.chdir(run_dir)
            extra = make_bins(num_sims, keys.get("orientation_file", template["orientation_file"]), False, "")
        finally:
            os.chdir(home)
        njobs = num_sims + extra
        extra_files = lambda i: os.path.join(run_dir, "Orientation_Bins", "bin_%d.ori" % i)  # noqa: E731
    elif mode == "flux":
        njobs = num_sims
    else:
        njobs = 1

    label = (cfg["grb_output_label"] if mode == "grb" else cfg["output_label"]).format(source=name)
    state = {
        "source": src, "source_name": name, "class": cls, "mode": mode, "run_dir": run_dir,
        "njobs": njobs, "num_sims": num_sims, "file_name": file_name, "sim_name": sim_name,
        "filtered_tra": filtered, "output_label": label, "products_dir": cfg["products_dir"],
        "megalib_env": cfg["megalib_env"], "cosipy_env": cfg["cosipy_env"],
        "revan_geometry": cfg["revan_geometry"], "t_ref": t_ref,
        "orientation_file": keys.get("orientation_file", template["orientation_file"]),
        "flux_scaling": flux_scaling, "lightcurve_chunks": lc_chunks, "slurm": cfg["slurm"],
        "stage": "setup", "attempt": 0, "completed": [], "jobs": [],
        "history": ["%s  set up (%s mode, %d job%s)" % (now(), mode, njobs, "s" if njobs > 1 else "")],
    }
    write_job_scripts(run_dir, cfg, state)
    if mode != "grb":
        make_sim_dirs(run_dir, state, extra_files)
        write_combined_tra(run_dir, state)
        if mode == "time" and not lc_chunks:
            os.rmdir(os.path.join(run_dir, "Orientation_Bins"))
    save_state(run_dir, state)

    msg = "%-50s %-5s %5d job%s -> %s" % (src, mode, njobs, "s" if njobs > 1 else " ", run_dir)
    if flux_scaling:
        msg += "\n    flux / %d: %s" % (num_sims, ", ".join(
            "%s %.4g -> %.4g" % (c["keyword"], c["flux"], c["scaled"]) for c in flux_scaling))
    if lc_chunks:
        msg += ("\n    light curve: %d time chunks with equal expected photons over [%.1f, %.1f] s; "
                "flux of each chunk from the light curve" % (lc_chunks["chunks"], lc_chunks["start"], lc_chunks["stop"]))
    if t_ref is not None:
        ori_note = "chunk orientation files" if lc_chunks else "orientation %s" % os.path.basename(keys["orientation_file"])
        msg += "\n    times relative to t_ref %r: %s; sim times fixed after cosima" % (t_ref, ori_note)
    print(msg)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-c", "--config", required=True, help="pipeline_config.yaml")
    p.add_argument("sources", nargs="*", help="library paths, e.g. DC5/sources/Galactic/cygX3")
    p.add_argument("--list", help="file with one library path per line (optional mode after it)")
    p.add_argument("--force", action="store_true", help="redo sources that are already set up")
    p.add_argument("--dry-run", action="store_true", help="show what would be done")
    args = p.parse_args(argv)

    cfg = load_config(args.config)
    entries = read_source_list(args)
    if not entries:
        p.error("give sources on the command line or with --list")
    with open(cfg["inputs_template"]) as f:
        template_text = f.read()
    template = yaml.load(template_text, Loader=yaml.FullLoader)
    check_paths(cfg, template)

    failed = []
    targets = {}
    for src, mode in entries:
        run_dir = os.path.join(cfg["sim_root"], class_name(src, cfg), os.path.basename(src))
        if run_dir in targets and targets[run_dir] != src:
            sys.exit("%s and %s would both use %s; simulate them in separate sim_roots (or use class_map)."
                     % (targets[run_dir], src, run_dir))
        targets[run_dir] = src
    for src, mode in entries:
        try:
            setup_source(src, mode, cfg, template_text, template, force=args.force, dry_run=args.dry_run)
        except SetupError as err:
            print("%-50s SKIPPED: %s" % (src, err))
            failed.append(src)
    print()
    print("%d of %d sources %s." % (len(entries) - len(failed), len(entries),
                                    "checked" if args.dry_run else "set up"))
    if not args.dry_run and len(failed) < len(entries):
        print("Submit with:  python %s submit %s"
              % (os.path.join(AUTOMATION_DIR, "run_pipeline.py"), cfg["sim_root"]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
