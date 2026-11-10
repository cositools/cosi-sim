"""
Build the DC5 dark-matter annihilation source (chi chi -> e+ e- gamma, FSR, NFW halo).

Usage: python3 build_dc5_dm.py <cosi-sim repo root> <mass MeV> <sigma v cm3/s>

The DC4 map (DC4/sources/DarkMatter/Annihilation_eeg_NFW: m = 30 MeV, <sigma v> = 1e-25 cm3/s) is
separable into J(l, b) x dN/dE. The DC5 map keeps the DC4 spatial template, sky grid and energy nodes and
rescales every energy node k by
    f_k = (sv / 1e-25) * (30 MeV / m)^2 * [dN/dE(E_k; m) / dN/dE(E_k; 30 MeV)]
with dN/dE the Altarelli-Parisi FSR spectrum (matches the DC4 spectral shape to < 1%).
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dm_model import fsr_ap

REPO, M, SV = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
M4, SV4 = 30.0, 1e-25
LIB = os.path.join(REPO, "cosi_sim", "Source_Library")
SRC = os.path.join(LIB, "DC4", "sources", "DarkMatter", "Annihilation_eeg_NFW")
OUT = os.path.join(LIB, "DC5", "sources", "DarkMatter", "Annihilation_eeg_NFW")
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(SRC, "Annihilation_eeg_NFW.dat")) as fi, open(os.path.join(OUT, "Annihilation_eeg_NFW.dat"), "w") as fo:
    f = None
    for line in fi:
        if line.startswith("EA"):
            E = np.array(line.split()[1:], float) / 1000.0
            f = (SV / SV4) * (M4 / M) ** 2 * fsr_ap(E, M) / fsr_ap(E, M4)
            fo.write(line)
        elif line.startswith("AP"):
            p = line.split()
            fo.write(f"AP {p[1]} {p[2]} {p[3]} {float(p[4]) * f[int(p[3])]:.6g}\n")
        else:
            fo.write(line)
print("energy-node scale factors:", np.array2string(f, precision=4))

src = open(os.path.join(SRC, "Annihilation_eeg_NFW.source")).read()
src = src.replace("# Define DC3 sim settings", "# Define DC5 sim settings").replace("# Define DC4 sim settings", "# Define DC5 sim settings")
open(os.path.join(OUT, "Annihilation_eeg_NFW.source"), "w").write(src)
