2026/January/27 Pierre Jean

This is the description of the model of the diffuse positron annihilation emissions from the galactic thin disk.

The spatial distribution is based on an axisymmetric 3D gaussian distribution of annihilation sources in our Galaxy, with a radial width of 14 kpc rms and a height width of 0.7 kpc rms. 
This model has been build such as to ressemble to the best fitting 2D from Skinner et al. (2014 - https://pos.sissa.it/228/054/pdf).
The spectral distribution takes into account the annihilation line and the orthopositronium continuum assuming that 50% of the annihilations occur in warm neutral phase and 50% occur in warm ionized phase of the interstellar medium. The spectral shapes were obtained with the model of Guessoum et al (2005 - https://ui.adsabs.harvard.edu/abs/2005A%26A...436..171G/abstract) that computes a spectrum for each phase of the interstellar medium. The spectrals models were corrected by the Doppler effect due to the Galactic rotation using the model of Fich, Blitz and Stark (1989 - https://ui.adsabs.harvard.edu/abs/1989ApJ...342..272F/abstract) for R > 3 kpc and a solid rotation model for R < 3 kpc.
The fluxes of the Thin Disk models are such as the total 511 keV flux in the Thin Disk is of 1.66e-3 ph/s/cm2 (Siegert et al. 2016 - https://ui.adsabs.harvard.edu/abs/2016A%26A...586A..84S/abstract) taking into account that the 511 keV flux in the "positrons from 26Al" model (used in the DC3) is of 0.32e-3 ph/s/cm2 and that the 511 keV flux in the "positrons from 44Ti" model (used in the DC3) is of 0.37e-3 ph/s/cm2. 

The spectral distribution has been separated into two files in order to reduce the size of the input files: the line (_line) and the ortho-positronium continuum (_cont). 
The input file Positrons_Thin_Disk_line.dat contains the intensity (ph/s/cm2/keV/sr) as a function of the Galactic coordinates and the photon energy (l, b, E) with a binning of 1 deg x 1 deg x 0.2 keV
The input file Positrons_Thin_Disk_cont.dat contains the intensity (ph/s/cm2/keV/sr) as a function of the Galactic coordinates and the photon energy (l, b, E) with a binning of 1 deg x 1 deg x 5.0 keV
The files Positrons_Thin_Disk_line.source and Positrons_Thin_Disk_cont.source should be used for the simulations.

Goal: Detection of the diffuse line and continuum emissions, detection of the Doppler shift in the disk, detection of the spectral shape. 
