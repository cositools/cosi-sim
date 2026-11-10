# Imports:
from SpectralModels import Band
from scipy.interpolate import interp1d
from scipy import integrate
import pandas as pd
from fermi_srcs import FermiSources

def cygX1_flux(energy_range, elow, ehigh):

    """cygX1 flux"""

    src_name = "cygX1"
    gal_l = 71.33496
    gal_b = 3.066917

    df = pd.read_csv("Cyg_X1.dat",skiprows=1,sep=r"\s+")
    energy = df["energy[eV]"]*(1.0/1000.0) #keV
    flux = df["flux[erg/cm^2/s]"] #erg/cm^2/s
    flux = flux*6.242e8 #keV/cm^2/s
    func = interp1d(energy,flux,kind="linear",bounds_error=False,fill_value="extrapolate")
    photons = func(energy_range)/(energy_range**2) #ph/cm^2/s/keV
    func2 = interp1d(energy_range,photons,kind="linear",bounds_error=False,fill_value="extrapolate")

    #integrated flux for source file:
    intg = integrate.quad(func2,elow,ehigh)[0]
    intg = float("{:.6f}".format(intg))
    print()
    print("Cyg X-1 flux between %s keV - %s keV [ph/cm^2/s]: " %(str(elow),str(ehigh)) + str(intg))
    print()

    return src_name, photons, intg
