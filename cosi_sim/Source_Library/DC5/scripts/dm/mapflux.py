"""Integrate a cosima NormalizedEnergyBeamFluxFunction (.dat) map.
AP i j k value: i=phi index, j=theta index, k=energy index; value in ph/cm2/s/keV/sr.
Linear interpolation in all axes -> trapezoid integration."""
import sys, gzip, numpy as np
def load(path):
    op = gzip.open if path.endswith('.gz') else open
    pa=ta=ea=None; rows=[]
    with op(path,'rt') as f:
        for line in f:
            s=line.split()
            if not s: continue
            if s[0]=='PA': pa=np.array(s[1:],float)
            elif s[0]=='TA': ta=np.array(s[1:],float)
            elif s[0]=='EA': ea=np.array(s[1:],float)
            elif s[0]=='AP': rows.append(s[1:5])
    a=np.array(rows,float)
    cube=np.zeros((len(pa),len(ta),len(ea)))
    cube[a[:,0].astype(int),a[:,1].astype(int),a[:,2].astype(int)]=a[:,3]
    return pa,ta,ea,cube
def flux(pa,ta,ea,cube):
    th=np.radians(ta); ph=np.radians(pa)
    w=np.sin(th)[None,:,None]
    integ=np.trapezoid(np.trapezoid(cube*w,th,axis=1),ph,axis=0)  # per energy node, ph/cm2/s/keV
    return integ, (np.trapezoid(integ,ea) if len(ea)>1 else integ[0])
if __name__=='__main__':
    for p in sys.argv[1:]:
        pa,ta,ea,c=load(p); per,tot=flux(pa,ta,ea,c)
        # peak position
        idx=np.unravel_index(np.argmax(c[:,:,len(ea)//2] if len(ea)>1 else c[:,:,0]),c.shape[:2])
        print(f"{p}: E nodes={ea[:5]}{'...' if len(ea)>5 else ''} n={len(ea)}  F(E-node)={per[:5]}  total={tot:.4e}  peak phi={pa[idx[0]]} theta={ta[idx[1]]}")
