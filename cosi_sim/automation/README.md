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
| `grb` | source under a `GRBs/` category | one job | uses the `*_normed.ori` in the source directory, `modify_sim_times(..., t_ref)` with t_ref from `sim_time_reference.txt`, then revan on `fixed_times` |

Each sim runs exactly the steps of `run_sims.py`: `define_sim()`, `run_cosima(seed=random)` (the seed is saved in `cosima_seed.txt`), `run_revan(geo_file=revan_geometry)`.

## What happens after `submit`

For each source, `submit` sends the simulation job (array or single) and a post-processing job that waits for it with `--dependency=afterany`. No job sits idle polling the queue. The post-processing job runs `run_pipeline.py finish <run_dir>`:

1. **check**: each sim must have `<name>.inc1.id1.tra.gz` and a revan terminal output ending with "Event reconstruction finished" (the `check_revan_parallel` criteria). Failed sims are resubmitted automatically as a smaller array, together with a new post-processing job, up to `slurm.max_retries` times. The result is in `check_report.txt`.
2. **mimrec**: in the MEGAlib environment, `run_mimrec(extract_root=True)` on the combined tra file, then `OverflowFilter.py`.
3. **cosipy**: in the cosipy environment, `UnBinnedData.read_tra` and `cut_SAA_events`.
4. **copy**: the `*_with_SAAcut` file goes to `products_dir`.

Progress is stored in `<run_dir>/automation.json`. Logs are in `<run_dir>/logs/`.

## Commands

```bash
python run_pipeline.py submit   <dirs> [--chain] [--dry-run] [--force]
python run_pipeline.py status   <dirs>
python run_pipeline.py check    <dirs>
python run_pipeline.py finish   <run_dir> [--from check|mimrec|cosipy|copy] [--no-resubmit]
python run_pipeline.py resubmit <run_dir> [--all]
python run_pipeline.py cancel   <dirs>
```

`<dirs>` can be source directories or any directory above them (the simulation root, a class directory).

- `--chain` starts each source's sims only after the previous source's sims have ended. Use it to queue many sources without exceeding per-user job limits.
- `finish` can be run by hand (e.g. on an interactive node). It continues from the first step that has not completed.
- `resubmit` resubmits only the failed sims, plus a new post-processing job, and resets the automatic retry count.

## Notes

- `setup_sims.py` refuses to redo a source that is already set up unless `--force` is given (this deletes its `Simulations/`).
- Library files stored as `.dat.gz` (thin-disk maps, magnetar light curves) are gunzipped in place in the source library, as `setup_srcs()` needs them unzipped.
- The time-chunk array size is the number of orientation bins actually written, so the extra bin made when the orientation file does not divide evenly is also simulated.
- `run_mimrec` gets the revan geometry explicitly, because it runs in a new Python process.
- The generated `run_sims.py`, `post_megalib.py`, `post_cosipy.py` and `*.sh` files are plain scripts that can be read, edited or run by hand.
