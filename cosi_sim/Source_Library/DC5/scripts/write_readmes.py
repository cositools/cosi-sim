"""Write README_DC5.md into every non-GRB DC5 source directory, using DC5_build_log.json.

Usage: python3 write_readmes.py <Source_Library/DC5 dir>
Entries flagged "skip_readme" in the build log (dark matter) keep their hand-written README_DC5.md;
GRB READMEs are written by build_dc5_grbs.py. Sources with a light curve get a "Light-curve flux"
section from lc_flux_check.json (written by fix_lightcurve_fluxes.py).
"""
import json, os, sys
ROOT = sys.argv[1]                      # .../Source_Library/DC5
log = json.load(open(os.path.join(ROOT, "DC5_build_log.json")))
lcflux = {}
for r in json.load(open(os.path.join(ROOT, "lc_flux_check.json"))):
    lcflux.setdefault(r["source"], []).append(r)

ADS = lambda b: f"https://ui.adsabs.harvard.edu/abs/{b}/abstract"
R = {
 "siegert16": ("Siegert et al. 2016, A&A 586, A84 (SPI 511 keV all-sky)", ADS("2016A%26A...586A..84S")),
 "siegert16sat": ("Siegert et al. 2016, A&A 595, A25 (511 keV from Milky Way satellites, LMC limit)", "https://arxiv.org/abs/1608.00393"),
 "knod25": ("Knödlseder et al. 2025, A&A 700, A257 (positron in-flight annihilation, COMPTEL)", "https://arxiv.org/abs/2506.17427"),
 "leising": ("DC3 Vela SNR 511 keV model (M. Leising), DC3/sources/511/Vela_SNR_511/Readme.txt", None),
 "bouchet09": ("Bouchet et al. 2009, ApJ 693, 1871 (1E 1740.7-2942 INTEGRAL spectra)", "https://iopscience.iop.org/article/10.1088/0004-637X/693/2/1871"),
 "cangemi21": ("Cangemi et al. 2021, A&A 650, A93 (Cyg X-1 hard/soft states)", ADS("2021A%26A...650A..93C")),
 "cangemi21x3": ("Cangemi et al. 2021, A&A 645, A60 (Cyg X-3 spectral states)", "https://www.aanda.org/articles/aa/pdf/2021/01/aa37951-20.pdf"),
 "pottschmidt06": ("Pottschmidt et al. 2006, A&A 452, 285 (GRS 1758-258)", "https://arxiv.org/abs/astro-ph/0509006"),
 "denhartog08b": ("den Hartog, Kuiper & Hermsen 2008, A&A 489, 263 (1RXS J1708-40)", "https://www.arxiv.org/abs/0804.1641"),
 "rea08": ("Götz et al. 2007, A&A 475, 317 (long-term hard X-ray variability of 1RXS J1708-40)", "https://arxiv.org/abs/0709.3712"),
 "cangemi23": ("Cangemi et al. 2023, A&A 669, A65 (MAXI J1820+070, MAXI J1348-630)", ADS("2023A%26A...669A..65C")),
 "hernanz14": ("Hernanz 2014, ASPC 490, 319 (gamma-rays from classical novae)", "https://arxiv.org/abs/1305.0769"),
 "4c21": ("DC3 4C 21.35 model, DC3/sources/Extragalactic/4C21p35_flare/README.txt (Fermi-LAT log-parabola extrapolation)", None),
 "lubinski10": ("Lubiński et al. 2010, MNRAS 408, 1851 (NGC 4151 spectral states)", ADS("2010MNRAS.408.1851L")),
 "inoue08": ("Inoue, Totani & Ueda 2008, ApJL 672, L5 (non-thermal AGN tail)", ADS("2008ApJ...672L...5I")),
 "martin09": ("Martin et al. 2009, A&A 506, 703 (26Al in Cygnus)", "https://arxiv.org/abs/1001.1521"),
 "wang20": ("Wang et al. 2020, ApJ 889, 169 (Galactic 60Fe)", ADS("2020ApJ...889..169W")),
 "martin10": ("Martin et al. 2010, A&A 511, A86 (60Fe/26Al)", ADS("2010A%26A...511A..86M")),
 "lopez15": ("Lopez et al. 2015, ApJ 814, 132 (NuSTAR 44Ti limits, Tycho)", ADS("2015ApJ...814..132L")),
 "diehl10": ("Diehl et al. 2010, A&A 522, A51 (26Al in Sco-Cen)", ADS("2010A%26A...522A..51D")),
 "madsen15": ("Madsen et al. 2015, ApJ 812, 14 (3C 273 broadband)", ADS("2015ApJ...812...14M")),
 "3c279": ("DC2/DC3 3C 279 models, DC3/sources/Extragalactic/3C279_high100/ReadMe.txt", None),
 "kuiper15": ("Kuiper & Hermsen 2015, MNRAS 449, 3827 (PSR B1509-58)", "https://doi.org/10.1093/mnras/stv426"),
 "puccetti14": ("Puccetti et al. 2014, ApJ 793, 26 (NuSTAR NGC 4945)", "https://www.arxiv.org/abs/1407.3974"),
 "brenneman14": ("Brenneman et al. 2014, ApJ 788, 61 (NuSTAR IC 4329A)", "https://arxiv.org/abs/1312.3563"),
 "gx339": ("Droulans et al. 2010, ApJ 717, 1022 (GX 339-4 hard-state INTEGRAL spectra)", ADS("2010ApJ...717.1022D")),
 "denhartog08a": ("den Hartog et al. 2008, A&A 489, 245 (4U 0142+61 hard X-ray spectrum and break)", "https://www.arxiv.org/abs/0804.1640"),
 "voss12": ("Voss et al. 2012, A&A 539, A66 (26Al in the Carina region)", "https://www.aanda.org/10.1051/0004-6361/201118209"),
 "grefenstette": ("Weinberger et al. 2020, A&A 638, A83 (44Ti in young SNRs, SPI)", ADS("2020A%26A...638A..83W")),
 "kuiper06": ("Kuiper et al. 2006, ApJ 645, 556 (hard X-ray tails of AXPs)", "https://arxiv.org/abs/astro-ph/0603467"),
 "guessoum05": ("Guessoum et al. 2005, A&A 436, 171 (positron annihilation spectra)", ADS("2005A%26A...436..171G")),
 "bonnoli11": ("Bonnoli et al. 2011, MNRAS 410, 368 (MeV blazar SED shapes)", ADS("2011MNRAS.410..368B")),
 "abdo11": ("Abdo et al. 2011, ApJL 736, L11 (Fermi-LAT PSR B1259-63 periastron flare)", "https://doi.org/10.1088/2041-8205/736/1/L11"),
 "gomezgomar98": ("Gómez-Gomar et al. 1998, MNRAS 296, 913 (gamma-ray emission of individual classical novae)", "https://arxiv.org/abs/astro-ph/9711322"),
}

CAT = {  # key in log -> (DC5 relative dir(s), title, refs, model text)
 "3C454p3_low": (["Extragalactic/3C454p3_low"], "Blazar 3C 454.3, low state", ["bonnoli11"],
   "DC4 model: low-state spectrum of Bonnoli et al. (2011), unpolarised, on whenever the source is not flaring (65% of the 3 months; on/off light curve)."),
 "3C454p3_high": (["Extragalactic/3C454p3_high"], "Blazar 3C 454.3, flare", ["bonnoli11"],
   "DC4 model: flare spectrum (03/12 model of Bonnoli et al. 2011), 50% polarisation at 45 deg, on during the flare (35% of the 3 months; on/off light curve)."),
 "PSRB1259": (["Galactic/PSRB1259"], "Gamma-ray binary PSR B1259-63, periastron flare", ["abdo11"],
   "DC3/DC4 model: 30 days of constant emission (T > 1839487305.0) at the nominal Fermi-LAT flux of Abdo et al. (2011), 6.13e-4 ph/cm2/s in 0.1-10 MeV."),
 "NB_511": (["511/NB_511"], "Narrow Galactic bulge, 511 keV line", ["siegert16"],
   "DC3 narrow-bulge 511 keV intensity map (1 deg grid). Same model as DC3/DC4."),
 "BB_511": (["511/BB_511"], "Broad Galactic bulge, 511 keV line", ["siegert16"],
   "DC3 broad-bulge 511 keV intensity map (1 deg grid), intensity scaled by 0.85 in DC5. The resulting bulge total "
   "(narrow + broad + central source) is 9.9e-4 ph/cm2/s, within 1 sigma of the SPI bulge flux of Siegert et al. (2016)."),
 "Vela_SNR_511": (["511/Vela_SNR_511"], "Vela SNR, 511 keV line", ["leising"],
   "DC3 model: positrons from 1e-4 Msun of 44Ti trapped in the remnant, spatial template from the ROSAT all-sky X-ray emission (~8 deg). Same model as DC3/DC4."),
 "Positrons_In_Flight_Annihilation": (["511/Positrons_In_Flight_Annihilation"], "Positron in-flight annihilation (Galactic bulge, MeV continuum)", ["knod25"],
   "2D Gaussian (sigma = 3.3 deg, i.e. FWHM 7.8 deg) at (l, b) = (-1.4, -0.2) deg with the DC4 best-fit spectrum. "
   "DC5 flux is 1.2x the DC4 value (3.72e-4 vs 3.1e-4 ph/cm2/s in 0.1-10 MeV), within the ~17% (1 sigma) flux uncertainty of Knödlseder et al. (2025)."),
 "LMC_511": (["511/LMC_511"], "Large Magellanic Cloud, 511 keV line", ["siegert16sat"],
   "The DC4 LMC_511 simulation used a definition that is not in cosi-sim. DC5 replaces it with the alternative DC3 LMC_Gaussian_511 definition (Gaussian, sigma = 3.3 deg, line at 511.5 keV) with the flux doubled to 8.54e-6 ph/cm2/s, still well below the SPI 2-sigma upper limit of 3.6e-5."),
 "M31_511": (["511/M31_511"], "M31, 511 keV line", ["siegert16sat"],
   "The DC4 M31_511 simulation used a definition that is not in cosi-sim. DC5 replaces it with the alternative DC3 M31_Gaussian_511 definition, with a more compact emission region (sigma 0.5 deg instead of 1.0 deg), i.e. annihilation concentrated toward the bulge; DC3 flux 2.13e-7 ph/cm2/s."),
 "1E1740": (["Galactic/1E1740_twocompt"], "1E 1740.7-2942", ["bouchet09"],
   "Alternative DC3 spectral model: two thermal-Comptonisation components (twocompt). DC4 used the compow (Comptonisation + power law) model; both fit INTEGRAL data but differ strongly at the highest energies."),
 "cygX1": (["Galactic/cygX1_soft"], "Cyg X-1", ["cangemi21"],
   "Alternative DC3 spectral model: soft state (eqpair fit to INTEGRAL data) with 20% energy-independent polarisation, for the full 3 months. DC4 used the hard state."),
 "cygX3": (["Galactic/cygX3"], "Cyg X-3", ["cangemi21x3"],
   "One of the DC3 eqpair spectral-state models (state drawn at random among those not used in DC4) for the full 3 months, at nominal flux (no x7.9 boost)."),
 "GRS1758": (["Galactic/GRS1758"], "GRS 1758-258", ["pottschmidt06"],
   "DC3 Comptonisation model (epoch 2 of Pottschmidt et al. 2006) with the flux scaled by 0.75, representing a dimmer hard-state epoch (the source shows tens-of-percent flux changes between epochs)."),
 "1RXSJ170849": (["Galactic/1RXSJ170849"], "Magnetar 1RXS J170849.0-400910", ["denhartog08b", "rea08"],
   "DC4 log-parabola spectrum, 80% polarisation and 11 s pulsation light curve. DC5 flux scaled by 0.75 (2.48e-4 ph/cm2/s), motivated by the reported long-term hard X-ray variability."),
 "magnetar2": (["Galactic/magnetar2"], "Generic magnetar (fictitious, DC4)", ["denhartog08b"],
   "DC4 generic magnetar (log-parabola, 40% polarisation, 5.5 s pulsation light curve). DC5 flux scaled by 1.5 (4.95e-4 ph/cm2/s)."),
 "MAXIJ1820": (["Galactic/MAXIJ1820"], "MAXI J1820+070 (hard-state outburst)", ["cangemi23"],
   "DC3 two-component spectral/polarisation model with the 60-day ON light curve. Both components scaled by 0.7 (a fainter hard-state outburst than the exceptional 2018 one)."),
 "nova_co": (["Galactic/nova_co_continuum", "Galactic/nova_co_511keV", "Galactic/nova_co_478keV"], "Classical CO nova", ["hernanz14", "gomezgomar98"],
   "DC3 CO-nova model (continuum, 511 keV line, 478 keV 7Be line with their light curves) at the position of V1369 Cen, at 1 kpc. "
   "DC5 keeps this model, with the Flux keywords set to the time averages of the Hernanz (2014) model, which should be the correct model."),
 "4C21p35": (["Extragalactic/4C21p35_noflare", "Extragalactic/4C21p35_flare"], "FSRQ 4C +21.35", ["4c21"],
   "DC3 two-state model (quiescent index 1.6, flaring index 2.5, flare light curve from Fermi-LAT). Both states scaled by 1.5 in DC5 (a brighter activity epoch)."),
 "NGC_4151": (["Extragalactic/NGC_4151"], "Seyfert galaxy NGC 4151", ["lubinski10", "inoue08"],
   "DC4 model (thermal cutoff power law Gamma=1.75, Ecut=200 keV + non-thermal Gamma=3.8 tail). DC5 increases the thermal (coronal) normalisation by 1.5, representing one of the brighter states of Lubinski et al. (2010); "
   "the non-thermal tail is unchanged. Spectrum: NGC4151_ec200_TH_and_NTH_bright_COSI.dat (thermal norm 0.2235, non-thermal norm 142.8 at 1 keV)."),
 "26Al_Cyg_Region": (["Nucleosynthesis/26Al_Cyg_Region"], "26Al in the Cygnus region", ["martin09"],
   "DC3 model (1808.8 keV line, 1.6 keV FWHM, 3.9e-5 ph/cm2/s at l=81, b=1) with a wider spatial distribution: Gaussian sigma 4.5 deg instead of 3.0 deg. Martin et al. (2009) note 3 deg is a lower limit with ~3 deg uncertainty."),
 "60Fe_NE2001": (["Nucleosynthesis/60Fe_NE2001"], "Galactic diffuse 60Fe (NE2001 model)", ["wang20", "martin10"],
   "DC3 NE2001-based 60Fe map scaled by 0.65 (total Galactic 60Fe mass 3.5 -> 2.3 Msun). The per-line 60Fe/26Al flux ratio becomes 0.12, between Martin et al. (2010, ~0.11) and Wang et al. (2020, 0.18 +- 0.04). "
   "The map is stored uncompressed (82 MB), like the DC3 original, so the pipeline can use it directly."),
 "Tycho": (["Nucleosynthesis/Tycho"], "Tycho SNR, 44Ti", ["lopez15"],
   "Point-like 44Ti line (1157 keV, 4000 km/s broadening). DC5 flux 1.0e-5 ph/cm2/s, equal to the NuSTAR upper limit, instead of 1.6x the limit in DC4."),
 "USco": (["Nucleosynthesis/USco"], "Upper Scorpius, 26Al and 60Fe", ["diehl10"],
   "DC4 extended (9 deg) 26Al and 60Fe model. DC5 halves both 60Fe lines (2.25e-5 ph/cm2/s each), giving a per-line 60Fe/26Al ratio of 0.375 instead of 0.75; still enhanced relative to the Galactic average, as expected for a ~10 Myr old association."),
 "3C273": (["Extragalactic/3C273"], "Quasar 3C 273 (new in DC5, from DC2)", ["madsen15"],
   "DC2 average-state model (8.6e-4 ph/cm2/s, 0.1-10 MeV). Only change: the DC2 transmission-probability line is replaced with the DC3+ settings (range cuts, EarthOccultation false) and an EN terminator is added to the spectrum file."),
 "3C279_high": (["Extragalactic/3C279_high"], "FSRQ 3C 279, high state (new in DC5, from DC3)", ["3c279"],
   "DC3 high-state spectrum (SSC dominated) at its physical flux (DC3 used x100): 1.19e-4 ph/cm2/s, 19.6% polarisation at 45 deg."),
 "PSRB1509": (["Galactic/PSRB1509"], "PSR B1509-58 (new in DC5, from DC2)", ["kuiper15"],
   "DC2 three-band pulsar model with pulse profiles (100-250 keV, 250-750 keV, 0.75-10 MeV). Only change: DC2 transmission-probability lines replaced with the DC3+ settings. Note: uses periodic light curves."),
 "NGC_4945": (["Extragalactic/NGC_4945"], "Seyfert 2 galaxy NGC 4945 (new in DC5)", ["puccetti14"],
   "Cutoff power law, Gamma = 1.9, Ecut = 300 keV (NuSTAR lower limits 200-300 keV), normalised to F(20-100 keV) = 2.0e-10 erg/cm2/s. Absorption is negligible above 100 keV. Flux 4.6e-4 ph/cm2/s (0.1-10 MeV), <1% of the Crab."),
 "IC_4329A": (["Extragalactic/IC_4329A"], "Seyfert 1 galaxy IC 4329A (new in DC5)", ["brenneman14"],
   "Cutoff power law, Gamma = 1.70, Ecut = 178 keV, normalised to the NuSTAR 5-79 keV flux of 3.04e-10 erg/cm2/s. Flux 4.3e-4 ph/cm2/s (0.1-10 MeV)."),
 "GX339m4_hard": (["Galactic/GX339m4_hard"], "Black-hole binary GX 339-4, hard state (new in DC5)", ["gx339"],
   "GX 339-4 in a moderately bright hard-state outburst lasting the full 3 months: cutoff power law Gamma = 1.6, Ecut = 200 keV, F(20-200 keV) = 1.5e-9 erg/cm2/s (~0.15 Crab in that band), 5% polarisation at 20 deg. Flux 2.9e-3 ph/cm2/s (0.1-10 MeV), ~5% of the Crab energy flux."),
 "4U0142p61": (["Galactic/4U0142p61"], "Magnetar 4U 0142+61 (new in DC5)", ["denhartog08a", "kuiper06"],
   "Steady hard tail (no pulsation light curve): log-parabola with local photon index 0.93 at 50 keV and the nuFnu peak at the reported ~228 keV break, normalised to F(20-229 keV) = 1.5e-10 erg/cm2/s. Flux 5.4e-4 ph/cm2/s (0.1-10 MeV)."),
 "26Al_Carina_Region": (["Nucleosynthesis/26Al_Carina_Region"], "26Al in the Carina region (new in DC5)", ["voss12"],
   "1808.8 keV line (same width as the DC3 Cygnus model) from a 2 deg Gaussian centred on Trumpler 16 (l=287.6, b=-0.6) with 1.5e-5 ph/cm2/s, the SPI best-fit value of Voss et al. (2012)."),
 "Ti44_hidden_SNR": (["Nucleosynthesis/Ti44_hidden_SNR"], "Fictitious young SNR, 44Ti (new in DC5)", ["grefenstette"],
   "Arbitrary source: an undiscovered, dust-obscured young SNR in the inner disk. Point-like 44Ti line at 1157.02 keV, 15.4 keV (1 sigma, 4000 km/s) broadening, 1.2e-5 ph/cm2/s, similar to the DC4 Tycho/Kepler models. Position drawn at random."),
 "nova_one_22Na": (["Nucleosynthesis/nova_one_22Na"], "Fictitious ONe nova, 22Na line (new in DC5)", ["hernanz14"],
   "Arbitrary source: an ONe nova at 1.5 kpc that erupted shortly before the observation. 22Na 1274.5 keV line with ~20 keV FWHM (sigma 8.5 keV); flux ~1e-5 ph/cm2/s at 1 kpc (Hernanz 2014) scaled to 4.4e-6. Steady, since the 22Na lifetime (3.75 yr) is much longer than 3 months. Position drawn at random."),
 "Positrons_Point_Source": (["511/Positrons_Point_Source"], "Fictitious compact 511 keV source (new in DC5)", ["guessoum05"],
   "Arbitrary source: steady point-like 511 keV line (e.g. a microquasar or pulsar-wind positron source), 2.5e-5 ph/cm2/s, line width as the DC4 central source (sigma 1.5 keV). Position drawn at random in the disk."),
 "BHXB_hard_transient": (["Galactic/BHXB_hard_transient"], "Fictitious black-hole X-ray binary (new in DC5)", ["cangemi23"],
   "Arbitrary source: new black-hole transient in a long hard-state outburst, cutoff power law Gamma = 1.6, Ecut = 150 keV, 1.5e-3 ph/cm2/s (~2% of the Crab energy flux in 0.1-10 MeV). Steady over 3 months. Position drawn at random near the plane."),
 "PWN_hard_source": (["Galactic/PWN_hard_source"], "Fictitious pulsar wind nebula (new in DC5)", ["kuiper15"],
   "Arbitrary source: Crab-like PWN ~80x fainter than the Crab nebula, power law Gamma = 2.1, 4e-4 ph/cm2/s, 30% polarisation at 100 deg. Position drawn at random in the disk."),
 "magnetar3": (["Galactic/magnetar3"], "Fictitious steady magnetar (new in DC5)", ["denhartog08b"],
   "Arbitrary source: magnetar hard tail without a pulsation light curve. Log-parabola alpha = 1.2, beta = 0.30, pivot 143.3 keV (same functional form as the DC4 magnetars), 2.5e-4 ph/cm2/s, 50% polarisation at 40 deg. Position drawn at random in the disk."),
 "MeV_blazar": (["Extragalactic/MeV_blazar"], "Fictitious MeV blazar (new in DC5)", ["bonnoli11"],
   "Arbitrary source: high-redshift FSRQ with its inverse-Compton peak at ~1 MeV. Log-parabola with local index 2.0 at 1 MeV and beta = 0.2, 3e-4 ph/cm2/s, 15% polarisation. Position drawn at random at |b| > 30 deg."),
 "Seyfert_new": (["Extragalactic/Seyfert_new"], "Fictitious Seyfert galaxy (new in DC5)", ["brenneman14"],
   "Arbitrary source: Seyfert galaxy with Gamma = 1.8, Ecut = 300 keV, 3e-4 ph/cm2/s (several times fainter than NGC 4151). Position drawn at random at |b| > 20 deg."),
 "26Al_new_region": (["Nucleosynthesis/26Al_new_region"], "Fictitious massive-star region, 26Al (new in DC5)", ["martin09", "voss12"],
   "Arbitrary source: an additional OB-association region, 4 deg Gaussian 1808.8 keV line, 1.5e-5 ph/cm2/s (similar to Carina, ~40% of Cygnus). Position drawn at random in the disk."),
}
# components logged individually but documented together
ALIAS = {"nova_co_continuum": "nova_co", "nova_co_511keV": "nova_co", "nova_co_478keV": "nova_co",
         "4C21p35_noflare": "4C21p35", "4C21p35_flare": "4C21p35"}

done = set()
for key, info in log.items():
    if info.get('skip_readme'): continue
    k = ALIAS.get(key, key)
    if k in done: continue
    done.add(k)
    dirs, title, refs, model = CAT[k]
    comps = [c for c, a in ALIAS.items() if a == k] or [key]
    for d in dirs:
        path = os.path.join(ROOT, "sources", d)
        txt = f"# {title} — DC5\n\n"
        txt += f"**DC5 status:** {info['status']}  \n"
        if "origin" in info: txt += f"**Based on:** `{info['origin']}`  \n"
        if "l" in info: txt += f"**Position:** l = {info['l']} deg, b = {info['b']} deg  \n"
        txt += "\n## Model\n\n" + model + "\n\n## Change relative to the DC4 mock dataset\n\n"
        for c in comps:
            txt += f"- {c}: {log[c]['change']}\n" if len(comps) > 1 else f"{log[c]['change']}\n"
        lc = lcflux.get("DC5/sources/" + d, [])
        if lc:
            txt += "\n## Light-curve flux\n\n"
            txt += ("MEGAlib scales a light curve so that its mean over the light curve's time range is 1, so the Flux "
                    "keyword must be the time-averaged flux over that range.\n\n")
            for r in lc:
                if r["verdict"] == "fixed":
                    txt += "- %s: **fixed**, Flux %.6g -> %.6g ph/cm2/s. %s.\n" % (r["component"], r["flux_old"], r["flux_new"], r["note"])
                elif r["verdict"] == "check":
                    txt += "- %s: **to be checked**, not changed. %s.\n" % (r["component"], r["note"])
                else:
                    txt += "- %s: correct, not changed (%s).\n" % (r["component"], r["note"])
        txt += "\nAny other README in this directory describes the original (DC2/DC3/DC4) model; where it conflicts with this file, this file describes what DC5 simulates.\n"
        txt += "\n## References\n\n"
        for r in refs:
            name, url = R[r]
            txt += f"- [{name}]({url})\n" if url else f"- {name}\n"
        txt += "\n_Source file follows the cosi-sim Source_Library conventions; select it in inputs.yaml as `DC5/sources/" + d + "`._\n"
        open(os.path.join(path, "README_DC5.md"), "w").write(txt)
        print("wrote", d)
