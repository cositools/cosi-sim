#!/usr/bin/env python3
"""
Run a simulation job command and stop it if its log files grow too large.

    python watch_logs.py --limit 1G --marker Output/log_limit_exceeded.txt \
        --slurm-logs <run_dir>/logs --logs 'Output/*terminal_output*.txt' -- python run_sims.py

Every --interval seconds the sizes of the log files (the --logs patterns, relative to the
current directory, and this job's SLURM output and error files in --slurm-logs) are added up.
Above --limit the command and everything it started are stopped, the reason is written to
--marker (which the pipeline check reads, so the sim is not resubmitted automatically), and
the exit code is 3. Otherwise the command's exit code is returned.

Written for the cosi-sim automation (setup_sims.py); standard library only.
"""

import argparse
import glob
import os
import signal
import subprocess
import sys
import time

UNITS = {"": 1, "B": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}


def parse_size(text):
    """'1G', '500M', '2T' or a number of bytes."""
    text = str(text).strip().upper().rstrip("B") or "0"
    unit = text[-1] if text[-1] in UNITS else ""
    return int(float(text[:-1] if unit else text) * UNITS[unit])


def human(n):
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024 or unit == "T":
            return "%.1f%s" % (n, unit) if unit != "B" else "%dB" % n
        n /= 1024.0


def slurm_log_files(log_dir):
    """This job's SLURM output/error files (names as written by setup_sims.py)."""
    if not log_dir:
        return []
    array, task = os.environ.get("SLURM_ARRAY_JOB_ID"), os.environ.get("SLURM_ARRAY_TASK_ID")
    tag = "%s_%s" % (array, task) if array and task else os.environ.get("SLURM_JOB_ID")
    if not tag:
        return []
    return [os.path.join(log_dir, "sim_%s.%s" % (kind, tag)) for kind in ("output", "error")]


def total_size(patterns, extra):
    files = set(extra)
    for pattern in patterns:
        files.update(glob.glob(pattern))
    total = 0
    for path in files:
        try:
            total += os.path.getsize(path)
        except OSError:
            pass
    return total


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", required=True, help="maximum total size of the log files, e.g. 1G")
    p.add_argument("--marker", required=True, help="file written when the limit is exceeded")
    p.add_argument("--logs", action="append", default=[], help="glob pattern of log files (repeatable)")
    p.add_argument("--slurm-logs", help="directory of the SLURM output/error files")
    p.add_argument("--interval", type=float, default=10.0, help="seconds between checks")
    p.add_argument("command", nargs=argparse.REMAINDER, help="-- command to run")
    args = p.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        p.error("no command given")
    limit = parse_size(args.limit)
    extra = slurm_log_files(args.slurm_logs)

    child = subprocess.Popen(command, start_new_session=True)     # own process group: cosima, tee, ...
    while True:
        try:
            return child.wait(timeout=args.interval)
        except subprocess.TimeoutExpired:
            pass
        size = total_size(args.logs, extra)
        if size <= limit:
            continue
        message = ("log files reached %s, above the limit of %s (slurm.max_log_size); the job was stopped. "
                   "Look at the start of the cosima/revan terminal output for what is filling it."
                   % (human(size), human(limit)))
        try:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=60)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        except ProcessLookupError:
            pass
        os.makedirs(os.path.dirname(os.path.abspath(args.marker)), exist_ok=True)
        with open(args.marker, "w") as f:
            f.write(message + "\n")
        sys.stderr.write("ERROR: %s\n" % message)
        print("ERROR: %s" % message, flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
