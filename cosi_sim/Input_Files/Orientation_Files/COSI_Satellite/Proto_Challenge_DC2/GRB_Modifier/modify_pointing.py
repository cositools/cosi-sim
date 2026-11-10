#imports
import pandas as pd
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord

ori_file = "../20280301_first_2hrs.ori"

df = pd.read_csv(ori_file,sep=r"\s+",skiprows=[0,7202],names=["type","time","xb","xl","zb","zl"])
print(df)
col0 = df["type"]
time = df["time"]
xb = df["xb"]
xl = df["xl"]
zb = df["zb"]
zl = df["zl"]

#convert longitude to standard Galactic coordinates:
#neg_index = zl > 180
#zl[neg_index] = zl[neg_index] - 360

#get total time:
total_time = max(time) - min(time) # seconds
hrs = total_time * (1/3600.0) # hours
days = hrs / 24.0 # days
print()
print("total_time [s]:")
print(total_time)
print("total time [hrs]:")
print(hrs)
print("total days:")
print(days)

# Get modified time:
new_time = time - np.amin(time)
print()
print("Time constant: " + str(np.amin(time)))
print()

# Write new file:
f = open("modified_2hr_pointing.ori","w")
f.write("Type OrientationsGalactic\n")

for i in range(0,len(new_time)):
    
    this_line = col0[i] + "\t" + str(new_time[i]) + "\t" + str(xb[i]) + "\t" \
              + str(xl[i]) + "\t" + str(zb[i]) + "\t" + str(zl[i]) + "\n"
    
    f.write(this_line)

f.write("EN")
f.close()

# Get time for desired offset,
# by calculating angular separation:
my_l, my_b = 340, 45
ang_max = 20.1
ang_min = 19.9
c1 = SkyCoord(zl*u.deg, zb*u.deg, frame='galactic')
c2 = SkyCoord(my_l*u.deg, my_b*u.deg, frame='galactic')
sep = c2.separation(c1)
sep_index = (ang_max*u.deg > sep) & (sep > ang_min*u.deg)
print()
print("Separations:")
print(sep.deg[sep_index])
print()
print("Times:")
print(np.array(new_time)[sep_index])
