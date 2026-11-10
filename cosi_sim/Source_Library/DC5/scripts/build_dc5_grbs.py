"""
Write the DC5 GRB source directories from the draw made by draw_dc5_grbs.py.

Usage: python3 build_dc5_grbs.py <cosi-sim repo root> <DC5_grb_draw.json>

For each DC4 GRB_bn burst, DC5/sources/GRBs/<name>/ gets
  <name>.source           same structure as the DC3 file; new Spectrum and Polarization lines
  <name>_lightcurve.dat   DC3 light curve with all times shifted to the DC5 trigger time
  README_DC5.md           model, DC4 -> DC5 changes, geometry, references

Run scripts/make_sim_time_inputs.py afterwards: it adds the time-shifted MEGAlib inputs and points the
source files to the shifted light curves (rerunning this script resets them to absolute times).
"""
import os, sys, re, json

REPO, DRAW = sys.argv[1], sys.argv[2]
LIB = os.path.join(REPO, "cosi_sim", "Source_Library")
SRC = os.path.join(LIB, "DC3", "sources", "GRBs")
OUT = os.path.join(LIB, "DC5", "sources", "GRBs")
draw = json.load(open(DRAW))

REFS = """- [Poolakkil et al. 2021, ApJ 913, 60 — Fermi GBM GRB spectral catalog, 10 years](https://arxiv.org/abs/2103.13528) (Band and power-law parameter distributions)
- [Gruber et al. 2014, ApJS 211, 12 — Fermi GBM GRB spectral catalog, 4 years](https://arxiv.org/abs/1401.5069)
- [Kole et al. 2020, A&A 644, A124 — POLAR GRB polarization catalog](https://arxiv.org/abs/2009.04871) (time-integrated polarization is low to moderate)
- [Fermi GBM burst catalog (HEASARC FERMIGBRST)](https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html) (original burst `{name}`)
"""

os.makedirs(OUT, exist_ok=True)
for name, g in draw["grbs"].items():
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    src = open(os.path.join(SRC, name, name + ".source")).read()
    d5, d4 = g["dc5"], g["dc4"]

    s = src.replace("# Define DC3 sim settings", "# Define DC5 sim settings")
    s = re.sub(r"^(\s*%s\.Orientation\s+).*$" % name,
               lambda m: m.group(1) + f"Galactic Fixed {d5['b']:.4f} {d5['l']:.4f}", s, flags=re.M)
    s = re.sub(r"^(\s*%s\.Flux\s+).*$" % name, lambda m: m.group(1) + f"{d5['flux']:.6g}", s, flags=re.M)
    s = re.sub(r"^(\s*%s\.Spectrum\s+).*$" % name, lambda m: m.group(1) + " ".join(d5["spectrum"]), s, flags=re.M)
    s = re.sub(r"^(\s*%s\.Polarization\s+).*$" % name,
               lambda m: m.group(1) + f"galactic {d5['pol'][0]:.2f} {d5['pol'][1]:.1f}", s, flags=re.M)
    # DC3 bn180703876 file declared EarthOccultation for the wrong component name (bn090424592)
    s = re.sub(r"^\s*\S+\.EarthOccultation\s+false\s*$", f"{name}.EarthOccultation false", s, flags=re.M)
    assert s.count(f"{name}.EarthOccultation false") == 1, name
    open(os.path.join(d, name + ".source"), "w").write(s.rstrip() + "\n")

    # Light curve: shift every time stamp by the same offset; keep all other lines unchanged
    shift = d5["t0"] - d4["t0"]
    with open(os.path.join(SRC, name, g["lc_file"])) as fi, open(os.path.join(d, g["lc_file"]), "w") as fo:
        for line in fi:
            if line.startswith("DP"):
                p = line.split()
                fo.write(f"DP {float(p[1]) + shift:.4f} {p[2]}\n")
            else:
                fo.write(line)

    sp4, sp5 = d4["spectrum"], d5["spectrum"]
    if sp5[0] == "Band":
        spec_tab = ("| Band alpha | {} | {} |\n| Band beta | {} | {} |\n| Epeak (keV) | {:.1f} | {:.1f} |\n"
                    .format(f"{float(sp4[3]):.3f}", sp5[3], f"{float(sp4[4]):.3f}", sp5[4], float(sp4[5]), float(sp5[5])))
    else:
        spec_tab = "| Power-law index | {:.3f} | {} |\n".format(float(sp4[3]), sp5[3])
    txt = f"""# {name} — DC5

**DC5 status:** modified (time, position, flux, spectral and polarization parameters)
**Based on:** `DC3/sources/GRBs/{name}` (included in the DC4 mock dataset)
**Duration (light-curve span):** {g['duration_s']:.2f} s

## Changes relative to the DC4 mock dataset

| Parameter | DC4 | DC5 |
|---|---|---|
| Trigger time (unix s) | {d4['t0']:.3f} | {d5['t0']:.3f} |
| End of burst (unix s) | {d4['t0'] + g['duration_s']:.3f} | {d5['t_end']:.3f} (limit 1836092100.0) |
| Day of the observation | {d4['day']:.2f} | {d5['day']:.2f} |
| Position l, b (deg) | {d4['l']:.4f}, {d4['b']:.4f} | {d5['l']:.4f}, {d5['b']:.4f} |
| Off-axis angle at trigger (deg) | {d4['offaxis']:.1f} | {d5['offaxis']:.1f} (end of burst: {d5['offaxis_end']:.1f}) |
| Zenith angle at trigger (deg) | {d4['zenith']:.1f} | {d5['zenith']:.1f} |
| Spectral model | {sp4[0]} | {sp5[0]} (unchanged) |
{spec_tab}| Photon flux 100 keV-10 MeV (ph/cm2/s) | {d4['flux']:.6g} | {d5['flux']:.6g} (x{d5['flux']/d4['flux']:.2f}) |
| Polarization fraction | {d4['pol'][0]:.2f} | {d5['pol'][0]:.2f} |
| Polarization angle (deg, galactic) | {d4['pol'][1]:.1f} | {d5['pol'][1]:.1f} |

The light curve is the DC3 light curve, unchanged in shape, with every time stamp shifted by {d5['shift_s']:+.3f} s.

## How the DC5 values were chosen

- **Time:** all DC5 GRBs fall in days 4-7 of the observation (3-7 days after the start of the DC4 orientation file), so they overlap the week of background simulations with ACS data and come after the activation build-up. The whole burst plus a 5 min margin ends before 1836092100.0 (7 days after the start of the orientation file). The time is random within the window, with >= 1 h separation from any other DC5 GRB.
- **Position:** placed at a target off-axis angle (angle between the COSI z-axis and the source) of {d5['target_offaxis']:.1f} deg, at a random azimuth around the z-axis at the trigger time. The targets are the DC4 GRB off-axis values jittered by up to +-3 deg and randomly reassigned, so the DC5 set reproduces the DC4 distribution. Required: off-axis angle <= 60 deg during the whole burst, zenith angle <= 100 deg (well above the ~113 deg Earth-occultation limit), livetime > 0 (no SAA) from 5 min before to 5 min after the burst, and an off-axis change < 3 deg during the burst (no slew).
- **Flux:** DC4 photon flux (100 keV-10 MeV, time-averaged over the light curve) times a log-uniform factor in [0.5, 2]. For the two DC4 bursts above 100 ph/cm2/s, which are already artificially bright, the factor is in [0.5, 1].
- **Spectrum:** same spectral model as DC4; parameters drawn from the Fermi GBM 10-year catalog fluence-spectrum distributions ({'short' if name == 'bn080802386' else 'long'} GRBs): alpha and log10(Epeak) Gaussian around the catalog medians (long: alpha = -0.84, Epeak = 144 keV; short: alpha = -0.46, Epeak = 413 keV), beta Gaussian around -2.3 (sigma 0.3), with cuts to keep alpha > beta and Epeak in a range COSI can constrain. For power-law bursts the index follows the high-energy (beta) distribution, since COSI only sees the spectrum above 100 keV.
- **Polarization:** the DC4 GRB polarization fractions are spread uniformly between 0 and 0.9; DC5 fractions are drawn from the same distribution (stratified uniform on [0, 0.9]). The angle is uniform in [0, 180) deg.

## References

{REFS.format(name=name)}
_Select it in inputs.yaml as `DC5/sources/GRBs/{name}`._
"""
    open(os.path.join(d, "README_DC5.md"), "w").write(txt)
    print("wrote", name)
