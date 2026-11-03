"""
Draw DC5 GRB times, spectral and polarization parameters (Request 5).

Usage: python3 draw_dc5_grbs.py <cosi-sim repo root> <orientation file (.ori or .ori.gz)> [seed]

For every DC4 "GRB_bn" burst:
  * position: unchanged (sky location of the DC4 model)
  * time: new trigger time between day 4 and day 7 of the observation (t_start + 3 d ... t_start + 7 d),
    chosen so that the off-axis angle (COSI z-axis to source) follows the DC4 GRB off-axis distribution,
    the source is in the field of view and above the Earth limb, and there is no SAA (livetime > 0)
    from 5 min before to 5 min after the burst
  * spectrum: same model (Band or power law), parameters drawn from the Fermi GBM 10-yr spectral catalog
    (Poolakkil et al. 2021) fluence-spectrum distributions; photon flux (100 keV-10 MeV) unchanged
  * polarization: fraction drawn from the DC4 distribution (stratified uniform on [0, 0.9]),
    angle uniform in [0, 180) deg
Magnetar bursts (MGF*, MgtBurst*) are unchanged; half of the DC4 ones are kept.
"""
import os, sys, re, json, random, secrets
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ori_tools import load_ori, geometry

REPO, ORI = sys.argv[1], sys.argv[2]
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else secrets.randbits(32)
rng = np.random.default_rng(SEED)
LIB = os.path.join(REPO, "cosi_sim", "Source_Library")
SRC = os.path.join(LIB, "DC3", "sources", "GRBs")

DC4_GRBS = ["bn081207680", "bn090424592", "bn100612726", "bn110605183", "bn131122490", "bn140329295",
            "bn161004964", "bn170405777", "bn180504136", "bn180703876", "bn080802386"]
SHORT = {"bn080802386"}          # T90 < 2 s -> short-GRB parameter distributions
DC4_MAGNETAR = ["MGF051103", "MGF070201", "MGF070222", "MGF180128A", "MGF200415A", "MGF231115A",
                "MgtBurst_bright_complex"]

# ---------------------------------------------------------------- constraints
FOV_MAX = 60.0          # deg, max off-axis angle (DC4 maximum 59.7 deg)
ZENITH_MAX = 100.0      # deg, source must be well above the Earth limb (occultation at ~113 deg)
WIN = (3.0, 7.0)        # days after the start of the orientation file -> days 4-7
SAA_MARGIN = 300.0      # s of livetime required before and after the burst
SPACING = 3600.0        # s minimum separation between two GRBs
OA_TOL = 2.0            # deg tolerance on the target off-axis angle
SLEW_TOL = 3.0          # deg, max change of the off-axis angle during the burst (avoids slews)

ori = load_ori(ORI)
T0 = ori["t"][0]

def parse(name):
    s = open(os.path.join(SRC, name, name + ".source")).read()
    b, l = map(float, re.search(r"Orientation\s+Galactic Fixed\s+(\S+)\s+(\S+)", s).groups())
    lcf = re.search(r"Lightcurve\s+File\s+\S+\s+(\S+)", s).group(1)
    lc = np.array([[float(x) for x in r.split()[1:3]] for r in open(os.path.join(SRC, name, lcf)) if r.startswith("DP")])
    sp = re.search(r"\.Spectrum\s+(.*)", s).group(1).split()
    pol = re.search(r"\.Polarization\s+galactic\s+(\S+)\s+(\S+)", s).groups()
    return dict(name=name, l=l, b=b, lc_file=lcf, t0=lc[0, 0], t1=lc[-1, 0], spectrum=sp,
                flux=float(re.search(r"\.Flux\s+(\S+)", s).group(1)), pol=(float(pol[0]), float(pol[1])))

grbs = [parse(n) for n in DC4_GRBS]

# ---------------------------------------------------------------- DC4 off-axis distribution
for g in grbs:
    oa, zen, live, _ = geometry(ori, g["l"], g["b"], np.array([g["t0"]]))
    g["dc4_offaxis"], g["dc4_zenith"] = float(oa[0]), float(zen[0])
dc4_oa = np.array([g["dc4_offaxis"] for g in grbs])

# Candidate trigger times (every 15 s bin start in the window) and their geometry, per GRB
tgrid = ori["t"][(ori["t"] >= T0 + WIN[0] * 86400) & (ori["t"] <= T0 + WIN[1] * 86400)]
live_t, live_v = ori["t"], ori["live"]
def live_ok(ta, tb):
    i0 = np.searchsorted(live_t, ta - SAA_MARGIN, side="right") - 1
    i1 = np.searchsorted(live_t, tb + SAA_MARGIN, side="right")
    return np.all(live_v[max(i0, 0):i1] > 0)

for g in grbs:
    dur = g["t1"] - g["t0"]
    oa0, zen0, _, _ = geometry(ori, g["l"], g["b"], tgrid)
    oa1, zen1, _, _ = geometry(ori, g["l"], g["b"], tgrid + dur)
    ok = (np.maximum(oa0, oa1) <= FOV_MAX) & (np.maximum(zen0, zen1) <= ZENITH_MAX) & (np.abs(oa1 - oa0) <= SLEW_TOL)
    g["cand"] = dict(t=tgrid[ok], oa=oa0[ok], zen=zen0[ok])
    g["min_oa"] = float(oa0[ok].min()) if ok.any() else np.inf

# Target off-axis angles: the DC4 set, jittered by +-3 deg and re-assigned at random among the GRBs.
# Then pick each trigger time at random among the times matching the target, with SAA margins and
# GRB spacing enforced. Targets are redrawn if a GRB cannot be scheduled.
def schedule():
    targets = np.clip(dc4_oa + rng.uniform(-3, 3, len(dc4_oa)), 0.5, FOV_MAX - 1)
    perm = rng.permutation(len(grbs))
    chosen, picks = [], []
    for g, p in zip(grbs, perm):
        c = g["cand"]
        idx = np.where(np.abs(c["oa"] - targets[p]) <= OA_TOL)[0]
        pick = None
        for i in rng.permutation(idx):
            t = round(c["t"][i] + rng.uniform(0, 15), 3)   # random sub-bin offset, ms precision
            if live_ok(t, t + g["t1"] - g["t0"]) and all(abs(t - u) > SPACING for u in chosen):
                pick = t; break
        if pick is None: return None
        chosen.append(pick); picks.append((pick, float(targets[p])))
    return picks

for attempt in range(5000):
    picks = schedule()
    if picks: break
else:
    raise RuntimeError("could not schedule GRBs")
for g, (t, tgt) in zip(grbs, picks):
    g["t0_new"], g["target_oa"] = t, tgt

# ---------------------------------------------------------------- spectra (Poolakkil et al. 2021, Table 4)
def draw_band(short):
    if short:   # short GRBs: alpha -0.46 (+0.68 -0.37), Epeak 413 (+651 -263) keV
        a = float(np.clip(rng.normal(-0.46, 0.45), -1.2, -0.05))
        ep = float(np.clip(10 ** rng.normal(np.log10(413), 0.35), 150, 2000))
    else:       # long GRBs: alpha -0.84 (+0.48 -0.35), Epeak 144 (+229 -85) keV
        a = float(np.clip(rng.normal(-0.84, 0.35), -1.5, -0.3))
        ep = float(np.clip(10 ** rng.normal(np.log10(144), 0.38), 60, 1200))
    # beta: BEST fluence sample -2.20 (+0.26 -0.29); long-GRB tail toward steep values
    b = float(np.clip(rng.normal(-2.3, 0.3), -3.2, -1.95))
    return a, b, ep

for g in grbs:
    sp = g["spectrum"]
    if sp[0] == "Band":
        a, b, ep = draw_band(g["name"] in SHORT)
        g["spectrum_new"] = ["Band", sp[1], sp[2], f"{a:.4f}", f"{b:.4f}", f"{ep:.2f}"]
    elif sp[0] == "PowerLaw":
        # MEGAlib power law index (positive). Above ~100 keV the photon index of GBM bursts is set by the
        # high-energy slope: use the beta distribution (2.2-2.4 typical)
        idx = float(np.clip(rng.normal(2.3, 0.25), 1.9, 2.9))
        g["spectrum_new"] = ["PowerLaw", sp[1], sp[2], f"{idx:.4f}"]
    else:
        raise RuntimeError(sp)

# ---------------------------------------------------------------- polarization
dc4_pf = np.array([g["pol"][0] for g in grbs])
n = len(grbs)
pf = (np.arange(n) + rng.uniform(0, 1, n)) * (dc4_pf.max() / n)   # stratified uniform on [0, 0.9]
pf = rng.permutation(np.round(pf, 2))
for g, f in zip(grbs, pf):
    g["pol_new"] = (float(f), float(round(rng.uniform(0, 180), 1)))

# ---------------------------------------------------------------- magnetar bursts: keep half
keep = sorted(rng.choice(DC4_MAGNETAR, size=(len(DC4_MAGNETAR) + 1) // 2, replace=False).tolist())

# ---------------------------------------------------------------- record + final geometry check
res = dict(seed=SEED, orientation_start=T0, window_days=WIN, constraints=dict(
    fov_max_deg=FOV_MAX, zenith_max_deg=ZENITH_MAX, saa_margin_s=SAA_MARGIN, spacing_s=SPACING),
    dc4_offaxis=sorted(dc4_oa.round(2).tolist()), magnetar_kept=keep,
    magnetar_removed=sorted(set(DC4_MAGNETAR) - set(keep)), grbs={})
for g in grbs:
    dur = g["t1"] - g["t0"]
    oa, zen, live, _ = geometry(ori, g["l"], g["b"], np.array([g["t0_new"], g["t0_new"] + dur]))
    assert oa.max() <= FOV_MAX and zen.max() <= ZENITH_MAX and live_ok(g["t0_new"], g["t0_new"] + dur)
    res["grbs"][g["name"]] = dict(
        l=g["l"], b=g["b"], duration_s=dur, lc_file=g["lc_file"],
        dc4=dict(t0=g["t0"], day=(g["t0"] - T0) / 86400 + 1, offaxis=g["dc4_offaxis"], zenith=g["dc4_zenith"],
                 spectrum=g["spectrum"], flux=g["flux"], pol=g["pol"]),
        dc5=dict(t0=g["t0_new"], day=(g["t0_new"] - T0) / 86400 + 1, offaxis=float(oa[0]), offaxis_end=float(oa[1]),
                 zenith=float(zen[0]), target_offaxis=g["target_oa"], spectrum=g["spectrum_new"], flux=g["flux"],
                 pol=g["pol_new"], shift_s=g["t0_new"] - g["t0"]))
print(json.dumps(res, indent=1))
