import numpy as np
# J2000 ICRS -> Galactic rotation (Hipparcos / Liu et al.)
R = np.array([[-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
              [ 0.4941094278755837, -0.4448296299600112,  0.7469822444972189],
              [-0.8676661490190047, -0.1980763734312015,  0.4559837761750669]])
def eq2gal(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    v = np.array([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
    g = R @ v
    return np.degrees(np.arctan2(g[1], g[0])) % 360, np.degrees(np.arcsin(g[2]))
def hms(h,m,s): return 15*(h+m/60+s/3600)
def dms(d,m,s): sg=-1 if str(d).startswith('-') else 1; return sg*(abs(d)+m/60+s/3600)
if __name__=='__main__':
    for n,ra,dec in [("Crab check",hms(5,34,31.94),dms(22,0,52.2)),("NGC4945",hms(13,5,27.5),dms(-49,28,6)),
                     ("IC4329A",hms(13,49,19.27),dms(-30,18,34.0)),("GX339-4",hms(17,2,49.38),dms(-48,47,23.2)),
                     ("4U0142+61",hms(1,46,22.41),dms(61,45,3.2))]:
        l,b=eq2gal(ra,dec); print(f"{n}: l={l:.4f} b={b:.4f}")
