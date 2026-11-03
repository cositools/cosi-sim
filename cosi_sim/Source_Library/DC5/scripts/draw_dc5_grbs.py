"""
Draw DC5 GRB times, spectral and polarization parameters (Request 5).

Usage: python3 draw_dc5_grbs.py <cosi-sim repo root> <orientation file (.ori or .ori.gz)> [seed]

For every DC4 "GRB_bn" burst:
  * time: new trigger time between day 4 and day 7 of the observation (t_start + 3 d ... t_start + 7 d);
    the whole burst (last light-curve time stamp) ends by t_start + 7 d = 1836092100.0 for DC4/DC5
  * position: new; placed at an off-axis angle (COSI z-axis to source) drawn from the DC4 GRB
    off-axis distribution, at a random azimuth around the z-axis at the trigger time; required to stay
    in the field of view and above the Earth limb, with no SAA (livetime > 0) from 5 min before to
    5 min after the burst
  * flux: DC4 photon flux (100 keV-10 MeV) times a log-uniform factor in [0.5, 2] (in [0.5, 1] for the
    two artificially bright DC4 bursts above 100 ph/cm2/s, so they do not become brighter)
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
T_END_MAX = None        # set below: t_start + 7 d (the burst must end inside the first week)

ori = load_ori(ORI)
T0 = ori["t"][0]
T_END_MAX = T0 + WIN[1] * 86400        # 1836092100.0 for the DC4 orientation file

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

live_t, live_v = ori["t"], ori["live"]
def live_ok(ta, tb):
    i0 = np.searchsorted(live_t, ta - SAA_MARGIN, side="right") - 1
    i1 = np.searchsorted(live_t, tb + SAA_MARGIN, side="right")
    return np.all(live_v[max(i0, 0):i1] > 0)

def axes(t):
    """Spacecraft x, y, z unit vectors (Galactic cartesian) at time t (orientation bin containing t)."""
    i = np.searchsorted(ori["t"], t, side="right") - 1
    lx, bx, lz, bz = np.radians([ori["xl"][i], ori["xb"][i], ori["zl"][i], ori["zb"][i]])
    x = np.array([np.cos(bx)*np.cos(lx), np.cos(bx)*np.sin(lx), np.sin(bx)])
    z = np.array([np.cos(bz)*np.cos(lz), np.cos(bz)*np.sin(lz), np.sin(bz)])
    x -= (x @ z) * z; x /= np.linalg.norm(x)
    return x, np.cross(z, x), z

def to_lb(v):
    return float(np.degrees(np.arctan2(v[1], v[0])) % 360), float(np.degrees(np.arcsin(np.clip(v[2], -1, 1))))

# Target off-axis angles: the DC4 set, jittered by +-3 deg and re-assigned at random among the GRBs.
# For each GRB: random trigger time in the window (burst must end by T_END_MAX), then a source position
# at the target off-axis angle and a random azimuth around the z-axis. Accepted if the burst stays in
# the field of view, above the Earth limb, outside the SAA (with margins), not during a slew, and is
# >= SPACING from the other GRBs. The draw restarts if a GRB cannot be placed.
tgrid = ori["t"][(ori["t"] >= T0 + WIN[0] * 86400) & (ori["t"] < T_END_MAX)]
def schedule():
    targets = np.clip(dc4_oa + rng.uniform(-3, 3, len(dc4_oa)), 0.5, FOV_MAX - 1)
    perm = rng.permutation(len(grbs))
    chosen, picks = [], []
    for g, p in zip(grbs, perm):
        dur = g["t1"] - g["t0"]
        th = np.radians(targets[p]); pick = None
        for _ in range(4000):
            t = round(float(rng.choice(tgrid)) + rng.uniform(0, 15), 3)   # ms precision
            if t + dur > T_END_MAX - SAA_MARGIN: continue                  # burst + margin inside week 1
            if not live_ok(t, t + dur) or any(abs(t - u) < SPACING for u in chosen): continue
            x, y, z = axes(t); ph = rng.uniform(0, 2 * np.pi)
            l, b = to_lb(np.cos(th) * z + np.sin(th) * (np.cos(ph) * x + np.sin(ph) * y))
            oa, zen, _, _ = geometry(ori, l, b, np.array([t, t + dur]))
            if oa.max() <= FOV_MAX and zen.max() <= ZENITH_MAX and abs(oa[1] - oa[0]) <= SLEW_TOL:
                pick = (t, l, b); break
        if pick is None: return None
        chosen.append(pick[0]); picks.append((*pick, float(targets[p])))
    return picks

for attempt in range(200):
    picks = schedule()
    if picks: break
else:
    raise RuntimeError("could not schedule GRBs")
for g, (t, l, b, tgt) in zip(grbs, picks):
    g["t0_new"], g["l_new"], g["b_new"], g["target_oa"] = t, round(l, 4), round(b, 4), tgt

# ---------------------------------------------------------------- flux
for g in grbs:
    hi = 1.0 if g["flux"] > 100 else 2.0
    g["flux_new"] = float(f"{g['flux'] * np.exp(rng.uniform(np.log(0.5), np.log(hi))):.6g}")

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
# Fixed to the selection of the first DC5 GRB draw (seed 2367866795), reviewed and kept by the DC5 lead.
# To redraw: sorted(rng.choice(DC4_MAGNETAR, size=(len(DC4_MAGNETAR) + 1) // 2, replace=False).tolist())
keep = ["MGF051103", "MGF180128A", "MGF200415A", "MgtBurst_bright_complex"]

# ---------------------------------------------------------------- record + final geometry check
res = dict(seed=SEED, orientation_start=T0, window_days=WIN, t_end_max=T_END_MAX, constraints=dict(
    fov_max_deg=FOV_MAX, zenith_max_deg=ZENITH_MAX, saa_margin_s=SAA_MARGIN, spacing_s=SPACING),
    dc4_offaxis=sorted(dc4_oa.round(2).tolist()), magnetar_kept=keep,
    magnetar_removed=sorted(set(DC4_MAGNETAR) - set(keep)), grbs={})
for g in grbs:
    dur = g["t1"] - g["t0"]
    oa, zen, live, _ = geometry(ori, g["l_new"], g["b_new"], np.array([g["t0_new"], g["t0_new"] + dur]))
    assert oa.max() <= FOV_MAX and zen.max() <= ZENITH_MAX and live_ok(g["t0_new"], g["t0_new"] + dur)
    assert g["t0_new"] + dur <= T_END_MAX
    res["grbs"][g["name"]] = dict(
        duration_s=dur, lc_file=g["lc_file"],
        dc4=dict(l=g["l"], b=g["b"], t0=g["t0"], day=(g["t0"] - T0) / 86400 + 1, offaxis=g["dc4_offaxis"],
                 zenith=g["dc4_zenith"], spectrum=g["spectrum"], flux=g["flux"], pol=g["pol"]),
        dc5=dict(l=g["l_new"], b=g["b_new"], t0=g["t0_new"], t_end=g["t0_new"] + dur,
                 day=(g["t0_new"] - T0) / 86400 + 1, offaxis=float(oa[0]), offaxis_end=float(oa[1]),
                 zenith=float(zen[0]), target_offaxis=g["target_oa"], spectrum=g["spectrum_new"], flux=g["flux_new"],
                 pol=g["pol_new"], shift_s=g["t0_new"] - g["t0"]))
print(json.dumps(res, indent=1))
