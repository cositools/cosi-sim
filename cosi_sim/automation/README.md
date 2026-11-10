# Automated simulation pipeline (SLURM)

Two scripts run the full cosi-sim workflow for a list of library sources, from directory setup to the final SAA-cut FITS file:

| Script | Runs in | Does |
|---|---|---|
| `setup_sims.py` | MEGAlib / cosi-sim environment | makes `<sim_root>/<class>/<source>/` with `inputs.yaml`, `cosipy_inputs.yaml`, `Sources/`, `Simulations/sim_<i>/` and the job scripts |
| `run_pipeline.py` | any `python3` (standard library only) | submits the jobs, checks them, resubmits failures, runs mimrec, the overflow filter and cosipy, and copies the final file |

Everything that is specific to you (paths, environments, SLURM settings) is in one config file, `pipeline_config.yaml`.

## Quick start

```bash
cp pipeline_config.yaml my_config.yaml        # fill in your paths
cp templates/inputs.yaml templates/cosipy_inputs.yaml /my/templates/   # or use your own

# 1. Set up (in the MEGAlib environment, where cosi_sim is installed):
python setup_sims.py -c my_config.yaml --list sources.txt --dry-run   # check the list
python setup_sims.py -c my_config.yaml --list sources.txt

# 2. Submit and follow:
python run_pipeline.py submit /path/to/simulations
python run_pipeline.py status /path/to/simulations
```

`sources.txt` has one library path per line; `#` starts a comment, and an optional second word forces the mode:

```
DC5/sources/Galactic/cygX3
DC5/sources/Galactic/magnetar2
DC5/sources/GRBs/bn081207680
DC4/sources/Galactic/Crab      flux
```

Sources can also be given on the command line instead of `--list`.

## The three modes

The mode is chosen from the library source file:

| Mode | When | Simulation | Notes |
|---|---|---|---|
| `time` | no light curve | `num_sims` time chunks (+1 if the orientation file does not divide evenly), one array task each | orientation bins from `cosi_sim.pipeline.make_orientation_bins`, as `run_parallel_sims.py` |
| `flux` | `.Lightcurve` in the source file | `num_sims` runs of the full exposure | every `.Flux` in the copied source file is divided by `num_sims` (the library file is not changed) |
| `grb` | source under a `GRBs/` category | one job | uses the `*_normed.ori` in the source directory |

Each sim runs exactly the steps of `run_sims.py`: `define_sim()`, `run_cosima(seed=random)` (the seed is saved in `cosima_seed.txt`), `run_revan(geo_file=revan_geometry)`.

## Light curves

**Times relative to t_ref.** MEGAlib has trouble with light curves at large absolute times: short bursts, and repeating light curves with periods below ~0.86 s (the number of repeats is stored in a 32-bit integer). Such library sources store their light curves in times t − t_ref (`*_shifted.dat`, made with `python -m cosi_sim.pipeline.time_reference`) and have a `sim_time_reference.txt`. In any mode, these sources are simulated in t − t_ref:
- **GRBs** use the `*_normed.ori` in the source directory.
- **Other sources** use the template orientation file shifted by t_ref. It is written once to `<sim_root>` and shared.

Each job then runs `modify_sim_times(..., t_ref)`, so the events get their absolute times back, and revan, mimrec and cosipy work on `fixed_times`.

**Start and stop times.** A light curve that does not repeat must have the same start and stop times as the orientation file of the simulation. For bursts (`grb` mode), it must lie inside it. Otherwise `setup_sims.py` skips the source and says why (also with `--dry-run`); `Setup.setup_srcs()` stops with the same error.

## What happens after `submit`

For each source, `submit` sends the simulation job (array or single) and a post-processing job that waits for it with `--dependency=afterany`. No job sits idle polling the queue. The post-processing job runs `run_pipeline.py finish <run_dir>`:

1. **check**: each sim must have `<name>.inc1.id1.tra.gz` and a revan terminal output ending with "Event reconstruction finished" (the `check_revan_parallel` criteria). Failed sims are resubmitted automatically as a smaller array, together with a new post-processing job, up to `slurm.max_retries` times. The result is in `check_report.txt`.
2. **mimrec**: in the MEGAlib environment, `run_mimrec(extract_root=True)` on the combined tra file, then `OverflowFilter.py`.
3. **plots**: in the MEGAlib environment, `plot_spectrum`, `plot_lc` and `plot_image` from the mimrec extraction. The figures (`spectra.pdf`, `LCs.pdf`, `sim_image.png`) go to `<products_dir>/Images/<class>/<source>/`. If a plot fails, the history says so and the pipeline continues; `finish` makes the missing plots later.
4. **cosipy**: in the cosipy environment, `UnBinnedData.read_tra` and `cut_SAA_events`.
5. **copy**: the `*_with_SAAcut` file goes to `products_dir`.

Each environment is sourced in a fresh login shell, as after logging in again, so the environment you submitted from does not carry over (your `~/.bashrc` is loaded, as at a normal login). Progress is stored in `<run_dir>/automation.json`. Logs are in `<run_dir>/logs/`.

## Commands

```bash
python run_pipeline.py submit   <dirs> [--max-jobs N | --no-queue | --chain] [--dry-run] [--force]
python run_pipeline.py fill     <sim_root>
python run_pipeline.py status   <dirs>
python run_pipeline.py check    <dirs>
python run_pipeline.py finish   <run_dir> [--from check|mimrec|plots|cosipy|copy] [--no-resubmit]
python run_pipeline.py resubmit <run_dir> [--all]
python run_pipeline.py cancel   <dirs>
```

`<dirs>` can be source directories or any directory above them (the simulation root, a class directory).

- `--max-jobs N` (or `slurm.max_jobs` in the config) turns on rolling submission, below. `--no-queue` ignores `slurm.max_jobs` and submits everything at once.
- `--chain` starts each source's sims only after the previous source's sims have ended. This limits how many jobs *run* at once, but all chained jobs are still *submitted* (pending), so it does not help with a limit on submitted jobs such as Palmetto's.
- `finish` can be run by hand (e.g. on an interactive node). It continues from the first step that has not completed; for a source finished before the plots step existed, it makes only the plots.
- `resubmit` resubmits only the failed sims, plus a new post-processing job, and resets the automatic retry count.

## Rolling submission (job limits)

SLURM clusters usually cap how many jobs one user can have pending + running, and every array task counts. On Palmetto 2 the `normal` QOS of the `work1` partition has `MaxSubmitPU = 3000`, so with `num_sims: 1000` (about 1002 jobs per source) only two sources fit at once; a third `sbatch` is rejected. Check your cluster with:

```bash
scontrol show partition work1 | grep -i qos
sacctmgr show qos format=name%20,maxsubmitpu,maxjobspu
```

Set `slurm.max_jobs` a little below that limit (e.g. 2900, leaving room for resubmissions and interactive jobs) and submit everything once:

```bash
python run_pipeline.py submit /path/to/simulations
```

The sources go into a queue file, `<sim_root>/pipeline_queue.json`, and are submitted in order while your total job count (`squeue`, all your jobs) stays at or below `max_jobs`. A smaller source, such as a GRB, can go ahead of a large one that does not fit yet. Each post-processing job submits the next waiting sources once its own sims have left the queue (after the check step), and again when it ends. There is no polling: at most two `squeue` calls per post-processing job.

Waiting sources show as `waiting` in `status`. If none of a queue's sources is running (e.g. your other jobs used the whole budget when you submitted), nothing will submit the waiting ones; `status` then tells you to run `run_pipeline.py fill <sim_root>`. `cancel` on a waiting source removes it from the queue.

`max_jobs` is saved with each source when `setup_sims.py` runs, and `submit` uses the value of the sources it is about to submit (sources already submitted or finished are ignored). So if you turn on rolling submission after setting some sources up, either rerun `setup_sims.py --force` for the ones not yet submitted, or pass `--max-jobs 2900` to `submit`.

## Notes

- `setup_sims.py` refuses to redo a source that is already set up unless `--force` is given (this deletes its `Simulations/`).
- Library files stored as `.dat.gz` (thin-disk maps, magnetar light curves) are gunzipped in place in the source library, as `setup_srcs()` needs them unzipped.
- The generated `run_sims.py`, `post_megalib.py`, `post_cosipy.py` and `*.sh` files are plain scripts that can be read, edited or run by hand.
