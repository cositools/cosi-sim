# Inputs:
from galpy.GalMaps import *
import numpy as np
import math
from scipy import stats, interpolate
from scipy.stats import gmean
from astropy.wcs import WCS
from astropy.io import fits

# These examples extract events from a 47.5 degree box around the Galactic center.

# Running healpix:
#this_file = "full/path/to/GALPROP/healpix/output"
#instance = GalMapsHeal()
#instance.read_healpix_file(this_file,verbose=False)
#instance.make_healmap(7)
#pixs=instance.get_polygon_region([42.5,137.5,137.5,42.5],[47.5,47.5,312.5,312.5]) 
#instance.mask_region(pixs)
#pixs=instance.get_disk_region(90,0,30)
#instance.plot_healmap("skymap.png",fig_kwargs={'title':"example"},plot_kwargs={'norm':'log'})
#instance.make_spectrum(pixs=pixs) 
#instance.write_spectrum("output_spectrum.dat")
#instance.plot_spectrum("spectra.pdf")


# inputs: 
int_flux = 3.5e-4 # ph/cm2/s 
pix_area = 7.2e-6 # sr

# Running fits: 
hdu = fits.open("vela_511_100.fits")
print(hdu.info())

# scale file to give correct integrated flux:
data = hdu[0].data 
total = np.sum(data)
scaling_factor = int_flux/(pix_area*total)
data = scaling_factor * data

print()
print("Sanity check on integrated flux:")
print(np.sum(data)*pix_area)
print()

data /= 0.001 # per 0.001 MeV
header = hdu[0].header
wcs = WCS(header)
energy = [0.510,0.511,0.512]

instance = GalMapsFITS()
instance.read_fits_objects(energy,data,wcs)
instance.gal2mega("fits","vela_511_100",use_2d=True)

#instance.read_fits_file(galdiff)
#pixs=instance.get_fits_region([-47.5,47.5],[0,47.5],lon2=[312.5,360])
#instance.make_spectrum(pixs)
#instance.write_spectrum("output_spectrum.dat")

# Running Utils:
#instance = Utils()

# Sum origianl spectra:
#instance.sum_spectra("output_spectrum_1.dat","output_spectrum_2.dat")

# Plot (mult) spectra:
#inputs = ["output_spectrum_1.dat","output_spectrum_2.dat"]
#labels = ["model1","model2"]
#ls = ['-','--']
#color = ['blue','orange']
#savefile="all_spectra.pdf"
#instance.plot_mult_spectra(savefile,inputs,labels,\
#        fig_kwargs={'title':'Inner Galaxy ($|l| < 47.5^\circ; |b|<47.5^\circ$)',\
#        'ylim':(1e-4,1e0),'xlim':(1e-2,1e4)},\
#        plot_kwargs={'ls':ls,'color':color},show_plot=True)
