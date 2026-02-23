This DC features 2 magnetars:
1. the magnetar (AXP) 1RXS J170849.0-400901. The resons to focus on this magnetar are:
    * GLON, GLAT: 346.47938142, 0.03838608
2. A generic magnetar with slightly different parameters than 1RXS J1780849.0-400901
    * GLON, GLAT: 250, 0.03838608


The models used are based on _Hartog, Kuiper and Hermsen 2008_ (https://drive.google.com/drive/u/0/home)

The Challenges:
---------------
* Can COSI detect the magnetar? (i.e. detect he pulsations?)
* Can COSI detect the turn over in the spectrum? and discriminate between 2 slightly different spectra?
* Can COSI detect polarization?

The Spectrum:
-------------
The spectrum is a log parabola in the MeV energy range:

    def log_parabola(x, norm, alpha, beta, pivot):
        var = x/pivot
        spec = norm * var**(-alpha-beta*np.log(var))
        return spec

The assumed parameters for J1780849.0-400901 are:
* alpha = 1.637
* beta = 0.261  
* norm = 1.68e-6 ph/cm2/s/keV 
* pivot = 143.276 keV

The assumed parameters for the generic magnetar are:
* alpha = 1.637
* beta = 0.261 x 2
* norm = 1.68e-6 ph/cm2/s/keV 
* pivot = 143.276 keV


The Polarization:
-----------------
For this challenge the polarization is assumed energy independent in the COSI band with a phase-integrated polarization degree of 
1. 80% (PA=-30 deg in Galactic coordinates) for 1RXS
2. 40% (PA=-75 deg in Galactic coordinates) for the generic magnetar

The Lightcurve:
---------------
The file _1RXSJ170849_magnetar_lightcurve.dat_ contains the periodic lightcurve of 1RXS:
* Period: P = 11.00502461 s
* Period derivative: Pdot = 1.95E-11 s/s
* Pulsed Fraction: PF = 0.5 

The file _magnetar2_lightcurve.dat_ contains the periodic lightcurve of the generic magnetar:
* Period: P = 11.00502461 / 2 s 
* Period derivative: Pdot = 1.95E-11 s/s
* Pulsed Fraction: PF = 0.5 

The Pulsed fraction is defined as (Fmax - Fmin)/(Fmax + Fmin), with F being the flux.
