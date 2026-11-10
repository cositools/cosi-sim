2024/July/16 Pierre Jean

This is the description of the model of the diffuse emission of the 1173 keV and 1332 keV lines due decay of 60Fe in our Galaxy.

The spatial distribution is derived from the model NE2001 of Cordes & Lazio (2002, https://arxiv.org/abs/astro-ph/0207156) that fits 
the distribution of massive stars in our Galaxy. The fraction of 60Fe in the bulge is 2%. This value is the same as the one of the 26Al, 
which is a compromise between SPI observations and results of studies of star formation rate in this region. The flux is computed assuming a
total mass of 60Fe of 3.5 M_sol in our Galaxy (see Wang et al., 2020 - https://ui.adsabs.harvard.edu/abs/2020ApJ...889..169W/abstract - and 
Siegert et al. 2023 - https://ui.adsabs.harvard.edu/abs/2023A%26A...672A..54S/abstract).
The shape of the line in each spatial bin takes into account the turbulence of the interstellar medium and the Galactic rotation using the model 
of Fich, Blitz and Stark (1989 - https://ui.adsabs.harvard.edu/abs/1989ApJ...342..272F/abstract) for R > 3 kpc and a solid rotation model for R < 3 kpc.

The input fits file (3Dmap_60Fe_ne2001_v2.fits.gz) contains the intensity (ph/s/cm2/keV/sr) as a function of the Galactic coordinates and the photon energy (l, b, E) with a binning of 1 deg x 1 deg x 0.1 keV. The input files has 3 extensions:
> primary extension => intensity matrix
> second extension => longitude values (deg)
> third extension => latitude values (deg)
> fourth extension => energy values (keV)
The fits file (3Dmap_60Fe_ne2001_v2.fits.gz) has been converted to the COSIMA-specific format ("3D Functions"): 3Dmap_60Fe_ne2001_v2.dat

Goal: Detection of the diffuse emission, extraction of the F(26Al)/F(60Fe) ratio and its uncertainty.


2025/January/28 Pierre Jean

The energy binning has been changed in order to reduce the size of the input files.
The new fits files (3Dmap_60Fe_ne2001_v2_1.fits.gz) has been converted to the COSIMA-specific format ("3D Functions"): 3Dmap_60Fe_ne2001_v2_1.dat.gz.
