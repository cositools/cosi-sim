#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("AllData.ori",sep=r"\s+",skiprows=1,names=["type","time","xb","xl","zb","zl"])
time = df["time"]
xb = df["xb"]
xl = df["xl"]
zb = df["zb"]
zl = df["zl"]

x_list = []
delta_list = []
for i in range(0,len(time)-1):
    
    delta_time = time[i+1] - time[i]
    x_list.append(time[i+1])
    delta_list.append(delta_time)

# Only keep good time bins:
x_list = np.array(x_list)
delta_list = np.array(delta_list)
good_index = delta_list > 0
bad_index = delta_list <= 0

print()
print("Number of negative bins removed:")
print(len(x_list[bad_index]))
print()
print("Min time:")
print(min(time))
print()
print("Max time:")
print(max(time))
print

#plot
fig = plt.figure(figsize=(12,6))
ax = plt.gca()
plt.loglog(x_list[good_index],delta_list[good_index])

# Plot GTIs:
GT = [1463441700.0000000000,1467478260.0000000000]
plt.axvline(x=GT[0],linestyle="-",color="grey")
plt.axvline(x=GT[1],linestyle="-",color="grey",label="GT")

# Before float:
BT = [1463441700.0000000000,1463449500.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="red")
plt.axvline(x=BT[1],linestyle="--",color="red",label="BT: before float")

# System problems:
BT = [1463461800.0000000000, 1463467200.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="orange")
plt.axvline(x=BT[1],linestyle="--",color="orange",label="BT: system problems")

# High shield rates:
BT = [1463794550.0000000000,1463794980.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="cyan")
plt.axvline(x=BT[1],linestyle="--",color="cyan",label="BT: high shield rates")

BT = [1463812560.0000000000,1463816220.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="cyan")
plt.axvline(x=BT[1],linestyle="--",color="cyan")

BT = [1464576960.0000000000,1464589980.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="cyan")
plt.axvline(x=BT[1],linestyle="--",color="cyan")

BT = [1464591000.0000000000,1464599700.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="cyan")
plt.axvline(x=BT[1],linestyle="--",color="cyan")

BT = [1464625080.0000000000,1464625800.0000000000]
plt.axvline(x=BT[0],linestyle="--",color="cyan")
plt.axvline(x=BT[1],linestyle="--",color="cyan")

plt.xlabel("Time [s]",fontsize=14)
plt.ylabel("$\Delta t$ [s]",fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
#plt.xlim(180,-180)
plt.ylim(1e-8,1e8)
plt.grid(color="grey",ls="--",alpha=0.4)
plt.legend(loc=1)
plt.savefig("delta_t_list.png")
plt.show()
