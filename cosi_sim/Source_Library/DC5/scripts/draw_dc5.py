"""Random draw of the DC5 reuse / modify / remove split, starting from the DC4 mock dataset.
Units group files that are components of one physical source. GRBs are excluded (kept as-is)."""
import random, secrets, json, sys
seed = int(sys.argv[1]) if len(sys.argv) > 1 else secrets.randbits(32)
rng = random.Random(seed)
# name: (n_files, removable)
units = {
 "Crab":(1,False), "cygX3":(1,False), "cygX1_hard":(1,False), "CenA":(1,False), "NGC_4151":(1,False),
 "NB_511":(1,False), "BB_511":(1,False), "Positrons_Central_Source":(1,False), "Positrons_Thin_Disk":(2,False),
 "Positrons_In_Flight_Annihilation":(1,False), "Positrons_from_26Al":(2,False), "Positrons_from_44Ti":(2,False),
 "26Al_NE2001":(1,False), "60Fe_NE2001":(1,False), "26Al_Cyg_Region":(1,False), "CasAG16distribution":(1,False),
 "1E1740_compow":(1,False), "GRS1758":(1,False), "3C454p3":(2,False), "4C71p07":(1,False),
 "G1903":(1,True), "Kepler":(1,True), "OrEr":(1,True), "SN1987A":(1,True), "Tycho":(1,True), "USco":(1,True),
 "VelaJr_44Ti":(1,True), "LMC_511":(1,True), "M31_511":(1,True), "Virgo_511":(1,True), "NGC_1068":(1,True),
 "1RXSJ170849":(1,True), "magnetar2":(1,True), "GC_Tuc_47":(1,True), "GC_Omega_Cen":(1,True),
 "GC_NGC_6397":(1,True), "GC_NGC_6121":(1,True), "Vela_SNR_511":(1,True), "nova_co":(3,True),
 "4C21p35":(2,True), "PSRB1259":(1,True), "LS5039":(1,True), "PSRJ1846":(1,True), "MAXIJ1820":(1,True),
 "MAXIJ1348":(1,True), "60Fe_Cyg_Region":(1,True),
}
N = sum(n for n,_ in units.values())
names = list(units); rng.shuffle(names)
removed, modified, reused = [], [], []
nrem = nmod = 0
for u in names:
    n, removable = units[u]
    if removable and nrem + n <= round(0.10*N) and n == 1:
        removed.append(u); nrem += n
    elif nmod + n <= round(0.40*N) + 1 and nmod < round(0.40*N):
        modified.append(u); nmod += n
    else:
        reused.append(u)
nreu = sum(units[u][0] for u in reused)
out = dict(seed=seed, n_files=N, n_units=len(units),
           removed=sorted(removed), modified=sorted(modified), reused=sorted(reused),
           files=dict(removed=nrem, modified=nmod, reused=nreu))
print(json.dumps(out, indent=1))
