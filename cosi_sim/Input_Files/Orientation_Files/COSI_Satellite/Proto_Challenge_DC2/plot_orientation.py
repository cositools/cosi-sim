#imports
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("20280301_first_2hrs.ori",sep=r"\s+",skiprows=[0,7202],names=["type","time","xb","xl","zb","zl"])
print(df)
time = df["time"]
xb = df["xb"]
xl = df["xl"]
zb = df["zb"]
zl = df["zl"]

#convert longitude to standard Galactic coordinates:
neg_index = zl > 180
zl[neg_index] = zl[neg_index] - 360

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

#plot
fig = plt.figure(figsize=(9,6))
ax = plt.gca()
plt.scatter(zl, zb, c=time,cmap='viridis')
cbar = plt.colorbar()
cbar.set_label("Time [s]",size=14,labelpad=12)
plt.xlabel("Galactic Longitude [$\circ$]",fontsize=14)
plt.ylabel("Galactic Latitude [$\circ$]",fontsize=14)
plt.title("z-orientation",fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlim(180,-180)
plt.ylim(-90,90)
plt.grid(color="grey",ls="--",alpha=0.4)
plt.savefig("zpointing.png")
plt.show()
