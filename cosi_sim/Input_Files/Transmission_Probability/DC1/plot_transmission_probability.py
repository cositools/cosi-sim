# Imports:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# Upload file:
df = pd.read_csv("TransmissionProbability_33000.dat",sep=r"\s+",skiprows=7,names=["index","theta","energy","probability"])

theta_list = [0.0,5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,90.0001,180.0]
energy_list = [50.0,60.0,80.0,100.0,150.0,200.0,300.0,400.0,500.0,600.0,800.0,1000.0,1022.0,1250.0,1500.0,2000.0,2044.0,3000.0,4000.0,5000.0,6000.0,7000.0,8000.0,9000.0,10000.0]

theta_index = np.arange(0,21,1)
energy_index = np.arange(0,25,1)

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


# Setup figure:
fig = plt.figure(figsize=(8,8))
ax = plt.gca()

# Plot log scale:
#img = ax.pcolor(energy_list,theta_list,array_list,norm=colors.LogNorm(vmin=1e-6, vmax=1),cmap="viridis")

# Plot:
img = ax.pcolormesh(energy_list,theta_list,array_list,cmap="viridis",vmin=0,vmax=1)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

cbar = plt.colorbar(img,fraction=0.045)
cbar.set_label("Probability",size=16,labelpad=12)
cbar.ax.tick_params(labelsize=12)

plt.ylabel('Zenith Angle [$\circ$]',fontsize=18)
plt.xlabel('Energy [keV]',fontsize=18)
plt.title('Transmission Probability (33 km)', fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

ax.tick_params(axis='both',which='major',length=9)
ax.tick_params(axis='both',which='minor',length=5)

#plt.grid(lw=1,ls="--",color="grey",alpha=0.3)
#plt.xlim(179.5,-179.5)
plt.xscale("log")
plt.savefig("transmission_probability.png",bbox_inches='tight')
plt.show()

