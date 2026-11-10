#imports
import pandas as pd
import numpy as np

ori_file = "modified_2hr_pointing.ori"
df = pd.read_csv(ori_file,sep=r"\s+",skiprows=[0,7202],names=["type","time","xb","xl","zb","zl"])
print(df)
time = df["time"]
xb = df["xb"]
xl = df["xl"]
zb = df["zb"]
zl = df["zl"]

dp = ["DP"]*len(time)
flux = [0]*len(time)
flux = np.array(flux)
time = np.array(time)
change_index = np.isin(time,[1878.0,1879.0,1880.0])
flux[change_index] = 1

d = {"dp":dp,"time":time,"flux":flux}
df = pd.DataFrame(data = d, columns = ["dp","time","flux"])
df.to_csv("modified_lc.dat",sep="\t",index=False,header=False)
