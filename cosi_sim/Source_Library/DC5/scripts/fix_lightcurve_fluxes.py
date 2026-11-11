"""
Check the Flux keyword of every DC5 source with a light curve, and fix it where it is not the
time average over the light curve.

MEGAlib scales a light curve so that its mean over the light curve's own time range is 1, so the
Flux keyword must be the time-averaged flux over that range. Several DC3/DC4 definitions used the
flux of the source while it is "on" (on/off light curves) or at the light-curve peak (nova). For
those, the DC5 file gets Flux = (on-state or peak flux) x (light-curve mean), which leaves the
intended flux at every time unchanged. Reused sources are copied to DC5 first (DC3/DC4 originals
are not changed).

Usage: python3 fix_lightcurve_fluxes.py <cosi-sim repo root>

Writes the DC5 copies / Flux lines, records the fixes in DC5_build_log.json, and writes
DC5/lc_flux_check.json with the verdict for every light-curve component (read by write_manifest.py,
write_readmes.py and write_dc5_readme.py). Running it again gives the same files.
"""
import json
import os
import re
import shutil
import sys

import numpy as np

REPO = sys.argv[1]
LIB = os.path.join(REPO, "cosi_sim", "Source_Library")
DC5 = os.path.join(LIB, "DC5")
GD = "Gomez-Gomar et al. 1998 (MNRAS 296, 913): CO nova at 1 kpc, peak continuum (170-470 keV) ~0.17, peak 511 keV line ~1e-2, late 478 keV maximum 1.4-2.6e-6 ph/cm2/s"

# key in the build log -> DC5 directory, origin (for reused sources), components to fix, reason
FIX = {
    "3C454p3_low": ("Extragalactic/3C454p3_low", "DC4/sources/Extragalactic/3C454p3_low", ["3C454p3_low"],
                    "on-state", "the spectrum file and README describe the low state (Bonnoli et al. 2011); on/off light curve, on 65.0% of the time"),
    "3C454p3_high": ("Extragalactic/3C454p3_high", "DC4/sources/Extragalactic/3C454p3_high", ["3C454p3_high"],
                     "on-state", "the spectrum file and README describe the flare (03/12 model of Bonnoli et al. 2011); on/off light curve, on 35.0% of the time"),
    "PSRB1259": ("Galactic/PSRB1259", "DC3/sources/Galactic/PSRB1259", ["PSRB1259"],
                 "on-state", "README and DC4 docs: 30-day constant emission at the nominal Abdo et al. (2011) flux of 6.13e-4 ph/cm2/s; on/off light curve, on 32.5% of the time"),
    "MAXIJ1820": ("Galactic/MAXIJ1820", None, ["MAXIJ1820_0p1-0p4", "MAXIJ1820_0p4-10"],
                  "on-state", "hard-state spectra (Cangemi et al. 2023) with the source 'on' for 60 days (README, DC4 docs); on/off light curve, on 65.0% of the time"),
    "nova_co_continuum": ("Galactic/nova_co_continuum", None, ["nova_co_cont"],
                          "peak", "the spectrum-file normalisation equals the flux at the light-curve peak (t = 0); " + GD),
    "nova_co_511keV": ("Galactic/nova_co_511keV", None, ["nova_co_511keV"], "peak", GD),
    "nova_co_478keV": ("Galactic/nova_co_478keV", None, ["nova_co_478keV"], "peak", GD),
}
FIXED_NOTE = "# Flux = time average over the light curve (MEGAlib scales the light curve to mean 1):"

# Light-curve components whose Flux keyword is kept: path -> (components, verdict, short label, note)
KEEP = {
    "DC4/sources/Galactic/Crab": (["Crab_P1", "Crab_Brg", "Crab_P2"], "correct", "phase average",
        "phase-averaged pulsar fluxes of the DC4 Crab model: the three pulsed components add up to 19% of the nebula flux "
        "(0.1-10 MeV), while read as fluxes at the light-curve maximum they would give 2.3%; repeating light curve"),
    "DC3/sources/Galactic/LS5039": (["LS5039"], "correct", "orbit average", "spectrum averaged over the orbital period (README); repeating light curve"),
    "DC5/sources/Galactic/1RXSJ170849": (["1RXSJ170849"], "correct", "phase average", "phase-integrated flux; the light curve 1 + 0.5 sin(2 pi t/P) has mean 1"),
    "DC5/sources/Galactic/magnetar2": (["magnetar2"], "correct", "phase average", "phase-integrated flux; the light curve 1 + 0.5 sin(2 pi t/P) has mean 1"),
    "DC5/sources/Galactic/PSRB1509": (["B1509_band1", "B1509_band2", "B1509_band3"], "correct", "phase average",
        "phase-averaged pulsed spectra (Kuiper & Hermsen 2015); repeating light curve"),
    "DC5/sources/Extragalactic/4C21p35_noflare": (["4C21p35_noflare"], "check", "unclear",
        "Unclear: the light curve varies within the quiescent state (on 77.3% of the time) and the README does not say whether Flux "
        "(the integral of the 4FGL-DR3 extrapolation, 5.5e-4 in DC4) is the 3-month average or the average while quiescent. "
        "If the latter, Flux should be 0.00083025 x 0.7726 = 6.41e-4. Not changed"),
    "DC5/sources/Extragalactic/4C21p35_flare": (["4C21p35_flare"], "check", "unclear",
        "Unclear: the light curve varies within the flare (on 29.2% of the time) and the README does not say whether Flux "
        "(the integral of the flare-state extrapolation, 0.0173 in DC4) is the 3-month average or the average during the flare. "
        "If the latter, Flux should be 0.0259398 x 0.2923 = 7.58e-3. Not changed"),
}
BURSTS = ("correct", "burst average", "average photon flux over the burst: stated in the GRB and magnetar-flare source files; "
           "the short-burst flux is the integral of its burst spectral fit (Li et al. 2021). Each burst is one run over its light curve")


def lc_mean(path):
    x, y, ip = [], [], "LINLIN"
    for line in open(path):
        s = line.split()
        if s[:1] == ["DP"]:
            x.append(float(s[1])); y.append(float(s[2]))
        elif s[:1] == ["IP"]:
            ip = s[1].upper()
    assert ip == "LINLIN", (path, ip)
    x, y = np.array(x), np.array(y)
    return float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2) / (x[-1] - x[0])), float(x[-1] - x[0])


logf = os.path.join(DC5, "DC5_build_log.json")
log = json.load(open(logf))
check = []
for key, (rel, origin, comps, state, reason) in FIX.items():
    d = os.path.join(DC5, "sources", rel)
    if not os.path.isdir(d):
        shutil.copytree(os.path.join(LIB, origin), d)
        print("copied", origin, "->", "DC5/sources/" + rel)
    src = os.path.join(d, os.path.basename(rel) + ".source")
    text = open(src).read()
    rec = log.setdefault(key, {"status": "reused (bug-fixed)", "origin": origin, "change": ""}).setdefault("lc_flux", {})
    for c in comps:
        lc = re.search(r"^\s*%s\.Lightcurve\s+File\s+\S+\s+(\S+)" % re.escape(c), text, re.M).group(1)
        mean, span = lc_mean(os.path.join(d, lc))
        if c in rec:
            state_flux = rec[c]["state_flux"]
        else:
            state_flux = float(re.search(r"^\s*%s\.Flux\s+(\S+)" % re.escape(c), text, re.M).group(1))
        flux = state_flux * mean
        rec[c] = {"state_flux": state_flux, "lc_mean": mean, "flux": flux, "state": state}
        text = re.sub(r"^%s .*\n(?=\s*%s\.Flux)" % (re.escape(FIXED_NOTE), re.escape(c)), "", text, flags=re.M)
        text = re.sub(r"^(\s*)(%s\.Flux)(\s+)\S+" % re.escape(c),
                      lambda m: "%s %s flux %r ph/cm2/s x light-curve mean %.6f\n%s%s%s%.9g" % (
                          FIXED_NOTE, state, state_flux, mean, m.group(1), m.group(2), m.group(3), flux),
                      text, count=1, flags=re.M)
        check.append({"source": "DC5/sources/" + rel, "component": c, "verdict": "fixed", "short": state + " flux x light-curve mean",
                      "flux_old": state_flux, "flux_new": flux, "lc_mean": mean,
                      "note": "Flux was the %s flux; it is now that flux x the light-curve mean (%.4g). Basis: %s" % (state, mean, reason)})
    open(src, "w").write(text)
    if key in ("3C454p3_low", "3C454p3_high", "PSRB1259"):
        log[key]["change"] = ("same model; Flux keyword corrected to the time average over the light curve "
                              "(the DC3/DC4 file gave the on-state flux, which MEGAlib would treat as the time average)")

for path, (comps, verdict, short, note) in KEEP.items():
    for c in comps:
        check.append({"source": path, "component": c, "verdict": verdict, "short": short, "note": note})
for name in sorted(os.listdir(os.path.join(DC5, "sources", "GRBs"))):
    check.append({"source": "DC5/sources/GRBs/" + name, "component": name, "verdict": BURSTS[0], "short": BURSTS[1], "note": BURSTS[2]})

json.dump(log, open(logf, "w"), indent=1)
json.dump(check, open(os.path.join(DC5, "lc_flux_check.json"), "w"), indent=1)
for r in check:
    if r["verdict"] == "fixed":
        print("%-46s %-20s %.6g -> %.6g (x%.6f)" % (r["source"], r["component"], r["flux_old"], r["flux_new"], r["lc_mean"]))
print(len(check), "light-curve components checked:",
      {v: sum(1 for r in check if r["verdict"] == v) for v in ("fixed", "correct", "check")})
