# Imports:
import pandas as pd
import matplotlib.pyplot as plt


#setup figure:
fig = plt.figure(figsize=(9,6))
ax = plt.gca()

source_list = ["crab","cygX1","cenA","vela"]
line_styles = ["-","--","-.",":"]
colors = ["cornflowerblue","darkorange","purple","green"]

path = "/zfs/astrohe/ckarwin/My_Class_Library/COSI/Data_Challenge/Source_Library/"

for i in range(0,len(source_list)):
    this_name = source_list[i]
    this_file = path + this_name + "/" + this_name + "_spec.dat"
    df = pd.read_csv(this_file,skiprows=6,sep=r"\s+",names=["ID","energy[keV]","flux[ph/cm^2/s/keV]"])
    energy = df["energy[keV]"]
    flux = energy**2 * df["flux[ph/cm^2/s/keV]"]*1.60218e-9 # erg/cm^2/s
    plt.loglog(energy,flux,ls=line_styles[i],color=colors[i],label=this_name)

#plot COSI range:
plt.vlines(2e2,1e-15,1e-7,color="grey",linestyles="--",alpha=0.5,label="COSI range")
plt.vlines(5e3,1e-15,1e-7,color="grey",linestyles="--",alpha=0.5)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("Energy [keV]", fontsize=14)
plt.ylabel("$\mathrm{E^2 \ dN/dE \ [erg \ cm^{-2} \ s^{-1}]}$", fontsize=14)
plt.title("Data Challenge 1",fontsize=14)
plt.ylim(1e-12,1e-7)
plt.xlim(70,7e4)
#plt.grid(color="grey",alpha=0.3,ls="-")
plt.legend(loc=1,frameon=False)
plt.savefig("data_challenge_1.pdf")
plt.show()
