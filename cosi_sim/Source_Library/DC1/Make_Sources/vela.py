# Imports:
from SpectralModels import Band
from scipy.interpolate import interp1d
from scipy import integrate
import pandas as pd
from fermi_srcs import FermiSources

def vela_flux(energy_range, elow, ehigh):

    """vela flux"""

    src_name = "vela"
    gal_l = 263.552
    gal_b = -2.787

    # Spectrum:
    df = pd.read_csv("vela.txt",sep=r"\s+")
    energy = df["energy[eV]"]*(1.0/1000.0) #keV
    flux = df["flux[erg/cm^2/s]"] #erg/cm^2/s
    flux = flux*6.242e8 #keV/cm^2/s
    photons = flux/(energy**2)
    func = interp1d(energy,photons,kind="linear",bounds_error=False,fill_value="extrapolate")

    # Extrapolate from LAT 4FGL 
    fermi_instance = FermiSources()
    energy_range_MeV = energy_range/1.0e3
    lat_flux = fermi_instance.get_flux("4FGL J0835.3-4510",energy_range_MeV) # pulsar, ph/cm^2/s/MeV
    lat_flux = lat_flux / 1000.0 # ph/cm^2/s/keV

    # Integrated flux for source file:
    func = interp1d(energy_range,lat_flux,kind="linear",bounds_error=False,fill_value="extrapolate")
    intg = integrate.quad(func,elow,ehigh)[0]
    intg = float("{:.6f}".format(intg))
    print()
    print("vela flux between %s keV - %s keV [ph/cm^2/s]: " %(str(elow),str(ehigh)) + str(intg))
    print()

    return src_name, lat_flux, intg
