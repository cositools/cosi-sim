import sys, os, json, secrets, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dm_significance import *
from dm_model import fsr_ap
# Usage: python3 run_dm_choice.py <cosi-sim repo root> <orientation file> <calibration> [seed]
# calibration = (published / predicted) 3-sigma line sensitivity at 1809 keV, printed by dm_significance.py
REPO, ORI = sys.argv[1], sys.argv[2]
CAL_1809 = float(sys.argv[3])
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else secrets.randbits(32)
DC4_MAP = os.path.join(REPO, 'cosi_sim/Source_Library/DC4/sources/DarkMatter/Annihilation_eeg_NFW/Annihilation_eeg_NFW.dat')
rng = np.random.default_rng(SEED)

S, dOm, psi, L, B = load_dm_template(DC4_MAP)
Wtot = np.sum(S * dOm)
def frac_in_R(R): return np.sum((S * dOm)[psi <= R]) / Wtot
kappa = relative_exposure(ORI, L, B, S * dOm)
# all-sky intensity spectrum: DC4 template normalisation (sv = 1e-25, m = 30 MeV), rescaled
E0 = 100.0
def Phi(E, m, sv):
    return Wtot / fsr_ap(np.array([E0 / 1000]), 30.0)[0] * (sv / 1e-25) * (30.0 / m) ** 2 * fsr_ap(E / 1000, m)
Eb = np.logspace(np.log10(200), np.log10(5000), 41)
Rs = np.arange(2, 41, 1.0)
print(f"kappa (DM-weighted exposure / Crab exposure) = {kappa:.3f}")
print("flux fraction within R:", {R: round(frac_in_R(R), 3) for R in [5, 10, 15, 20, 30]})
z4 = significance(30.0, 1e-25, kappa, frac_in_R, Phi, Rs, Eb)
print(f"DC4 model (30 MeV, 1e-25): raw Z = {z4[0]:.0f}, calibrated Z = {z4[0]*CAL_1809:.0f} (R = {z4[1]} deg)")
# new mass: log-uniform 10-60 MeV, at least 20% away from 30 MeV
while True:
    m = float(np.round(np.exp(rng.uniform(np.log(10), np.log(60))), 1))
    if abs(m / 30 - 1) > 0.2: break
# cross section for calibrated Z = 5 (Z is linear in sv for S << B)
z1 = significance(m, 1e-25, kappa, frac_in_R, Phi, Rs, Eb)
sv5 = 1e-25 * 5 / (z1[0] * CAL_1809)
sv = float(f"{sv5:.2g}")
z = significance(m, sv, kappa, frac_in_R, Phi, Rs, Eb)
flux = lambda m, sv: np.trapezoid(Phi(np.logspace(2, 4, 400), m, sv), np.logspace(2, 4, 400))
out = dict(seed=SEED, mass_MeV=m, sigmav_cm3_s=sv, kappa=kappa, calibration=CAL_1809,
           Z_raw=z[0], Z_calibrated=z[0] * CAL_1809, best_ROI_deg=z[1], S_counts=z[2], B_counts=z[3],
           flux_100keV_10MeV=flux(m, sv), dc4_flux_100keV_10MeV=flux(30.0, 1e-25),
           dc4_Z_raw=z4[0], dc4_Z_calibrated=z4[0] * CAL_1809)
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dm_choice.json'), 'w'), indent=1)
# sensitivity of the choice to the ROI-independent assumptions
for f in [0.5, 1, 2]:
    print(f"if the true sensitivity differs by x{f}: Z = {z[0]*CAL_1809*f:.1f}")
