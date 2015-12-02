# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%matplotlib inline
import netCDF4
import numpy as np
from numpy import ma
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import shapely.geometry

# <codecell>

avg = netCDF4.Dataset('/home/will/Projects/bering-seabird-vulnerability/resources/cccma_h1_average.nc')
# Load latitude and longitude arrays
latitude = np.array(avg.variables['LATITUDE'])
longitude = np.array(avg.variables['LONGITUDE'])

#Generate grids using the lon and lat values, where each location
#is identified by a lon/lat value.
x,y = np.meshgrid(longitude, latitude)

#Get a mask from the first variable
sample = ma.masked_array(avg.variables['temp_latlon'][:])
mask=ma.getmask(sample)

# <rawcell>

# Here's where we'd import a shape file.

# <codecell>

from osgeo import gdal, gdalnumeric, ogr, osr

# <codecell>

from cartopy.io import shapereader
shp=shapereader.Reader("/home/will/Projects/bering-seabird-vulnerability/resources/MEOW_LME_Poly_GCS.shp")
print len(shp)
shps = shp.records()

# <codecell>

lme = next(shps)

# <codecell>

print lme.geometry.geom_type
print lme.geometry.bounds

# <codecell>

print lme

# <codecell>

from shapely.ops import cascaded_union
geoms = shp.geometries()
polygon = cascaded_union(list(geoms))

# <codecell>

print polygon

# <codecell>

polygon =lme.geometry

# <codecell>

from shapely.geometry import Point

def inpolygon(polygon, xp, yp):
    return np.array([Point(x, y).intersects(polygon) for x, y in zip(xp, yp)],
                    dtype=np.bool)

# <codecell>

mask = inpolygon(polygon, x.ravel(), y.ravel())

# <codecell>

mask_grid = mask.reshape(x.shape)
plt.imshow(mask_grid, origin ='lower')

# <codecell>

hind_avg = ma.squeeze(ma.masked_array(avg.variables['temp_latlon'][:])[0,0])
hind_avg.shape

# <codecell>

plt.imshow(hind_avg, origin = 'lower')

# <codecell>

x = [50, 100, 120]
y = [50, 100, 25]

coordlist=np.vstack((x,y)).T
print coordlist

# <codecell>

polypath = Path(coordlist)
mask = polypath.contains_points(np.array(hind_avg), radius=0.0).reshape(x.shape)

# <codecell>

f, ax = plt.subplots(1,1)
extent=[-0.5,250,0,161]
ax.imshow(np.array(hind_avg), extent=extent, interpolation='none', origin='lower')
ax.imshow(mask, interpolation='none', extent=extent, origin='lower', alpha=.5, cmap='gray')
patch = PathPatch(polypath, facecolor='g', alpha=.5)
ax.add_patch(patch)
plt.show()

# <codecell>


