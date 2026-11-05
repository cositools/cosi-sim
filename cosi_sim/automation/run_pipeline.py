#!/usr/bin/env python3
"""
Run the cosi-sim pipeline for sources prepared with setup_sims.py.

    python run_pipeline.py submit  <targets> [--max-jobs N | --chain]   # submit sims + post-processing
    python run_pipeline.py fill    <sim_root>            # submit waiting sources that fit now
    python run_pipeline.py status  <targets>             # progress of each source
    python run_pipeline.py check   <targets>             # check the sim outputs only
    python run_pipeline.py finish  <run_dir> [--from STEP] [--no-resubmit]
    python run_pipeline.py resubmit <run_dir>            # resubmit failed sims by hand
    python run_pipeline.py cancel  <targets>             # scancel the recorded jobs

<targets> are source run directories, or any directory above them
(e.g. the simulation root or a class directory); every directory below it
that contains an automation.json is used.

How it works
------------
`submit` sends the simulation job (a SLURM array of cosima + revan runs, or a
single job for GRBs) and a post-processing job that waits for it with
`--dependency=afterany`, so nothing sits idle polling the queue. The
post-processing job runs `finish`, which

  1. checks every sim (revan finished, tra file written);
     failed sims are resubmitted automatically (up to slurm.max_retries times),
     together with a new post-processing job;
  2. runs mimrec (extract_root=True) and the MEGAlib overflow filter
     in the MEGAlib environment;
  3. runs cosipy read_tra and cut_SAA_events in the cosipy environment;
  4. copies the *_with_SAAcut file to products_dir.

Rolling submission (optional): with slurm.max_jobs in the config, or
--max-jobs N, sources are queued and submitted only while your SLURM jobs
(pending + running, array tasks counted separately) stay <= N. Each
post-processing job submits the next waiting sources once its own sims have
left the queue, so a whole data challenge can be submitted with one command.

Each step is recorded in <run_dir>/automation.json, so `finish` can be rerun
by hand and continues from the first step that has not completed
(or from --from check|mimrec|cosipy|copy).

This file only uses the Python standard library.
"""

import argparse
import datetime
import fcntl
import glob
import json
import os
import shutil
import subprocess
import sys

STATE_FILE = "automation.json"
STEPS = ["check", "mimrec", "cosipy", "copy"]
AUTOMATION_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# State and small helpers
# ---------------------------------------------------------------------------

def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def load_state(run_dir):
    with open(os.path.join(run_dir, STATE_FILE)) as f:
        return json.load(f)


def save_state(run_dir, state):
    path = os.path.join(run_dir, STATE_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def update_state(run_dir, fn=None, message=None, **fields):
    """Read-modify-write automation.json under a lock.

    The submitting process and the post-processing jobs can both write the file,
    so every write starts from the current file on disk.
    """
    with open(os.path.join(run_dir, STATE_FILE + ".lock"), "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
        except OSError:
            pass                      # file system without locking: still read-modify-write
        state = load_state(run_dir)
        state.update(fields)
        if fn:
            fn(state)
        if message:
            log_event(state, message)
        save_state(run_dir, state)
    return state


def log_event(state, message):
    state.setdefault("history", []).append("%s  %s" % (now(), message))
    print(message)


def find_run_dirs(targets, max_depth=4):
    """Run directories (containing automation.json) at or below each target."""
    found = []
    for target in targets:
        target = os.path.abspath(target)
        if os.path.isfile(os.path.join(target, STATE_FILE)):
            found.append(target)
            continue
        if not os.path.isdir(target):
            print("WARNING: %s is not a directory, skipped." % target)
            continue
        base_depth = target.rstrip(os.sep).count(os.sep)
        for root, dirs, files in os.walk(target):
            depth = root.count(os.sep) - base_depth
            if STATE_FILE in files:
                found.append(root)
                dirs[:] = []          # do not descend into Simulations/ etc.
            elif depth >= max_depth:
                dirs[:] = []
            else:
                dirs[:] = sorted(d for d in dirs if d not in ("Simulations", "Output", "Sources", "logs"))
    # Keep order, drop duplicates:
    seen = set()
    return [d for d in found if not (d in seen or seen.add(d))]


def tail_lines(path, nbytes=16384):
    """Last lines of a (possibly large) text file."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - nbytes))
        data = f.read().decode("utf-8", errors="replace")
    return data.splitlines()


def compress_ranges(indices):
    """[0,1,2,5,7,8] -> '0-2,5,7-8' (SLURM --array syntax)."""
    indices = sorted(set(indices))
    parts = []
    i = 0
    while i < len(indices):
        j = i
        while j + 1 < len(indices) and indices[j + 1] == indices[j] + 1:
            j += 1
        parts.append(str(indices[i]) if i == j else "%d-%d" % (indices[i], indices[j]))
        i = j + 1
    return ",".join(parts)


def sim_output_dirs(state):
    """(index, Output directory) for every sim of this source."""
    run_dir = state["run_dir"]
    if state["mode"] == "grb":
        return [(0, os.path.join(run_dir, "Output"))]
    return [(i, os.path.join(run_dir, "Simulations", "sim_%d" % i, "Output"))
            for i in range(state["njobs"])]


def check_one_sim(output_dir, tra_name):
    """Same criteria as Simulate.check_revan_parallel. Returns (ok, reason, n_compton)."""
    tra = os.path.join(output_dir, tra_name)
    log = os.path.join(output_dir, "revan_terminal_output.txt")
    if not os.path.isfile(tra):
        return False, "no revan output (%s)" % tra_name, None
    if not os.path.isfile(log):
        return False, "no revan terminal output", None
    lines = [l for l in tail_lines(log) if l.strip()]
    if not lines:
        return False, "empty revan terminal output", None
    if not any("Event reconstruction finished" in l for l in lines[-3:]):
        return False, "revan did not finish", None
    n_compton = None
    for line in reversed(lines[-40:]):
        if "Compton" in line:
            for token in line.replace(":", " ").split():
                try:
                    n_compton = float(token)
                    break
                except ValueError:
                    continue
            break
    return True, "", n_compton


def check_sims(state):
    """Check every sim of a source. Returns (failed indices, report lines, n_compton list)."""
    tra_name = "%s.inc1.id1.tra.gz" % state["sim_name"]
    failed, report, counts = [], [], []
    for i, out in sim_output_dirs(state):
        ok, reason, n = check_one_sim(out, tra_name)
        if not ok:
            failed.append(i)
            report.append("sim %d: %s" % (i, reason))
        elif n is not None:
            counts.append(n)
            if n == 0:
                report.append("sim %d: WARNING: 0 Compton events" % i)
    return failed, report, counts


# ---------------------------------------------------------------------------
# SLURM
# ---------------------------------------------------------------------------

class SubmitError(Exception):
    """sbatch rejected a job. sim_id is set if the simulation job was already submitted."""
    def __init__(self, message, sim_id=None):
        super().__init__(message)
        self.sim_id = sim_id


def sbatch(args, run_dir, dry_run=False):
    cmd = ["sbatch", "--parsable"] + args
    if dry_run:
        print("    [dry run] (cd %s && %s)" % (run_dir, " ".join(cmd)))
        return "DRYRUN"
    out = subprocess.run(cmd, cwd=run_dir, capture_output=True, text=True)
    if out.returncode != 0:
        raise SubmitError("sbatch %s was rejected: %s" % (args[-1], (out.stderr or out.stdout).strip()))
    return out.stdout.strip().split(";")[0]


def array_spec(state, indices=None):
    spec = compress_ranges(indices) if indices is not None else "0-%d" % (state["njobs"] - 1)
    throttle = state["slurm"].get("array_throttle")
    if throttle:
        spec += "%%%d" % int(throttle)
    return spec


def submit_sim_jobs(state, indices=None, depend_on=None, dry_run=False, note=None):
    """Submit the simulation job(s) and the dependent post-processing job.

    Each job ID is written to automation.json as soon as it exists, so `cancel`
    always finds it. If the post-processing job is rejected, the source is
    marked post_not_submitted and SubmitError is raised.
    """
    run_dir = state["run_dir"]
    dep = ["--dependency=afterany:%s" % depend_on] if depend_on else []
    if state["mode"] == "grb":
        sim_id = sbatch(dep + ["grb_job.sh"], run_dir, dry_run)
    else:
        sim_id = sbatch(dep + ["--array=%s" % array_spec(state, indices), "slurm_array_job.sh"],
                        run_dir, dry_run)
    if not dry_run:
        job = {"sim": sim_id, "post": None, "time": now()}
        if note:
            job["resubmitted"] = note
        update_state(run_dir, lambda s: s.setdefault("jobs", []).append(job))
    try:
        post_id = sbatch(["--dependency=afterany:%s" % sim_id, "postprocess.sh"], run_dir, dry_run)
    except SubmitError as err:
        update_state(run_dir, stage="post_not_submitted",
                     message="ERROR: %s. Simulation job %s has no post-processing job; when it ends, run: "
                             "run_pipeline.py finish %s (or cancel it)" % (err, sim_id, run_dir))
        raise SubmitError(str(err), sim_id=sim_id)
    if not dry_run:
        def set_post(s):
            for j in reversed(s.get("jobs", [])):
                if j["sim"] == sim_id:
                    j["post"] = post_id
                    break
        update_state(run_dir, set_post)
    return sim_id, post_id


# ---------------------------------------------------------------------------
# Rolling submission (optional; enabled with max_jobs / --max-jobs)
# ---------------------------------------------------------------------------
#
# SLURM limits how many jobs a user may have pending + running (on Palmetto 2:
# MaxSubmitPU = 3000, counting every array task). With max_jobs set, `submit`
# puts the sources in a queue file next to the class directories
# (<sim_root>/pipeline_queue.json) and submits only what fits. Each source's
# post-processing job then submits the next waiting sources, once its own sims
# have left the queue. Nothing polls: there is one squeue call per fill.

QUEUE_FILE = "pipeline_queue.json"


def queue_path_for(run_dir):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(run_dir))), QUEUE_FILE)


def jobs_needed(state):
    return state["njobs"] + 1          # array tasks (or the GRB job) + post-processing job


class LockedQueue:
    """Context manager: load, lock, and save the queue file."""

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.lock = open(self.path + ".lock", "w")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX)
        except OSError:
            pass
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.queue = json.load(f)
        else:
            self.queue = {"max_jobs": None, "waiting": [], "history": []}
        return self.queue

    def __exit__(self, *exc):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.queue, f, indent=2)
        os.replace(tmp, self.path)
        self.lock.close()
        return False


def count_my_jobs():
    """Number of this user's pending + running jobs, counting array tasks separately."""
    user = os.environ.get("USER") or os.environ.get("LOGNAME")
    cmd = ["squeue", "-h", "-r", "-o", "%i"] + (["-u", user] if user else ["--me"])
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise SubmitError("squeue failed: %s" % (out.stderr or out.stdout).strip())
    return sum(1 for line in out.stdout.splitlines() if line.strip())


def fill_queue(path):
    """Submit waiting sources while they fit under max_jobs. Returns the run dirs submitted."""
    if not os.path.exists(path):
        return []
    with LockedQueue(path) as q:
        if not q["waiting"]:
            return []
        try:
            used = count_my_jobs()
        except SubmitError as err:
            q["history"].append("%s  ERROR: %s; nothing submitted" % (now(), err))
            print("ERROR: %s" % err)
            return []
        start = used
        submitted, remaining = [], []
        waiting = list(q["waiting"])
        for k, run_dir in enumerate(waiting):
            state = load_state(run_dir)
            if state["stage"] != "waiting":          # cancelled or submitted another way
                continue
            need = jobs_needed(state)
            if used + need > q["max_jobs"]:
                remaining.append(run_dir)           # keep looking: a smaller source may fit
                continue
            name = "%s/%s" % (state["class"], state["source_name"])
            update_state(run_dir, stage="submitted", attempt=0, completed=[])
            try:
                sim_id, post_id = submit_sim_jobs(state)
            except SubmitError as err:
                if err.sim_id is None:              # rejected: keep it and the rest waiting
                    update_state(run_dir, stage="waiting", message="%-40s ERROR: %s" % (name, err))
                    remaining += [d for d in waiting[k:] if d not in remaining]
                    break
                used += need                        # sims queued; reported as post_not_submitted
                continue
            update_state(run_dir, message="%-40s submitted from the queue: sims %s (%d), post-processing %s"
                         % (name, sim_id, state["njobs"], post_id))
            used += need
            submitted.append(run_dir)
        q["waiting"] = remaining
        q["history"].append("%s  %d jobs in SLURM before, %d after; submitted %d source(s), %d waiting"
                            % (now(), start, used, len(submitted), len(remaining)))
    return submitted


def enqueue(run_dirs, max_jobs, force=False):
    """Mark sources as waiting in their queue files, then fill each queue."""
    queues = {}
    for run_dir in run_dirs:
        state = load_state(run_dir)
        name = "%s/%s" % (state["class"], state["source_name"])
        if state["stage"] not in ("setup",) and not force:
            print("%-40s skipped (stage: %s; use --force to submit again)" % (name, state["stage"]))
            continue
        if jobs_needed(state) > max_jobs:
            print("%-40s skipped: needs %d jobs, more than max_jobs = %d"
                  % (name, jobs_needed(state), max_jobs))
            continue
        path = queue_path_for(run_dir)
        update_state(run_dir, stage="waiting", queue_file=path, attempt=0, completed=[])
        queues.setdefault(path, []).append(run_dir)
    for path, dirs in queues.items():
        with LockedQueue(path) as q:
            q["max_jobs"] = max_jobs
            q["waiting"] += [d for d in dirs if d not in q["waiting"]]
            q["history"].append("%s  %d source(s) added, max_jobs %d" % (now(), len(dirs), max_jobs))
        submitted = fill_queue(path)
        with open(path) as f:
            n_wait = len(json.load(f)["waiting"])
        print("Queue %s: %d source(s) submitted now, %d waiting (max_jobs %d)."
              % (path, len(submitted), n_wait, max_jobs))
        if n_wait:
            active = ("submitted", "resubmitted", "checking", "mimrec", "cosipy")
            running = [d for d in find_run_dirs([os.path.dirname(path)])
                       if load_state(d).get("queue_file") == path and load_state(d)["stage"] in active]
            if running:
                print("The waiting sources are submitted automatically as running sources finish.")
            else:
                print("None of these sources is running yet (your other jobs fill the budget), so run\n"
                      "    python %s fill %s\nonce some of your jobs have ended."
                      % (os.path.abspath(__file__), os.path.dirname(path)))


def fill_for(state):
    """Called by the post-processing job: submit waiting sources of this source's queue."""
    path = state.get("queue_file")
    if path:
        fill_queue(path)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_submit(args):
    run_dirs = find_run_dirs(args.targets)
    if not run_dirs:
        sys.exit("No prepared sources found (run setup_sims.py first).")
    max_jobs = args.max_jobs
    if max_jobs is None and not args.no_queue:
        max_jobs = load_state(run_dirs[0])["slurm"].get("max_jobs")
    if max_jobs:
        if args.chain:
            sys.exit("--chain and max_jobs (rolling submission) cannot be combined; use one or the other.")
        if args.dry_run:
            for run_dir in run_dirs:
                state = load_state(run_dir)
                print("    [dry run] queue %s/%s (%d jobs)" % (state["class"], state["source_name"],
                                                             jobs_needed(state)))
            print("    [dry run] sources are submitted while your SLURM jobs stay <= %d" % max_jobs)
            return 0
        enqueue(run_dirs, int(max_jobs), force=args.force)
        return 0
    previous = None
    errors = 0
    for run_dir in run_dirs:
        state = load_state(run_dir)
        name = "%s/%s" % (state["class"], state["source_name"])
        if state["stage"] not in ("setup",) and not args.force:
            print("%-40s skipped (stage: %s; use --force to submit again)" % (name, state["stage"]))
            continue
        depend = previous if args.chain else None
        if not args.dry_run:
            update_state(run_dir, stage="submitted", attempt=0, completed=[])
        try:
            sim_id, post_id = submit_sim_jobs(state, depend_on=depend, dry_run=args.dry_run)
        except SubmitError as err:
            errors += 1
            if err.sim_id is None:      # nothing was submitted: allow a plain resubmit later
                update_state(run_dir, stage="setup", message="%-40s ERROR: %s" % (name, err))
            else:
                print("%-40s ERROR: %s" % (name, err))
            continue
        if args.dry_run:
            continue
        update_state(run_dir, message="%-40s submitted: sims %s (%d), post-processing %s"
                     % (name, sim_id, state["njobs"], post_id))
        previous = sim_id
    return 1 if errors else 0


def cmd_check(args):
    for run_dir in find_run_dirs(args.targets):
        state = load_state(run_dir)
        failed, report, counts = check_sims(state)
        name = "%s/%s" % (state["class"], state["source_name"])
        print("%s: %d/%d sims ok" % (name, state["njobs"] - len(failed), state["njobs"]))
        if counts:
            print("    Compton events per sim: mean %.1f, min %g, max %g"
                  % (sum(counts) / len(counts), min(counts), max(counts)))
        for line in report[:args.max_lines]:
            print("    " + line)
        if len(report) > args.max_lines:
            print("    ... %d more" % (len(report) - args.max_lines))
        if failed:
            print("    failed: %s" % compress_ranges(failed))


def cmd_status(args):
    run_dirs = find_run_dirs(args.targets)
    print("%-42s %-5s %-6s %-11s %-18s %s" % ("source", "mode", "jobs", "sims ok", "stage", "final file"))
    for run_dir in run_dirs:
        state = load_state(run_dir)
        name = "%s/%s" % (state["class"], state["source_name"])
        if state["stage"] == "setup":
            ok = "-"
        else:
            failed, _, _ = check_sims(state)
            ok = "%d/%d" % (state["njobs"] - len(failed), state["njobs"])
        final = state.get("final_file") or ""
        print("%-42s %-5s %-6d %-11s %-18s %s" % (name, state["mode"], state["njobs"], ok,
                                                state["stage"], os.path.basename(final)))
    queues = list(dict.fromkeys(load_state(d).get("queue_file") for d in run_dirs if load_state(d).get("queue_file")))
    active = ("submitted", "resubmitted", "checking", "mimrec", "cosipy")
    for path in queues:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            q = json.load(f)
        if not q["waiting"]:
            continue
        print("\n%d source(s) waiting in %s (max_jobs %s)." % (len(q["waiting"]), path, q["max_jobs"]))
        if not any(load_state(d)["stage"] in active for d in run_dirs if load_state(d).get("queue_file") == path):
            print("No source of this queue is running, so nothing will submit them; run:\n"
                  "    python %s fill %s" % (os.path.abspath(__file__), os.path.dirname(path)))


def run_in_env(env_script, command, run_dir, log_path):
    """cd <env dir>; source <env>; cd <run_dir>; <command>  -- output to log_path."""
    env_dir, env_file = os.path.split(os.path.abspath(env_script))
    script = 'cd "%s" && source "./%s" && cd "%s" && %s' % (env_dir, env_file, run_dir, command)
    env = dict(os.environ, MPLBACKEND="Agg")
    with open(log_path, "a") as log:
        log.write("\n==== %s  %s\n" % (now(), command))
        log.flush()
        result = subprocess.run(["bash", "-c", script], stdout=log, stderr=subprocess.STDOUT, env=env)
    return result.returncode


def fail(run_dir, stage, message):
    update_state(run_dir, stage=stage, message="ERROR: " + message)
    return 1


def _finish(args):
    run_dir = os.path.abspath(args.run_dir)
    state = load_state(run_dir)

    def commit(message=None, **fields):
        """Record fields locally and in automation.json (merged with the file on disk)."""
        state.update(fields)
        update_state(run_dir, message=message, **fields)

    completed = list(state.get("completed", []))
    if args.from_step:
        completed = STEPS[:STEPS.index(args.from_step)]
        commit(completed=list(completed))
    todo = [s for s in STEPS if s not in completed]
    if not todo:
        print("All steps already completed; final file: %s" % state.get("final_file"))
        return 0
    logs = os.path.join(run_dir, "logs")
    os.makedirs(logs, exist_ok=True)

    # 1. Check the sims, resubmitting failures:
    if "check" in todo:
        commit(stage="checking")
        failed, report, counts = check_sims(state)
        with open(os.path.join(run_dir, "check_report.txt"), "w") as f:
            f.write("%s\n%d/%d sims ok\n" % (now(), state["njobs"] - len(failed), state["njobs"]))
            if counts:
                f.write("Compton events per sim: mean %.1f, min %g, max %g\n"
                        % (sum(counts) / len(counts), min(counts), max(counts)))
            f.write("\n".join(report) + "\n")
        if failed:
            retries = state["slurm"].get("max_retries", 2)
            attempt = state.get("attempt", 0)
            if not args.no_resubmit and attempt < retries:
                # Record the attempt before submitting, so the new post job sees it:
                commit(attempt=attempt + 1, stage="resubmitted")
                indices = None if state["mode"] == "grb" else failed
                try:
                    sim_id, post_id = submit_sim_jobs(state, indices=indices, note=compress_ranges(failed))
                except SubmitError as err:
                    if err.sim_id is None:
                        return fail(run_dir, "failed_sims", "could not resubmit %d failed sims: %s"
                                    % (len(failed), err))
                    return 1          # already recorded as post_not_submitted
                commit(message="%d failed sims (%s) resubmitted, attempt %d/%d: sims %s, post-processing %s"
                       % (len(failed), compress_ranges(failed), attempt + 1, retries, sim_id, post_id))
                return 0
            return fail(run_dir, "failed_sims",
                        "%d sims failed (%s) after %d resubmission(s); see check_report.txt. "
                        "Fix and run: run_pipeline.py resubmit %s"
                        % (len(failed), compress_ranges(failed), attempt, run_dir))
        completed.append("check")
        commit(message="all %d sims ok" % state["njobs"], completed=list(completed))
        # The sims have left the SLURM queue: let waiting sources use the slots.
        fill_for(state)

    # 2. mimrec + overflow filter (MEGAlib environment).
    #    post_megalib.py removes old outputs first and checks that mimrec wrote a new file.
    filtered = os.path.join(run_dir, state["filtered_tra"])
    if "mimrec" in todo:
        commit(stage="mimrec")
        if os.path.exists(filtered):
            os.remove(filtered)
        code = run_in_env(state["megalib_env"], "python post_megalib.py", run_dir,
                          os.path.join(logs, "post_megalib.log"))
        if code != 0 or not os.path.isfile(filtered):
            return fail(run_dir, "failed_mimrec",
                        "mimrec/overflow filter failed (exit %d, %s %s); see logs/post_megalib.log"
                        % (code, state["filtered_tra"], "exists" if os.path.isfile(filtered) else "missing"))
        completed.append("mimrec")
        commit(message="mimrec and overflow filter done", completed=list(completed))

    # 3. cosipy (cosipy environment):
    pattern = os.path.join(run_dir, state["output_label"] + "_with_SAAcut*")
    if "cosipy" in todo:
        commit(stage="cosipy")
        for old in glob.glob(os.path.join(run_dir, state["output_label"] + "*")):
            os.remove(old)
        code = run_in_env(state["cosipy_env"], "python post_cosipy.py", run_dir,
                          os.path.join(logs, "post_cosipy.log"))
        if code != 0 or not glob.glob(pattern):
            return fail(run_dir, "failed_cosipy",
                        "cosipy step failed (exit %d); see logs/post_cosipy.log" % code)
        completed.append("cosipy")
        commit(message="cosipy extraction and SAA cut done", completed=list(completed))

    # 4. Copy the final file:
    if "copy" in todo:
        finals = sorted(glob.glob(pattern))
        if not finals:
            return fail(run_dir, "failed_copy", "no %s file to copy" % os.path.basename(pattern))
        os.makedirs(state["products_dir"], exist_ok=True)
        for final in finals:
            dest = os.path.join(state["products_dir"], os.path.basename(final))
            if os.path.exists(dest):
                print("NOTE: overwriting %s" % dest)
            shutil.copy2(final, dest)
        final_file = os.path.join(state["products_dir"], os.path.basename(finals[0]))
        completed.append("copy")
        commit(message="done: %s" % final_file, final_file=final_file,
               completed=list(completed), stage="done")
    return 0


def cmd_finish(args):
    try:
        return _finish(args)
    finally:
        # Waiting sources (rolling submission) get any slots freed meanwhile.
        fill_for(load_state(os.path.abspath(args.run_dir)))


def cmd_fill(args):
    paths = []
    for target in args.targets:
        direct = os.path.join(os.path.abspath(target), QUEUE_FILE)
        if os.path.exists(direct):
            paths.append(direct)
    for run_dir in find_run_dirs(args.targets):
        path = load_state(run_dir).get("queue_file")
        if path:
            paths.append(path)
    paths = list(dict.fromkeys(paths))
    if not paths:
        print("No queue found.")
        return 0
    for path in paths:
        submitted = fill_queue(path)
        with open(path) as f:
            n_wait = len(json.load(f)["waiting"])
        print("Queue %s: %d source(s) submitted, %d waiting." % (path, len(submitted), n_wait))
    return 0


def cmd_resubmit(args):
    run_dir = os.path.abspath(args.run_dir)
    state = load_state(run_dir)
    failed, _, _ = check_sims(state)
    if not failed and not args.all:
        print("No failed sims. To continue the post-processing run: run_pipeline.py finish %s" % run_dir)
        return 0
    indices = None if (args.all or state["mode"] == "grb") else failed
    what = "all sims" if indices is None else compress_ranges(failed)
    if not args.dry_run:
        # Automatic retries start again:
        update_state(run_dir, stage="resubmitted", completed=[], attempt=0)
    try:
        sim_id, post_id = submit_sim_jobs(state, indices=indices, dry_run=args.dry_run, note=what)
    except SubmitError as err:
        if err.sim_id is None:        # otherwise already reported as post_not_submitted
            update_state(run_dir, stage="failed_sims", message="ERROR: %s" % err)
        return 1
    if not args.dry_run:
        update_state(run_dir, message="resubmitted %s: sims %s, post-processing %s" % (what, sim_id, post_id))
    return 0


def cmd_cancel(args):
    for run_dir in find_run_dirs(args.targets):
        state = load_state(run_dir)
        if state["stage"] == "waiting":
            with LockedQueue(state["queue_file"]) as q:
                q["waiting"] = [d for d in q["waiting"] if d != run_dir]
            update_state(run_dir, stage="setup", message="removed from the submission queue")
            continue
        jobs = state.get("jobs", [])
        if not jobs:
            continue
        ids = [j for j in (jobs[-1].get("sim"), jobs[-1].get("post")) if j]
        subprocess.run(["scancel"] + ids)
        update_state(run_dir, stage="cancelled", message="cancelled jobs %s" % " ".join(ids))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("submit", help="submit sims and post-processing")
    s.add_argument("targets", nargs="+")
    s.add_argument("--chain", action="store_true",
                   help="start each source's sims only after the previous source's sims end")
    s.add_argument("--force", action="store_true", help="submit even if already submitted")
    s.add_argument("--max-jobs", type=int, default=None,
                   help="rolling submission: keep your SLURM jobs (pending + running) at or below this "
                        "(default: slurm.max_jobs from the config)")
    s.add_argument("--no-queue", action="store_true", help="ignore slurm.max_jobs and submit everything now")
    s.add_argument("--dry-run", action="store_true", help="print the sbatch commands only")
    s.set_defaults(func=cmd_submit)

    s = sub.add_parser("fill", help="submit waiting sources that fit (rolling submission)")
    s.add_argument("targets", nargs="+", help="simulation root, class or source directories")
    s.set_defaults(func=cmd_fill)

    s = sub.add_parser("status", help="show progress")
    s.add_argument("targets", nargs="+")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("check", help="check the sim outputs")
    s.add_argument("targets", nargs="+")
    s.add_argument("--max-lines", type=int, default=20)
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("finish", help="check, mimrec, filter, cosipy, copy (run by postprocess.sh)")
    s.add_argument("run_dir")
    s.add_argument("--from", dest="from_step", choices=STEPS, help="restart from this step")
    s.add_argument("--no-resubmit", action="store_true", help="do not resubmit failed sims")
    s.set_defaults(func=cmd_finish)

    s = sub.add_parser("resubmit", help="resubmit failed sims (and post-processing)")
    s.add_argument("run_dir")
    s.add_argument("--all", action="store_true", help="resubmit every sim")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_resubmit)

    s = sub.add_parser("cancel", help="scancel the latest jobs")
    s.add_argument("targets", nargs="+")
    s.set_defaults(func=cmd_cancel)

    args = p.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
