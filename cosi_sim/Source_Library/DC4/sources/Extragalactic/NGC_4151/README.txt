###########################################
#
##-- Created by Parshad Patel, February 19 2026
#
###########################################

This folder contains the spectral model of the AGN NGC 4151. 

The columns in each file are: Format <Energy in keV> <Spectrum in ph cm^-2 s^-1 keV^-1>
The energy band used is 100 keV to 10000 keV


The baseline model is a cutoff power law (thermal electrons) + a powerlaw (non-thermal tail). The model papers: Lubinski+2010 (thermal), Inoue+2008 (non-thermal).


NGC4151_ec200_TH_and_NTH_COSI.dat:

Thermal: Gamma=1.75, Ecut=200 keV; Norm at 1 keV = 0.149 keV-1 s-1 cm-2
Non-Thermal: Gamma=3.8; Norm at 1 keV = 142.8 keV-1 s-1 cm-2

The goal of these data for COSI is: determine flux in the COSI band, coronal cut-off location, and flux/index for the non-thermal tail.



