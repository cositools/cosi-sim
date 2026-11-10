# Imports:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# Upload file:
df = pd.read_csv("TP_Earth_occultation_550km_zenith_pointing.dat",sep=r"\s+",skiprows=7,names=["index","theta","energy","probability"])

theta_list = [0.0, 45.0, 90.0, 112.5, 112.98, 145.0, 180.0]
energy_list = [100.0, 1000.0, 5000.0, 10000.0]

theta_index = np.arange(0,len(theta_list),1)
energy_index = np.arange(0,len(energy_list),1)

theta = df["theta"]
energy = df["energy"]
probability = df["probability"]

array_list = []
for each in theta_index: 
    this_column_index = theta == each
    this_column = probability[this_column_index]
    array_list.append(this_column)
array_list = np.array(array_list)
print(array_list)
print(array_list.shape)
np.save("TP",array_list)

# Setup figure:
fig = plt.figure(figsize=(8,8))
ax = plt.gca()

# Plot log scale:
#img = ax.pcolor(energy_list,theta_list,array_list,norm=colors.LogNorm(vmin=1e-6, vmax=1),cmap="viridis")

# Plot:
img = ax.pcolormesh(energy_list,theta_list,array_list,shading="auto",cmap="viridis")
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

cbar = plt.colorbar(img,fraction=0.045)
cbar.set_label("Probability",size=16,labelpad=12)
cbar.ax.tick_params(labelsize=12)

plt.ylabel('Zenith Angle [$\circ$]',fontsize=18)
plt.xlabel('Energy [keV]',fontsize=18)
plt.title('Transmission Probability', fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

ax.tick_params(axis='both',which='major',length=9)
ax.tick_params(axis='both',which='minor',length=5)

#plt.grid(lw=1,ls="--",color="grey",alpha=0.3)
plt.xlim(1e2,1e4)
plt.ylim(0,180)
plt.xscale("log")
plt.savefig("transmission_probability.png",bbox_inches='tight')
plt.show()

