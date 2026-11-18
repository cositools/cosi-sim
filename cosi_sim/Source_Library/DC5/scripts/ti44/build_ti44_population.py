"""
Build the DC5 44Ti SNR population from A. Anaya's population synthesis (popsyn/).

Usage: python3 build_ti44_population.py <cosi-sim repo root> <seed>

popsyn/spatial/map<k>.csv (19 files) each list 8-9 SNRs (l, b, flux): the 5 known young SNRs
(SN 1987A, Tycho, Kepler, Vela Jr, G1.9+0.3) at their real positions with population-synthesis
fluxes, and 3-4 SNRs at random positions. popsyn/spectra/spectrum<i>.dat (48 files) are 44Ti
1157 keV line profiles. One map is drawn at random, and every SNR in it gets a different random
spectrum (template.source). Flux is the line flux over the spectrum range (1110-1205 keV), in
ph/cm2/s. Cas A is not in the maps; DC5 reuses the DC4 Cas A (CasAG16distribution).

Writes Source_Library/DC5/sources/Nucleosynthesis/Ti44_SNR_population/ (one source file with one
component per SNR, the spectra used, README_DC5.md), Source_Library/DC5/DC5_ti44_draw.json, and the
entry in DC5_build_log.json. Run after build_dc5.py; the same seed gives the same files.
"""
import csv, glob, json, os, random, re, shutil, sys
import numpy as np

REPO, SEED = sys.argv[1], int(sys.argv[2])
rng = random.Random(SEED + 44)
HERE = os.path.dirname(os.path.abspath(__file__))
POP = os.path.join(HERE, "popsyn")
DC5 = os.path.join(REPO, "cosi_sim", "Source_Library", "DC5")
NAME = "Ti44_SNR_population"
OUT = os.path.join(DC5, "sources", "Nucleosynthesis", NAME)
HEADER = """# Define DC5 sim settings (optimizes sim time):
DefaultRangeCut 0.005
Region Spacecraft
Spacecraft.Volume SCbody
Spacecraft.RangeCut 1.

Region Pipebody
Pipebody.Volume PIPbody
Pipebody.RangeCut 1.

"""
# The 5 known SNRs, in the order and at the positions of every map (same positions as the DC4 sources)
KNOWN = [("SN1987A", "SN 1987A", 279.7, -31.9), ("Tycho", "Tycho", 120.1, 1.4), ("Kepler", "Kepler", 4.5, 6.8),
         ("VelaJr", "Vela Jr", 266.3, -1.2), ("G1p9p0p3", "G1.9+0.3", 1.9, 0.3)]
C_KMS = 299792.458
E0 = 1157.02


def number(path):
    return int(re.findall(r"(\d+)\.\w+$", path)[0])


def line_stats(path):
    """Centroid (keV) and the velocity range (km/s) where the profile is non-zero."""
    dp = np.array([ln.split()[1:3] for ln in open(path) if ln.startswith("DP")], float)
    e, y = dp[:, 0], dp[:, 1]
    centroid = np.trapezoid(y * e, e) / np.trapezoid(y, e)
    nz = e[y > 0]
    return centroid, (nz[0] / E0 - 1) * C_KMS, (nz[-1] / E0 - 1) * C_KMS


maps = sorted(glob.glob(os.path.join(POP, "spatial", "map*.csv")), key=number)
spectra = sorted(glob.glob(os.path.join(POP, "spectra", "spectrum*.dat")), key=number)
mapfile = rng.choice(maps)
snrs = list(csv.DictReader(open(mapfile)))
for (_, _, l, b), r in zip(KNOWN, snrs):
    assert (float(r["l"]), float(r["b"])) == (l, b), (mapfile, r)
picked = rng.sample(spectra, len(snrs))

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
src, rows = HEADER, []
for k, (r, spec) in enumerate(zip(snrs, picked)):
    if k < len(KNOWN):
        comp, label = "Ti44_" + KNOWN[k][0], KNOWN[k][1]
    else:
        comp, label = "Ti44_popSNR%d" % (k - len(KNOWN) + 1), "population-synthesis SNR %d" % (k - len(KNOWN) + 1)
    l, b, flux = float(r["l"]) % 360.0, float(r["b"]), float(r["flux"])
    spec_name = "Ti44_" + os.path.basename(spec)
    shutil.copy2(spec, os.path.join(OUT, spec_name))
    centroid, v_lo, v_hi = line_stats(spec)
    src += (f"# {label}\n"
            f"DataChallenge.Source          {comp}\n"
            f"{comp}.ParticleType               1\n"
            f"{comp}.Beam                       FarFieldPointSource 0 0\n"
            f"{comp}.Orientation                Galactic Fixed {b:.6f} {l:.6f}\n"
            f"{comp}.Spectrum                   File {spec_name}\n"
            f"{comp}.Flux                       {flux:.6g}\n"
            f"{comp}.EarthOccultation false\n\n")
    rows.append(dict(component=comp, snr=label, l=round(l, 4), b=round(b, 4), flux=flux, spectrum=spec_name,
                     centroid_keV=round(centroid, 2), v_min_kms=round(v_lo), v_max_kms=round(v_hi)))
open(os.path.join(OUT, NAME + ".source"), "w").write(src)

total = sum(r["flux"] for r in rows)
draw = dict(seed=SEED, rng="random.Random(seed + 44)", map=os.path.basename(mapfile), n_snr=len(rows),
            total_flux=total, snrs=rows)
json.dump(draw, open(os.path.join(DC5, "DC5_ti44_draw.json"), "w"), indent=1)

table = "\n".join(f"| `{r['component']}` | {r['snr']} | {r['l']:.2f} | {r['b']:.2f} | {r['flux']:.3g} | `{r['spectrum']}` | "
                  f"{r['centroid_keV']:.1f} | {r['v_min_kms']:+.0f} to {r['v_max_kms']:+.0f} |" for r in rows)
open(os.path.join(OUT, "README_DC5.md"), "w").write(f"""# 44Ti SNR population — DC5

**DC5 status:** new (population synthesis, A. Anaya)
**Draw:** `{draw['map']}` of the 19 population-synthesis maps, with a random spectrum for each SNR (seed {SEED}; `DC5/DC5_ti44_draw.json`)

## Model

Young supernova remnants seen in the 44Ti 1157 keV line, from a population synthesis by A. Anaya. The map gives
the 5 known young SNRs (SN 1987A, Tycho, Kepler, Vela Jr, G1.9+0.3) at their real positions with population-synthesis
fluxes, plus {len(rows) - len(KNOWN)} SNRs at random positions. Some may be below the detection threshold. Each SNR is a point
source with its own line profile (`Ti44_spectrum*.dat`, broadened and shifted by its ejecta velocities); Flux is the
line flux over the spectrum range (1110–1205 keV). Total: {total:.3g} ph/cm²/s.

| Component | SNR | l (deg) | b (deg) | Flux (ph/cm²/s) | Spectrum | Centroid (keV) | Line extent (km/s) |
|---|---|---|---|---|---|---|---|
{table}

Cas A is not part of the map: DC5 reuses the DC4 Cas A model (`DC4/sources/Nucleosynthesis/CasAG16distribution`).

## Change relative to the DC4 mock dataset

New. It replaces the DC4 models of SN 1987A, Tycho, Kepler, Vela Jr and G1.9+0.3 (all below the detection threshold
in the DC4 analysis).

The template files and the script are in `DC5/scripts/ti44/`.

_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/Nucleosynthesis/{NAME}`._
""")

logf = os.path.join(DC5, "DC5_build_log.json")
log = json.load(open(logf))
log[NAME] = dict(status="new (population synthesis)", skip_readme=True, flux=total,
                 change=f"44Ti SNR population (A. Anaya): {draw['map']}, {len(rows)} SNRs (the 5 known young SNRs with "
                        f"population-synthesis fluxes and {len(rows) - len(KNOWN)} at random positions), each with a random "
                        f"1157 keV line profile; total {total:.3g} ph/cm2/s. Replaces the DC4 SN 1987A, Tycho, Kepler, Vela Jr "
                        f"and G1.9+0.3 models")
json.dump(log, open(logf, "w"), indent=1, default=float)
print(f"{draw['map']}: {len(rows)} SNRs, total {total:.3g} ph/cm2/s -> {OUT}")
for r in rows:
    print("  %-18s %-30s l=%8.3f b=%7.3f flux=%.3g %s" % (r["component"], r["snr"], r["l"], r["b"], r["flux"], r["spectrum"]))
