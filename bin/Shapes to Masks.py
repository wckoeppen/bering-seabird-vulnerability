# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#A list of imports we need for code later in the notebook.
#The css_styles() function must go last.
%matplotlib inline
from owslib.wfs import WebFeatureService
import json
from utilities import find_dict_keys
import fiona
from shapely.geometry import shape, MultiPolygon
from shapely.geometry import box

import folium
from utilities import get_coords
from IPython.core.display import HTML

import time
import numpy as np
from numpy import ma
import netCDF4
import pandas as pd
from pandas import Series

import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib import ticker

from utilities import css_styles
css_styles()

# <codecell>

#Load our important bird areas again.
known_wfs = "http://solo.axiomalaska.com/geoserver/audubon_ibav3/ows"
wfs = WebFeatureService(known_wfs, version='1.0.0')
geojson_response = wfs.getfeature(typename=['audubon_ibav3:audubon_ibas_v3_20aug2014'], outputFormat="application/json", srsname="urn:x-ogc:def:crs:EPSG:4326").read()
geojson = json.loads(geojson_response)

# <codecell>

lmes= MultiPolygon([shape(pol['geometry'])
            for pol in fiona.open('/home/will/Projects/bering-seabird-vulnerability/resources/MEOW_LME_Poly.shp')])

# <codecell>

#The original metadata was not very good, and not all fields were filled in (e.g., units),
#so we have to correct these. This is our known metadata for the outputs:
metadata = pd.DataFrame({
         'orgName': [
                   #these don't have depth
                   'icephl_latlon','ben_latlon',
                   'aice_latlon',
                   #these do
                 'phs_latlon','phl_latlon','mzl_latlon','cop_latlon','ncao_latlon','ncas_latlon','eup_latlon','det_latlon',
                 'temp_latlon',
                 'u_latlon',
                 'v_latlon',],
         'name': ['Ice Phytoplankton Concentration',
                  'Benthos Concentration',
                  'Sea Ice Area Fraction',
                  'Small Phytoplankton Concentration',
                  'Large Phytoplankton Concentration',
                  'Large Microzooplankton Concentration',
                  'Small Coastal Copepod Concentration',
                  'Offshore Neocalanus Concentration',
                  'Neocalanus Concentration',
                  'Euphausiids Concentration',
                  'Detritus Concentration',
                  'Sea Water Temperature',
                  'Zonal (U) Current',
                  'Meridional (V) Current'],
         'units': ['mgC/m2','mgC/m2',
                   'Fraction',
                   'mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3',
                   'degrees C',
                   'm/s',
                   'm/s']
       })

# <codecell>

#Hindcast
#These are the H1/H2 stats of the CCCma model
#NOTEs:
#(1) in the respository, these files are gzipped and must be gunzipped before this cell will work,
#(2) change the filenames to match your system
#(3) you need the full path, ipython doesn't seem to understand ~/.
avg =     netCDF4.Dataset('/home/will/Projects/bering-seabird-vulnerability/resources/cccma_h1_average.nc')
stddev =  netCDF4.Dataset('/home/will/Projects/bering-seabird-vulnerability/resources/cccma_h1_rmssdn.nc')
pavg =    netCDF4.Dataset('/home/will/Projects/bering-seabird-vulnerability/resources/cccma_h2_average.nc')
pstddev = netCDF4.Dataset('/home/will/Projects/bering-seabird-vulnerability/resources/cccma_h2_rmssdn.nc')

#These were the previous stats
#avg = netCDF4.Dataset('~/Projects/bering-seabird-vulnerability/Resources/core_average.nc')
#stddev = netCDF4.Dataset('~/Projects/bering-seabird-vulnerability/Resources/core_rmssdn.nc')
#pavg = netCDF4.Dataset('~/Projects/bering-seabird-vulnerability/Resources/cccma_average.nc')
#pstddev = netCDF4.Dataset('~/Projects/bering-seabird-vulnerability/Resources/cccma_rmssdn.nc')

#Get a mask from the first variable
sample = ma.masked_array(avg.variables[metadata.orgName[0]][:])
mask=ma.getmask(sample)

# <codecell>

hind_avg = ma.squeeze(ma.masked_array(avg.variables['temp_latlon'][:])[0,0])

# <codecell>

hind_avg.shape

# <codecell>

plt.imshow(hind_avg)

# <codecell>

# Load latitude and longitude arrays
latitude = np.array(avg.variables['LATITUDE'])
longitude = np.array(avg.variables['LONGITUDE'])

# <codecell>

import operator
from osgeo import gdal, gdalnumeric, ogr, osr
import Image, ImageDraw
import os

# <codecell>

def imageToArray(i):
    """
    Converts a Python Imaging Library array to a 
    gdalnumeric image.
    """
    a=gdalnumeric.fromstring(i.tostring(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    """
    Converts a gdalnumeric array to a 
    Python Imaging Library Image.
    """
    i=Image.fromstring('L',(a.shape[1],a.shape[0]),
            (a.astype('b')).tostring())
    return i
     
def world2Pixel(geoMatrix, x, y):
  """
  Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
  the pixel location of a geospatial coordinate 
  """
  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = int((x - ulX) / xDist)
  line = int((ulY - y) / yDist)
  return (pixel, line) 

# <codecell>

shapef=ogr.Open("/home/will/Projects/bering-seabird-vulnerability/resources/MEOW_LME_Poly.shp")

lyr=shapef.GetLayer()
layerDefinition = lyr.GetLayerDefn()

print "Features:", lyr.GetFeatureCount()

print "Fields:"
for i in range(layerDefinition.GetFieldCount()):
    print "  ", layerDefinition.GetFieldDefn(i).GetName()

# <codecell>

for feature in lyr:
    print feature.GetField("REALM")

# <codecell>

for feature in lyr:
    geom = feature.GetGeometryRef()
    print geom.Centroid().ExportToWkt()

# <codecell>

poly = lyr.GetNextFeature()

# <codecell>

print poly

# <codecell>

mapper = folium.Map(location=[65.1, -150.6], zoom_start=3)
#Mapy polygons in red
for s in lmes:
    for c in get_coords(s):
        mapper.line(c, line_color='#FF0000', line_weight=3)

mapper.lat_lng_popover()
mapper._build_map()
HTML('<iframe srcdoc="{srcdoc}" style="width:100%; height: 535px; border: none"></iframe>'.format(srcdoc=mapper.HTML.replace('"', '&quot;')))

# <codecell>

print lmes

# <codecell>

|

