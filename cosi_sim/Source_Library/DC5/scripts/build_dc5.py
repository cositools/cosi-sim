"""
Build the DC5 source directory for cosi-sim.

Usage: python3 build_dc5.py <cosi-sim repo root> <seed>

The reuse / modify / remove split is drawn by draw_dc5.py (same seed).
This script writes Source_Library/DC5/sources/... for every source that is
bug-fixed, modified, or new. Reused sources are referenced at their existing
library paths in DC5/DC5_mock_dataset_src_list.txt.
"""
import os, sys, shutil, gzip, re, random, json
import numpy as np

REPO = sys.argv[1]
SEED = int(sys.argv[2])
rng = random.Random(SEED + 1)          # sub-choices; offset from the split draw
LIB = os.path.join(REPO, "cosi_sim", "Source_Library")
DC5 = os.path.join(LIB, "DC5", "sources")
EMIN, EMAX = 100.0, 10000.0
log = {}                                # name -> dict(info) for the summary

HEADER = """# Define DC5 sim settings (optimizes sim time):
DefaultRangeCut 0.005
Region Spacecraft
Spacecraft.Volume SCbody
Spacecraft.RangeCut 1.

Region Pipebody
Pipebody.Volume PIPbody
Pipebody.RangeCut 1.

"""

# ---------------------------------------------------------------- helpers
def lib(p): return os.path.join(LIB, p)

def newdir(cat, name):
    d = os.path.join(DC5, cat, name)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d)
    return d

def copy_dir(src, cat, name, skip=()):
    """Copy a library source dir into DC5/<cat>/<name>, renaming the .source file."""
    s = lib(src); d = newdir(cat, name)
    old = os.path.basename(src)
    for f in sorted(os.listdir(s)):
        if f in skip: continue
        out = name + ".source" if f == old + ".source" else f
        shutil.copy2(os.path.join(s, f), os.path.join(d, out))
    return d

def srcfile(cat, name): return os.path.join(DC5, cat, name, name + ".source")

def read(p): return open(p).read()
def write(p, txt): open(p, "w").write(txt)

def set_param(path, key, value, comp=None):
    """Replace '<comp>.<key>   old' with the new value, keeping the spacing."""
    txt = read(path)
    pat = re.compile(r"^(\s*%s\.%s\s+)(.*?)\s*$" % (re.escape(comp) if comp else r"[^.\s]+", key), re.M)
    n = len(pat.findall(txt))
    if n == 0: raise RuntimeError(f"{key} not found in {path}")
    txt = pat.sub(lambda m: m.group(1) + str(value), txt)
    write(path, txt)
    return n

def get_param(path, key, comp=None):
    pat = re.compile(r"^\s*%s\.%s\s+(.*?)\s*$" % (re.escape(comp) if comp else r"[^.\s]+", key), re.M)
    return pat.findall(read(path))

def scale_flux(path, factor, comp=None):
    out = []
    pat = re.compile(r"^(\s*(%s)\.Flux\s+)(\S+)" % (re.escape(comp) if comp else r"[^.\s]+"), re.M)
    def rep(m):
        new = float(m.group(3)) * factor
        out.append((m.group(2), float(m.group(3)), new))
        return m.group(1) + f"{new:.6g}"
    txt = pat.sub(rep, read(path)); write(path, txt)
    if not out: raise RuntimeError("no Flux in " + path)
    return out

def dc2_to_dc5(path):
    """DC2 files use a transmission-probability line; DC3/DC4 use EarthOccultation false + range cuts."""
    lines = [l for l in read(path).splitlines() if "FarFieldTransmissionProbability" not in l]
    body = "\n".join(lines).strip() + "\n"
    comps = re.findall(r"DataChallenge\.Source\s+(\S+)", body)
    for c in comps:  # add EarthOccultation after the Flux line of each component
        body = re.sub(r"(^\s*%s\.Flux[^\n]*\n)" % re.escape(c), lambda m, c=c: m.group(1) + c + ".EarthOccultation false\n", body, flags=re.M)
    write(path, HEADER + body)

def point_source(name, l, b, spectrum, flux, pol=None, beam="FarFieldPointSource 0 0", comment=""):
    s = f"DataChallenge.Source          {name}\n"
    s += f"{name}.ParticleType               1\n"
    s += f"{name}.Beam                       {beam}\n"
    s += f"{name}.Orientation                Galactic Fixed {b:.6f} {l:.6f}\n"
    s += f"{name}.Spectrum                   {spectrum}\n"
    s += f"{name}.Flux                       {flux:.6g}\n"
    if pol: s += f"{name}.Polarization galactic {pol[0]:.2f} {pol[1]:.0f}\n"
    s += f"{name}.EarthOccultation false\n"
    return (comment + "\n" if comment else "") + s

E_GRID = np.logspace(np.log10(EMIN), np.log10(EMAX), 200)
KEV2ERG = 1.602176634e-9

def write_spec(path, func, flux_100_10000=None, norm_band=None, norm_eflux=None):
    """Write a cosima spectrum file. Normalise either to a photon flux in 100 keV-10 MeV,
    or to an energy flux (erg/cm2/s) in norm_band (keV). Returns the 100 keV-10 MeV photon flux."""
    if norm_eflux is not None:
        e = np.logspace(np.log10(norm_band[0]), np.log10(norm_band[1]), 2000)
        k = norm_eflux / (np.trapezoid(e * func(e), e) * KEV2ERG)
    else:
        k = 1.0
    f = k * func(E_GRID)
    pflux = np.trapezoid(f, E_GRID)
    if flux_100_10000 is not None:
        f *= flux_100_10000 / pflux; pflux = flux_100_10000
    with open(path, "w") as h:
        h.write("#Format: <DP> <Energy in keV> <Spectrum in ph cm^-2 s^-1 keV^-1>\n")
        h.write(f"#flux (100.0 - 10000.0 keV): {pflux:.6g} ph/cm^2/s\n\n")
        h.write("IP LOGLOG\n")
        for e, v in zip(E_GRID, f): h.write(f"DP {e:.4f} {v:.6e}\n")
        h.write("EN\n")
    return pflux

def cutoffpl(G, Ec):   return lambda e: e**-G * np.exp(-e / Ec)
def powerlaw(G):       return lambda e: e**-G
def logpar(a, b, piv): return lambda e: (e/piv)**(-a - b*np.log(e/piv))

# ---- cosima 3D map (NormalizedEnergyBeamFluxFunction) tools
def rewrite_map(src, dst, fn, gz=False):
    """Stream a map file, applying fn(k, value) -> value to every AP line (k = energy index)."""
    op_in = gzip.open if src.endswith(".gz") else open
    op_out = gzip.open if gz else open
    with op_in(src, "rt") as fi, op_out(dst, "wt") as fo:
        for line in fi:
            if line.startswith("AP"):
                p = line.split()
                v = fn(int(p[3]), float(p[4]))
                fo.write(f"AP {p[1]} {p[2]} {p[3]} {v:.6g}\n")
            else:
                fo.write(line)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapflux

def map_flux(path):
    pa, ta, ea, c = mapflux.load(path)
    return mapflux.flux(pa, ta, ea, c)[1]

def zero_511_sidebands(src, dst, extra=1.0):
    """Bug fix: equal values at 510/511/512 keV double the line flux.
    Zero the 510 and 512 keV nodes (energy index 0 and 2)."""
    rewrite_map(src, dst, lambda k, v: (v * extra if k == 1 else 0.0))

def rec(name, **kw): log[name] = kw

# =============================================================== BUG-FIXED (Request 3)
# Narrow bulge: reused model, bug fixed only
d = copy_dir("DC3/sources/511/NB_511", "511", "NB_511")
f0 = map_flux(lib("DC3/sources/511/NB_511/NB_511_DC3_1deg.dat"))
zero_511_sidebands(lib("DC3/sources/511/NB_511/NB_511_DC3_1deg.dat"), os.path.join(d, "NB_511_DC3_1deg.dat"))
f1 = map_flux(os.path.join(d, "NB_511_DC3_1deg.dat"))
rec("NB_511", status="reused (bug-fixed)", origin="DC3/sources/511/NB_511",
    change=f"511 keV side nodes (510, 512 keV) set to zero; integrated flux {f0:.3e} -> {f1:.3e} ph/cm2/s")

# Vela SNR 511: reused model, bug fixed only
d = copy_dir("DC3/sources/511/Vela_SNR_511", "511", "Vela_SNR_511")
f0 = map_flux(lib("DC3/sources/511/Vela_SNR_511/Vela_SNR_511.dat"))
zero_511_sidebands(lib("DC3/sources/511/Vela_SNR_511/Vela_SNR_511.dat"), os.path.join(d, "Vela_SNR_511.dat"))
f1 = map_flux(os.path.join(d, "Vela_SNR_511.dat"))
rec("Vela_SNR_511", status="reused (bug-fixed)", origin="DC3/sources/511/Vela_SNR_511",
    change=f"511 keV side nodes set to zero; integrated flux {f0:.3e} -> {f1:.3e} ph/cm2/s (README value 3.5e-4)")

# Broad bulge: bug fix + modification (flux x0.85)
d = copy_dir("DC3/sources/511/BB_511", "511", "BB_511")
f0 = map_flux(lib("DC3/sources/511/BB_511/BB_511_DC3_1deg.dat"))
zero_511_sidebands(lib("DC3/sources/511/BB_511/BB_511_DC3_1deg.dat"), os.path.join(d, "BB_511_DC3_1deg.dat"), extra=0.85)
f1 = map_flux(os.path.join(d, "BB_511_DC3_1deg.dat"))
rec("BB_511", status="modified (+bug-fixed)", origin="DC3/sources/511/BB_511",
    change=f"511 keV side nodes set to zero (bug fix) and broad-bulge intensity scaled x0.85; integrated flux {f0:.3e} -> {f1:.3e} ph/cm2/s")

# In-flight annihilation: position fix + flux x1.2
d = copy_dir("DC4/sources/511/Positrons_In_Flight_Annihilation", "511", "Positrons_In_Flight_Annihilation")
p = srcfile("511", "Positrons_In_Flight_Annihilation")
old_or = get_param(p, "Orientation")[0]
set_param(p, "Orientation", "Galactic Fixed -0.2 -1.4")
fl = scale_flux(p, 1.2)
rec("Positrons_In_Flight_Annihilation", status="modified (+bug-fixed)", origin="DC4/sources/511/Positrons_In_Flight_Annihilation",
    change=f"Orientation '{old_or}' -> 'Galactic Fixed -0.2 -1.4' (bug fix: MEGAlib order is b, l); flux {fl[0][1]:.3g} -> {fl[0][2]:.3g} ph/cm2/s (x1.2)")

# =============================================================== MODIFIED
# 1E 1740.7-2942: alternative DC3 model (two-component Comptonisation)
copy_dir("DC3/sources/Galactic/1E1740_twocompt", "Galactic", "1E1740_twocompt")
rec("1E1740", status="modified", origin="DC3/sources/Galactic/1E1740_compow -> DC3/sources/Galactic/1E1740_twocompt",
    change="swapped compow model for the alternative twocompt model (Bouchet et al. 2009)")

# Cyg X-1: alternative DC3 model (soft state for the full 3 months)
copy_dir("DC3/sources/Galactic/cygX1_soft", "Galactic", "cygX1_soft")
rec("cygX1", status="modified", origin="DC3/sources/Galactic/cygX1_hard -> DC3/sources/Galactic/cygX1_soft",
    change="source in the soft state for the full 3 months (Cangemi et al. 2021 model)")

# Cyg X-3: different spectral state from the DC3 set, nominal flux
state = rng.choice(["quiescent", "FHXR", "FIM", "FSXR", "hypersoft"])
d = newdir("Galactic", "cygX3")
spec = f"cygX3_{state}_spec.dat"
shutil.copy2(lib(f"DC3/sources/Galactic/cygX3/{spec}"), os.path.join(d, spec))
nominal = float(re.search(r"keV\):\s*([0-9.eE+-]+)", read(os.path.join(d, spec))).group(1))
write(srcfile("Galactic", "cygX3"), HEADER + point_source(f"cygX3_{state}", 79.84549, 0.70006, f"File {spec}", nominal))
rec("cygX3", status="modified", origin="DC4/sources/Galactic/cygX3",
    change=f"transition state replaced by the {state} state (DC3 Cangemi et al. 2021 models) for the full 3 months at nominal flux {nominal:.4g} ph/cm2/s")

# GRS 1758-258: flux x0.75
copy_dir("DC3/sources/Galactic/GRS1758", "Galactic", "GRS1758")
fl = scale_flux(srcfile("Galactic", "GRS1758"), 0.75)
rec("GRS1758", status="modified", origin="DC3/sources/Galactic/GRS1758",
    change=f"flux {fl[0][1]:.4g} -> {fl[0][2]:.4g} ph/cm2/s (x0.75, dimmer hard-state epoch)")

# 1RXS J170849: flux x0.75
copy_dir("DC4/sources/Galactic/1RXSJ170849", "Galactic", "1RXSJ170849")
fl = scale_flux(srcfile("Galactic", "1RXSJ170849"), 0.75)
rec("1RXSJ170849", status="modified", origin="DC4/sources/Galactic/1RXSJ170849",
    change=f"flux {fl[0][1]:.3g} -> {fl[0][2]:.3g} ph/cm2/s (x0.75, long-term hard X-ray variability, den Hartog et al. 2008)")

# generic magnetar: flux x1.5
copy_dir("DC4/sources/Galactic/magnetar2", "Galactic", "magnetar2")
fl = scale_flux(srcfile("Galactic", "magnetar2"), 1.5)
rec("magnetar2", status="modified", origin="DC4/sources/Galactic/magnetar2",
    change=f"flux {fl[0][1]:.3g} -> {fl[0][2]:.3g} ph/cm2/s (x1.5)")

# MAXI J1820+070: both components x0.7
copy_dir("DC3/sources/Galactic/MAXIJ1820", "Galactic", "MAXIJ1820")
fl = scale_flux(srcfile("Galactic", "MAXIJ1820"), 0.7)
rec("MAXIJ1820", status="modified", origin="DC3/sources/Galactic/MAXIJ1820",
    change="; ".join(f"{c}: {a:.4g} -> {b:.4g}" for c, a, b in fl) + " ph/cm2/s (x0.7, fainter hard-state outburst)")

# CO nova: all three components x1.5 (distance 1.0 -> 0.82 kpc)
for comp in ["nova_co_continuum", "nova_co_511keV", "nova_co_478keV"]:
    copy_dir(f"DC3/sources/Galactic/{comp}", "Galactic", comp)
    fl = scale_flux(srcfile("Galactic", comp), 1.5)
    rec(comp, status="modified", origin=f"DC3/sources/Galactic/{comp}",
        change=f"flux {fl[0][1]:.4g} -> {fl[0][2]:.4g} ph/cm2/s (x1.5: nova at 0.82 kpc instead of 1 kpc)")

# 4C 21.35: both states x1.5
for comp in ["4C21p35_noflare", "4C21p35_flare"]:
    copy_dir(f"DC3/sources/Extragalactic/{comp}", "Extragalactic", comp)
    fl = scale_flux(srcfile("Extragalactic", comp), 1.5)
    rec(comp, status="modified", origin=f"DC3/sources/Extragalactic/{comp}",
        change=f"flux {fl[0][1]:.4g} -> {fl[0][2]:.4g} ph/cm2/s (x1.5)")

# NGC 4151: thermal (coronal) component x1.5, non-thermal tail unchanged
d = copy_dir("DC4/sources/Extragalactic/NGC_4151", "Extragalactic", "NGC_4151", skip=("NGC4151_ec200_TH_and_NTH_COSI.dat", "image.png"))
f_old = 0.00188
newflux = write_spec(os.path.join(d, "NGC4151_ec200_TH_and_NTH_bright_COSI.dat"),
                     lambda e: 1.5 * 0.149 * e**-1.75 * np.exp(-e / 200.) + 142.8 * e**-3.8)
p = srcfile("Extragalactic", "NGC_4151")
set_param(p, "Spectrum", "File NGC4151_ec200_TH_and_NTH_bright_COSI.dat")
set_param(p, "Flux", f"{newflux:.5g}")
rec("NGC_4151", status="modified", origin="DC4/sources/Extragalactic/NGC_4151",
    change=f"thermal (Gamma=1.75, Ecut=200 keV) normalisation x1.5 (brighter state, Lubinski et al. 2010); non-thermal tail unchanged; flux {f_old} -> {newflux:.4g} ph/cm2/s")

# LMC 511 (DC3 Gaussian definition): flux x2
copy_dir("DC3/sources/511/LMC_Gaussian_511", "511", "LMC_511")
p = srcfile("511", "LMC_511")
write(p, read(p).replace("LMC_Gaussian_511", "LMC_511"))
fl = scale_flux(p, 2.0)
rec("LMC_511", status="modified", origin="DC3/sources/511/LMC_Gaussian_511 (the DC4 LMC_511 definition is not in cosi-sim)",
    change=f"DC4 LMC_511 model replaced by the alternative DC3 LMC_Gaussian_511 definition, with flux x2 relative to DC3 ({fl[0][1]:.3g} -> {fl[0][2]:.3g} ph/cm2/s; still below the SPI 2-sigma limit 3.6e-5, Siegert et al. 2016)")

# M31 511: more compact (sigma 1.0 -> 0.5 deg)
copy_dir("DC3/sources/511/M31_Gaussian_511", "511", "M31_511")
p = srcfile("511", "M31_511")
write(p, read(p).replace("M31_Gaussian_511", "M31_511"))
set_param(p, "Beam", "FarFieldGaussian 0 0 0.5")
rec("M31_511", status="modified", origin="DC3/sources/511/M31_Gaussian_511 (the DC4 M31_511 definition is not in cosi-sim)",
    change="DC4 M31_511 model replaced by the alternative DC3 M31_Gaussian_511 definition, with the Gaussian width reduced 1.0 -> 0.5 deg (emission concentrated in the M31 bulge); DC3 flux 2.13e-7 ph/cm2/s")

# 26Al Cygnus: width 3 -> 4.5 deg
copy_dir("DC3/sources/Al26/26Al_Cyg_Region", "Nucleosynthesis", "26Al_Cyg_Region")
set_param(srcfile("Nucleosynthesis", "26Al_Cyg_Region"), "Beam", "FarFieldGaussian 0 0 4.5")
rec("26Al_Cyg_Region", status="modified", origin="DC3/sources/Al26/26Al_Cyg_Region",
    change="Gaussian width 3.0 -> 4.5 deg (Martin et al. 2009: 3 deg is a lower limit, +-3 deg uncertainty); flux unchanged")

# 60Fe NE2001: x0.65
d = copy_dir("DC3/sources/Fe60/60Fe_NE2001", "Nucleosynthesis", "60Fe_NE2001", skip=("3Dmap_60Fe_ne2001_v2_1.dat",))
src = lib("DC3/sources/Fe60/60Fe_NE2001/3Dmap_60Fe_ne2001_v2_1.dat")
dst = os.path.join(d, "3Dmap_60Fe_ne2001_v2_1.dat")
f0 = map_flux(src)
rewrite_map(src, dst, lambda k, v: v * 0.65)
f1 = map_flux(dst)
rec("60Fe_NE2001", status="modified", origin="DC3/sources/Fe60/60Fe_NE2001",
    change=f"map intensity x0.65 (60Fe mass 3.5 -> 2.3 Msun); total flux (both lines) {f0:.3e} -> {f1:.3e} ph/cm2/s")

# Tycho 44Ti: flux -> 1.0x NuSTAR upper limit
copy_dir("DC4/sources/Nucleosynthesis/Tycho", "Nucleosynthesis", "Tycho")
fl = scale_flux(srcfile("Nucleosynthesis", "Tycho"), 1.0 / 1.6)
rec("Tycho", status="modified", origin="DC4/sources/Nucleosynthesis/Tycho",
    change=f"flux {fl[0][1]:.3g} -> {fl[0][2]:.3g} ph/cm2/s (1.0x instead of 1.6x the Lopez et al. 2015 upper limit)")

# Upper Sco: 60Fe lines x0.5
copy_dir("DC4/sources/Nucleosynthesis/USco", "Nucleosynthesis", "USco")
a = scale_flux(srcfile("Nucleosynthesis", "USco"), 0.5, comp="USco_60Fe_high")
b = scale_flux(srcfile("Nucleosynthesis", "USco"), 0.5, comp="USco_60Fe_low")
rec("USco", status="modified", origin="DC4/sources/Nucleosynthesis/USco",
    change=f"60Fe line fluxes {a[0][1]:.3g} -> {a[0][2]:.3g} ph/cm2/s each (x0.5; 60Fe/26Al per line 0.75 -> 0.375); 26Al unchanged")

# =============================================================== NEW: from other data challenges
# 3C 273 (DC2), converted to DC3+ conventions
d = copy_dir("DC2/sources/Extragalactic/3C273", "Extragalactic", "3C273")
dc2_to_dc5(srcfile("Extragalactic", "3C273"))
sp = os.path.join(d, "3C273_spec.dat")
if not read(sp).rstrip().endswith("EN"): write(sp, read(sp).rstrip() + "\nEN\n")
rec("3C273", status="new (from DC2)", origin="DC2/sources/Extragalactic/3C273",
    change="average state (Madsen et al. 2015), flux 8.6e-4 ph/cm2/s; DC2 transmission-probability line replaced by DC3+ settings")

# 3C 279 high state (DC3 high100 model at x1)
d = newdir("Extragalactic", "3C279_high")
txt = read(lib("DC3/sources/Extragalactic/3C279_high100/3C279_high100_spec.dat")).splitlines()
txt[1] = "#flux (100 keV - 10 MeV): 0.000118672 ph cm^-2 s^-1 (high state, x1; shape identical to DC3 3C279_high100)"
write(os.path.join(d, "3C279_high_spec.dat"), "\n".join(txt) + "\n")
write(srcfile("Extragalactic", "3C279_high"), HEADER + point_source("3C279_high", 305.104299, 57.062412,
      "File 3C279_high_spec.dat", 0.0118672 / 100, pol=(0.1962, 45)))
rec("3C279_high", status="new (from DC3)", origin="DC3/sources/Extragalactic/3C279_high100",
    change="high-state spectrum at its physical flux (x1 instead of x100): 1.19e-4 ph/cm2/s, 19.6% polarisation at 45 deg")

# PSR B1509-58 (DC2), phase-resolved pulsar
d = copy_dir("DC2/sources/Galactic/PSRB1509", "Galactic", "PSRB1509")
dc2_to_dc5(srcfile("Galactic", "PSRB1509"))
rec("PSRB1509", status="new (from DC2)", origin="DC2/sources/Galactic/PSRB1509",
    change="3 energy bands with periodic pulse profiles (Kuiper et al. 2015); DC2 transmission-probability lines replaced by DC3+ settings")

# =============================================================== NEW: real sources from the literature
KEV = lambda e: e
# NGC 4945 (Seyfert 2): Gamma=1.9, Ecut=300 keV, 20-100 keV energy flux 2.0e-10
d = newdir("Extragalactic", "NGC_4945")
fx = write_spec(os.path.join(d, "NGC_4945_spec.dat"), cutoffpl(1.9, 300.), norm_band=(20, 100), norm_eflux=2.0e-10)
write(srcfile("Extragalactic", "NGC_4945"), HEADER + point_source("NGC_4945", 305.2721, 13.3397, "File NGC_4945_spec.dat", fx))
rec("NGC_4945", status="new (literature)", l=305.2721, b=13.3397, flux=fx,
    change="cutoff power law Gamma=1.9, Ecut=300 keV (NuSTAR: Ecut > 200-300 keV, Puccetti et al. 2014); F(20-100 keV)=2.0e-10 erg/cm2/s")

# IC 4329A (Seyfert 1): Gamma=1.70, Ecut=178 keV, F(5-79 keV)=3.04e-10
d = newdir("Extragalactic", "IC_4329A")
fx = write_spec(os.path.join(d, "IC_4329A_spec.dat"), cutoffpl(1.70, 178.), norm_band=(5, 79), norm_eflux=3.04e-10)
write(srcfile("Extragalactic", "IC_4329A"), HEADER + point_source("IC_4329A", 317.4963, 30.9200, "File IC_4329A_spec.dat", fx))
rec("IC_4329A", status="new (literature)", l=317.4963, b=30.92, flux=fx,
    change="cutoff power law Gamma=1.70, Ecut=178 keV, F(5-79 keV)=3.04e-10 erg/cm2/s (Brenneman et al. 2014)")

# GX 339-4 hard state: Gamma=1.6, Ecut=200 keV, F(20-200 keV)=1.5e-9 (~0.15 Crab)
d = newdir("Galactic", "GX339m4_hard")
fx = write_spec(os.path.join(d, "GX339m4_hard_spec.dat"), cutoffpl(1.6, 200.), norm_band=(20, 200), norm_eflux=1.5e-9)
write(srcfile("Galactic", "GX339m4_hard"), HEADER + point_source("GX339m4_hard", 338.9391, -4.3265, "File GX339m4_hard_spec.dat", fx, pol=(0.05, 20)))
rec("GX339m4_hard", status="new (literature)", l=338.9391, b=-4.3265, flux=fx,
    change="black-hole LMXB in a moderately bright hard state for the full 3 months: Gamma=1.6, Ecut=200 keV, F(20-200 keV)=1.5e-9 erg/cm2/s; 5% polarisation")

# 4U 0142+61 magnetar hard tail: Gamma=0.93 below a ~228 keV break (den Hartog et al. 2008)
d = newdir("Galactic", "4U0142p61")
beta = (2.0 - 0.93) / (2 * np.log(228. / 50.))
fx = write_spec(os.path.join(d, "4U0142p61_spec.dat"), logpar(0.93, beta, 50.), norm_band=(20, 229), norm_eflux=1.5e-10)
write(srcfile("Galactic", "4U0142p61"), HEADER + point_source("4U0142p61", 129.3840, -0.4307, "File 4U0142p61_spec.dat", fx))
rec("4U0142p61", status="new (literature)", l=129.384, b=-0.4307, flux=fx,
    change=f"log-parabola, local index 0.93 at 50 keV with the nuFnu peak at 228 keV (beta={beta:.3f}); F(20-229 keV)=1.5e-10 erg/cm2/s (den Hartog et al. 2008); steady (no pulsation light curve)")

# Carina region 26Al: 1.5e-5 at Trumpler 16 (Voss et al. 2012)
d = newdir("Nucleosynthesis", "26Al_Carina_Region")
write(srcfile("Nucleosynthesis", "26Al_Carina_Region"), HEADER + point_source("26Al_Carina_Region", 287.6, -0.6,
      "Gaussian 1808.8 0.68 3", 1.5e-5, beam="FarFieldGaussian 0 0 2.0"))
rec("26Al_Carina_Region", status="new (literature)", l=287.6, b=-0.6, flux=1.5e-5,
    change="1809 keV line, 2 deg Gaussian at Trumpler 16, flux 1.5e-5 ph/cm2/s (Voss et al. 2012), width as DC3 Cygnus model")

# =============================================================== NEW: arbitrary (fictitious) sources
def rand_disk(lmax, bsig):
    l = rng.uniform(-lmax, lmax) % 360; b = rng.gauss(0, bsig); return round(l, 3), round(b, 3)
def rand_highlat(bmin):
    l = rng.uniform(0, 360); b = rng.choice([-1, 1]) * np.degrees(np.arcsin(rng.uniform(np.sin(np.radians(bmin)), 1)))
    return round(l, 3), round(b, 3)

l, b = rand_disk(60, 1.0)
d = newdir("Nucleosynthesis", "Ti44_hidden_SNR")
write(srcfile("Nucleosynthesis", "Ti44_hidden_SNR"), HEADER + point_source("Ti44_hidden_SNR", l, b, "Gaussian 1157.02 15.4 3", 1.2e-5))
rec("Ti44_hidden_SNR", status="new (arbitrary)", l=l, b=b, flux=1.2e-5,
    change="unknown young, dust-obscured SNR: point-like 44Ti line, 4000 km/s broadening, 1.2e-5 ph/cm2/s (comparable to Tycho/Kepler models)")

l, b = rand_disk(90, 5.0)
d = newdir("Nucleosynthesis", "nova_one_22Na")
write(srcfile("Nucleosynthesis", "nova_one_22Na"), HEADER + point_source("nova_one_22Na", l, b, "Gaussian 1274.5 8.5 3", 4.4e-6))
rec("nova_one_22Na", status="new (arbitrary)", l=l, b=b, flux=4.4e-6,
    change="ONe nova at 1.5 kpc: 22Na 1275 keV line (~20 keV FWHM), ~1e-5 ph/cm2/s at 1 kpc (Hernanz 2014) scaled to 1.5 kpc; constant (22Na lifetime 3.75 yr)")

l, b = rand_disk(120, 2.0)
d = newdir("511", "Positrons_Point_Source")
write(srcfile("511", "Positrons_Point_Source"), HEADER + point_source("Positrons_Point_Source", l, b, "Gaussian 511 1.5 3", 2.5e-5))
rec("Positrons_Point_Source", status="new (arbitrary)", l=l, b=b, flux=2.5e-5,
    change="steady point-like 511 keV line (e.g. a microquasar or pulsar positron source), 2.5e-5 ph/cm2/s, same line width as the DC4 central source")

l, b = rand_disk(80, 3.0)
d = newdir("Galactic", "BHXB_hard_transient")
fx = write_spec(os.path.join(d, "BHXB_hard_transient_spec.dat"), cutoffpl(1.6, 150.), flux_100_10000=1.5e-3)
write(srcfile("Galactic", "BHXB_hard_transient"), HEADER + point_source("BHXB_hard_transient", l, b, "File BHXB_hard_transient_spec.dat", fx))
rec("BHXB_hard_transient", status="new (arbitrary)", l=l, b=b, flux=fx,
    change="new black-hole X-ray binary in a long hard-state outburst: Gamma=1.6, Ecut=150 keV, 1.5e-3 ph/cm2/s (about 1/20 of the Crab in 100 keV-10 MeV)")

l, b = rand_disk(150, 1.0)
d = newdir("Galactic", "PWN_hard_source")
fx = write_spec(os.path.join(d, "PWN_hard_source_spec.dat"), powerlaw(2.1), flux_100_10000=4.0e-4)
write(srcfile("Galactic", "PWN_hard_source"), HEADER + point_source("PWN_hard_source", l, b, "File PWN_hard_source_spec.dat", fx, pol=(0.3, 100)))
rec("PWN_hard_source", status="new (arbitrary)", l=l, b=b, flux=fx,
    change="Crab-like pulsar wind nebula ~80x fainter than the Crab nebula: power law Gamma=2.1, 4e-4 ph/cm2/s, 30% polarisation")

l, b = rand_disk(170, 0.5)
d = newdir("Galactic", "magnetar3")
fx = write_spec(os.path.join(d, "magnetar3_spec.dat"), logpar(1.2, 0.30, 143.276), flux_100_10000=2.5e-4)
write(srcfile("Galactic", "magnetar3"), HEADER + point_source("magnetar3", l, b, "File magnetar3_spec.dat", fx, pol=(0.5, 40)))
rec("magnetar3", status="new (arbitrary)", l=l, b=b, flux=fx,
    change="steady hard-tail magnetar (no pulsation light curve): log-parabola alpha=1.2, beta=0.30, pivot 143 keV, 2.5e-4 ph/cm2/s, 50% polarisation")

l, b = rand_highlat(30)
d = newdir("Extragalactic", "MeV_blazar")
fx = write_spec(os.path.join(d, "MeV_blazar_spec.dat"), logpar(2.0, 0.2, 1000.), flux_100_10000=3.0e-4)
write(srcfile("Extragalactic", "MeV_blazar"), HEADER + point_source("MeV_blazar", l, b, "File MeV_blazar_spec.dat", fx, pol=(0.15, 120)))
rec("MeV_blazar", status="new (arbitrary)", l=l, b=b, flux=fx,
    change="high-redshift FSRQ with nuFnu peak at 1 MeV: log-parabola alpha=2.0, beta=0.2 at 1 MeV, 3e-4 ph/cm2/s (between 4C 71.07 and 3C 279), 15% polarisation")

l, b = rand_highlat(20)
d = newdir("Extragalactic", "Seyfert_new")
fx = write_spec(os.path.join(d, "Seyfert_new_spec.dat"), cutoffpl(1.8, 300.), flux_100_10000=3.0e-4)
write(srcfile("Extragalactic", "Seyfert_new"), HEADER + point_source("Seyfert_new", l, b, "File Seyfert_new_spec.dat", fx))
rec("Seyfert_new", status="new (arbitrary)", l=l, b=b, flux=fx,
    change="Seyfert galaxy with Gamma=1.8, Ecut=300 keV, 3e-4 ph/cm2/s (a few times fainter than NGC 4151)")

l, b = rand_disk(100, 1.0)
d = newdir("Nucleosynthesis", "26Al_new_region")
write(srcfile("Nucleosynthesis", "26Al_new_region"), HEADER + point_source("26Al_new_region", l, b,
      "Gaussian 1808.8 0.68 3", 1.5e-5, beam="FarFieldGaussian 0 0 4.0"))
rec("26Al_new_region", status="new (arbitrary)", l=l, b=b, flux=1.5e-5,
    change="additional massive-star region: 4 deg Gaussian 1809 keV source, 1.5e-5 ph/cm2/s (similar to Carina / ~40% of Cygnus)")

json.dump(log, open(os.path.join(os.path.dirname(DC5), "DC5_build_log.json"), "w"), indent=1, default=float)
print(json.dumps(log, indent=1, default=float))
