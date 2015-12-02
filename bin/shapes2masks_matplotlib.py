# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%matplotlib inline
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.pyplot as plt

# <codecell>

# generate some fake data
xmin, xmax, ymin, ymax = -10, 30, -4, 20
y,x = np.mgrid[ymin:ymax+1,xmin:xmax+1]
z = (x-(xmin+xmax)/2)**2 + (y-(ymin + ymax)/2)**2
extent = [xmin-.5, xmax+.5, ymin-.5, ymax+.5]
xr, yr = [np.random.random_integers(lo, hi, 5) for lo, hi
         in ((xmin, xmax), (ymin, ymax))] # generates 3 random integers within the bounds to create a polygon.

# <codecell>

print xr, yr

# <codecell>

coordlist = np.vstack((xr, yr)).T  # create an Nx2 array of coordinates
coord_map = np.vstack((x.flatten(), y.flatten())).T # create an Mx2 array listing all the coordinates in field

# <codecell>

print coord_map

# <codecell>

polypath = Path(coordlist)
mask = polypath.contains_points(coord_map, radius=0.0).reshape(x.shape) # have mpl figure out which coords are within the contour

# <codecell>

f, ax = plt.subplots(1,1)
ax.imshow(z, extent=extent, interpolation='none', origin='lower', cmap='hot')
ax.imshow(mask, interpolation='none', extent=extent, origin='lower', alpha=.5, cmap='gray')
patch = PathPatch(polypath, facecolor='g', alpha=.5)
ax.add_patch(patch)
plt.show()
#print(z[mask].sum())  # prints out the total accumulated

# <codecell>

plt.imshow(mask, interpolation='none')

# <codecell>


