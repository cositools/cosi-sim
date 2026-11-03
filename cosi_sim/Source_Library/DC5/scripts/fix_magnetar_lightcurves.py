"""
Fix the periodic light curves of 1RXSJ170849 and magnetar2 (DC4 bug: the repeated light-curve
segment did not contain a whole number of rotations, so the pulse phase jumped at every repeat).

Usage: python3 fix_magnetar_lightcurves.py <cosi-sim repo root>

The DC4 files sample 1 + 0.5 sin(2 pi t / P) at ~1 s with a constant period P (11.00502461 s for
1RXS J170849, half of that for magnetar2). The file is cut at t_end = N * P (N = number of whole
periods it contains) and a final point is added at t_end with the phase-0 value, so that a periodic
repeat (Lightcurve File true) keeps the pulse phase continuous. Written to the DC5 copies only.
"""
import os, sys, gzip, json
import numpy as np

REPO = sys.argv[1]
G = os.path.join(REPO, "cosi_sim", "Source_Library", "DC5", "sources", "Galactic")
CASES = [("1RXSJ170849", "1RXSJ170849_magnetar_lightcurve.dat.gz", 11.00502461),
         ("magnetar2", "magnetar2_lightcurve.dat.gz", 11.00502461 / 2)]
NOTE = {}
model = lambda t, P: 1 + 0.5 * np.sin(2 * np.pi * t / P)

for name, f, P in CASES:
    path = os.path.join(G, name, f)
    head, tt, vv = [], [], []
    for line in gzip.open(path, "rt"):
        if line.startswith("DP"):
            p = line.split(); tt.append(p[1]); vv.append(p[2])
        elif not line.startswith("EN"):
            head.append(line)
    t = np.array(tt, float); v = np.array(vv, float)
    if abs((t[-1] - t[0]) / P - round((t[-1] - t[0]) / P)) < 1e-6:
        print(name, "already a whole number of periods"); NOTE[name] = int(round((t[-1] - t[0]) / P)); continue
    resid = np.abs(v - model(t, P)).max()
    assert resid < 1e-6, f"{name}: light curve does not follow the expected profile (max residual {resid})"
    N = int(np.floor((t[-1] - t[0]) / P)); NOTE[name] = N
    t_end = t[0] + N * P
    keep = t < t_end - 1e-6
    with gzip.open(path, "wt") as fo:
        fo.writelines(head)
        for a, b in zip(np.array(tt)[keep], np.array(vv)[keep]):
            fo.write(f"DP {a} {b}\n")
        fo.write(f"DP {float(t_end)!r} {float(model(t_end, P))!r}\n")
        fo.write("EN\n")
    # verification
    t2 = np.r_[t[keep], t_end]; v2 = np.r_[v[keep], model(t_end, P)]
    mean = np.trapezoid(v2, t2) / (t2[-1] - t2[0])
    print(f"{name}: {len(t)} -> {len(t2)} points, span {t[-1]-t[0]:.1f} -> {t_end - t[0]:.4f} s "
          f"= {N} whole periods (was {(t[-1]-t[0])/P:.4f}); end value {v2[-1]:.6f} = start value {v2[0]:.6f}; "
          f"time-averaged light curve {mean:.6f}")

# record the fix in the DC5 build log (used by the README generator)
logf = os.path.join(REPO, "cosi_sim", "Source_Library", "DC5", "DC5_build_log.json")
log = json.load(open(logf))
for name, N in NOTE.items():
    tag = "light curve trimmed to"
    if tag not in log[name]["change"]:
        log[name]["change"] += (f"; {tag} {N} whole pulse periods so that the periodic repeat keeps the pulse "
                                "phase continuous (DC4 period bug fix)")
json.dump(log, open(logf, "w"), indent=1)
