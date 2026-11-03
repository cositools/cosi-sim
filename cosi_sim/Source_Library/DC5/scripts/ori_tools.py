"""Minimal orientation-file tools (same column convention as cosipy SpacecraftHistory._open_ori)."""
import gzip, numpy as np
def load_ori(path):
    op = gzip.open if path.endswith('.gz') else open
    rows = []
    with op(path, 'rt') as f:
        for line in f:
            if line.startswith('OG'): rows.append(line.split()[1:10])
    a = np.array(rows, float)
    return dict(t=a[:,0], xb=a[:,1], xl=a[:,2], zb=a[:,3], zl=a[:,4], alt=a[:,5], eb=a[:,6], el=a[:,7], live=a[:,8])
def unit(l, b):
    l, b = np.radians(l), np.radians(b)
    return np.stack([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)], -1)
def ang(u1, u2):
    return np.degrees(np.arccos(np.clip(np.sum(u1*u2, -1), -1, 1)))
def geometry(ori, l, b, t):
    """Off-axis angle (z-axis to source) and zenith angle at times t (nearest earlier 15 s bin)."""
    i = np.clip(np.searchsorted(ori['t'], t, side='right') - 1, 0, len(ori['t'])-1)
    s = unit(l, b)
    return ang(unit(ori['zl'][i], ori['zb'][i]), s), ang(unit(ori['el'][i], ori['eb'][i]), s), ori['live'][i], i
