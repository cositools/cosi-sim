2024/June/23 Che-Yen Jimmy Chu
This is the description to the source model of magnetar bursts (SRG 1935+2154 and 1E 1048.1-5937)
2 light curves and 2 different flux levels are included in DC3

Goal: to test whether magnetar bursts are detectable by COSI GeDs.
If they are not detectable, we may artificially increase the flux to evaluate the detector's efficiency in capturing these bursts.
If they are detectable, we can focus on localizing the bursts and analyzing their light curves and spectra.
Based on our current estimations, we expect non-detection.

Burst 1: SGR 1935+2154, a bright burst with complex light curve (source file: MgtBurst_bright_complex.source)
Burst 2: 1E 1048.1-5937, a dim burst with simple light curve (source file: MgtBurst_dim_simple.source)
Burst 3: spectrum of SGR 1935 burst + light curve of 1E 1048 burst (source file: MgtBurst_bright_simple.source)
==> a bright burst with simple light curve
Burst 4: spectrum of 1E 1048 burst + light curve of SGR 1935 burst (source file: MgtBurst_dim_complex.source)
==> a dim burst with complex light curve

Reference:
SGR 1935+2154: Li, et al., 2021, NatAstron., 5, 378
A bright burst with radio conterpart (FRB) confirmed
Light curve: using 10-30 keV light curve since 27-250 keV light curve suffers pile-up
Spectrum: using cutoff power-law with power index 1.56 and cutoff energy 83.89

1E 1048.1-5937: Gavriil, et al., 2002, Nature, 419, 142
The first burst which was discovery from an AXP (not from SGR)
Light curve: using 2-20 keV light curve
Spectrum: using cutoff power-law with power index 0.89 and assumed* cutoff energy 37.01
*The spectrum fitting reported is up to 40 keV, which makes the cutoff hard to idnetify, so I choose the avereged cutoff energy of magnetar burst (Collazzi, et al., 2015, ApJS, 218, 11).

Note:
These models are for DC3 with the standard energy range (0.1-10 MeV). However, magnetar bursts are too dim and too soft to be detected by COSI GeDs. Therefore, I have prepared another set with a lower energy range (10-500 keV) for future data challenges, as we may use them for shield analysis. Please see the directory "For_shields" for the content.