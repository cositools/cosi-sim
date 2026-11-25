"""Apply the cosima Band rule of grb_band.py to an existing GRB draw (DC5_grb_draw.json), as
draw_dc5_grbs.py now does while drawing: Epeak values whose E0 = Epeak/(2+alpha) is not above the
spectrum's Emin are drawn again (generator seeded with the draw's seed + 1, in the draw's GRB order).
The previous value is kept as "epeak_cosima_redraw_from". Safe to rerun.

Usage: python3 apply_grb_band_rule.py <DC5_grb_draw.json>
"""
import json, sys
import numpy as np
from grb_band import epeak_for_cosima

path = sys.argv[1]
draw = json.load(open(path))
rng_e0 = np.random.default_rng(draw["seed"] + 1)
for name, g in draw["grbs"].items():
    sp = g["dc5"]["spectrum"]
    if sp[0] != "Band":
        continue
    ep0 = float(g["dc5"].get("epeak_cosima_redraw_from", sp[5]))
    ep = epeak_for_cosima(float(sp[3]), ep0, float(sp[1]), name == "bn080802386", rng_e0)
    if ep != ep0:
        g["dc5"]["epeak_cosima_redraw_from"] = ep0
        sp[5] = f"{ep:.2f}"
        print(f"{name}: Epeak {ep0:.2f} -> {ep:.2f} keV (E0 {ep0 / (2 + float(sp[3])):.1f} -> {ep / (2 + float(sp[3])):.1f} keV)")
json.dump(draw, open(path, "w"), indent=1)
