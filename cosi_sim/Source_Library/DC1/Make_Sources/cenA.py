# Imports:
from SpectralModels import Band
from scipy.interpolate import interp1d
from scipy import integrate
import pandas as pd

def cenA_flux(energy_range, elow, ehigh):

    """cenA flux"""

    # Cen A (from HESS+LAT 2018)
    src_name = "cenA"
    gal_l = 309.516
    gal_b = 19.417

    # Spectrum:
    df = pd.read_csv("cenA.txt",sep=r"\s+")
    energy = df["energy[eV]"]*(1.0/1000.0) #keV
    flux = df["flux[erg/cm^2/s]"] #erg/cm^2/s
    flux = flux*6.242e8 #keV/cm^2/s
    func = interp1d(energy,flux,kind="linear",bounds_error=False,fill_value="extrapolate")
    photons = func(energy_range)/energy_range**2 #ph/cm^2/s/keV
    func2 = interp1d(energy_range,photons,kind="linear",bounds_error=False,fill_value="extrapolate")

    #integrated flux for source file:
    intg = integrate.quad(func2,elow,ehigh)[0]
    intg = float("{:.6f}".format(intg))
    print()
    print("cenA flux between %s keV - %s keV [ph/cm^2/s]: " %(str(elow),str(ehigh)) + str(intg))
    print()

    return src_name, photons, intg 
