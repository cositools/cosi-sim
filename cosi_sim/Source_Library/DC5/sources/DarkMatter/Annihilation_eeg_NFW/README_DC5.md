# Annihilating MeV dark matter (χχ → e⁺e⁻γ, NFW halo) — DC5

**DC5 status:** new component (included in the DC5 mock dataset; the DC4 dark matter files were not part of the DC4 mock dataset)  
**Based on:** `DC4/sources/DarkMatter/Annihilation_eeg_NFW` (Y. Watanabe et al., DC3/DC4 dark matter challenge)  
**Source:** select it in inputs.yaml as `DC5/sources/DarkMatter/Annihilation_eeg_NFW`

## Model

Two dark matter particles annihilate into an e⁺e⁻ pair with a final-state-radiation (FSR) photon. The photon spectrum is the FSR spectrum for √s = 2 m_DM:

dN/dE = (α/π) · (1 + (1 − x)²)/x · [ln(s(1 − x)/m_e²) − 1] · (2/√s), with x = 2E/√s.

The spatial distribution follows an NFW profile with the Cirelli et al. (2011) parameters (r_s = 24.42 kpc, ρ_s = 0.184 GeV cm⁻³, r☉ = 8.33 kpc). The intensity is

dΦ/dE dΩ = ⟨σv⟩ / (8π m_DM²) · J(l, b) · dN/dE,  with J(l, b) = ∫ ρ² ds along the line of sight.

| Parameter | DC4 | DC5 |
|---|---|---|
| DM mass | 30 MeV | **17.3 MeV** |
| ⟨σv⟩ | 1 × 10⁻²⁵ cm³ s⁻¹ | **3.9 × 10⁻²⁸ cm³ s⁻¹** |
| Total flux, 100 keV–10 MeV (whole sky) | 6.1 × 10⁻² ph cm⁻² s⁻¹ | **5.9 × 10⁻⁴ ph cm⁻² s⁻¹** |
| Expected significance in 3 months (see below) | ~500σ | **~5σ** |

The mass was drawn at random (log-uniform between 10 and 60 MeV, at least 20% away from the DC4 mass; seed 1304370250). The FSR endpoint (E = m_DM) is therefore above COSI's band, as in DC4.

## How the map was made

The DC4 map is separable into a spatial J-factor template times one spectrum. Its spectrum matches the formula above to < 1%, and its normalization matches ⟨σv⟩/(8π m²)·J to within 1–4% (10% in the central 1° pixel, where the cusp is pixel-averaged). The DC5 map therefore keeps the DC4 spatial template, sky grid (1° × 0.5°) and the 10 log-spaced energy nodes between 100 keV and 10 MeV. Each energy node k is rescaled by

f_k = (⟨σv⟩/10⁻²⁵) · (30 MeV / m)² · dN/dE(E_k; m) / dN/dE(E_k; 30 MeV),

which ranges from 0.0102 at 100 keV to 0.0077 at 10 MeV. Checks on the written file: same number of grid points as DC4, the spectrum matches the 17.3 MeV FSR shape to < 1%, and the normalization against an independent NFW line-of-sight integral reproduces the DC4 pattern (1.006–1.04 off the centre).

## Expected significance

Wasabi was not reachable from the build environment, so the significance was estimated from the published DC4 mock-dataset count spectra (cosi-data-challenges, `data-products/images/spectrum.png`, digitized into `scripts/dm/dc4_spectrum_digitized.json`):

- **Effective exposure** A(E) = Crab count rate / Crab input spectrum: about 17, 23, 22, 18 and 14 cm² at 0.2, 0.3, 0.5, 1 and 1.8 MeV (time-averaged, DC4 event selection).
- **Exposure of the dark matter region** relative to the Crab, from the DC4/DC5 orientation file (livetime × cos θ, weighted by the NFW template): κ = 0.57. The Galactic centre is exposed less than the Crab, partly because of the orientation-file SAA issue described in the bug report.
- **Background:** the total DC4 background count spectrum, multiplied by the fraction of events whose Compton cones pass through a circular region of interest (ROI) of radius R around the Galactic centre: f = ⟨sin φ⟩ · sin(R + ARM_FWHM), with ⟨sin φ⟩ = 0.64 and ARM from Tomsick et al. (2023), 4.1° at 511 keV and 2.1° at 1809 keV.
- **Signal:** the template flux within R, times 70% ARM containment.
- **Significance:** Z = √(Σ S²/B) over 40 log bins between 0.2 and 5 MeV, maximized over R (statistics only).
- **Calibration:** applied to a point-source narrow line at 1809 keV, the same method is 2.9× more optimistic than COSI's published 3σ, 2-year line sensitivity (3 × 10⁻⁶ ph cm⁻² s⁻¹). All significances are therefore scaled down by that factor. At 511 keV the method is optimistic by a larger factor, as expected because the strong instrumental 511 keV line is left out of the continuum background.

**Result:** Z ≈ 5.0 (calibrated; 14.6 before calibration) for m = 17.3 MeV and ⟨σv⟩ = 3.9 × 10⁻²⁸ cm³ s⁻¹. The best ROI is the full 40° tested, with ~3.7 × 10⁴ signal counts on ~5.6 × 10⁷ background counts. With the same method, the DC4 model would have been detected at ~500σ.

**Caveats:**
- The estimate is uncertain by about a factor of 2 (Z ≈ 2.5–10), and it assumes the background is known exactly.
- The signal is about 0.07% of the background in the ROI and has a smooth, background-like spectrum, so in practice detecting it requires a background model accurate to better than ~0.01%. A detection robust to a 1% background systematic would need ⟨σv⟩ about 75× larger.
- As for DC4, ⟨σv⟩ is above the CMB limit for s-wave annihilation into e⁺e⁻ (≈ 4 × 10⁻²⁸ cm³ s⁻¹ × m/GeV ≈ 7 × 10⁻³⁰ cm³ s⁻¹ at 17.3 MeV). The signal is meant to exercise the analysis, not to represent an allowed s-wave model.

The calculation is in `DC5/scripts/dm/` (`dm_significance.py`, `run_dm_choice.py`), and the map is written by `build_dc5_dm.py`.

## References

- [DC4 dark matter challenge (cosi-data-challenges)](https://github.com/cositools/cosi-data-challenges/tree/develop)
- [Cirelli et al. 2011, JCAP 03, 051 — PPPC 4 DM ID (NFW parameters)](https://arxiv.org/abs/1012.4515)
- [Coogan, Morrison & Profumo 2020, JCAP 01, 056 — Hazma (FSR spectra, scalar mediator)](https://arxiv.org/abs/1907.11846)
- [Tomsick et al. 2023 — COSI mission overview (ARM and line sensitivities)](https://arxiv.org/abs/2308.12362)
- [Caputo et al. 2022 — Dark matter prospects with COSI](https://arxiv.org/abs/2210.09310)
- [cosi-data-challenges backgrounds page (DC4 background components)](https://github.com/cositools/cosi-data-challenges/tree/main/backgrounds)
