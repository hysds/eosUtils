#!/usr/bin/env python
import os, sys, time
from datetime import datetime
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from pprint import pprint, pformat


from wvcc.cloudsat.GeoProf import GeoProf


file = '2012076091048_31299_CS_2B-GEOPROF_GRANULE_P_R04_E05.hdf'
g = GeoProf(file)
g.simplify()
west, south, east, north = g.getBbox()
linestrings = g.getLineStrings()
line_type = g.getLineType()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.scatter(g.geoDict['Longitude'], g.geoDict['Latitude'], s=1)
ax.plot([i[0] for i in linestrings[0]], [i[1] for i in linestrings[0]])
ax.plot([west, east, east, west, west], [north, north, south, south, north])

#get times for first and last pixel; get corresponding dates with 1 day slop
ti = g.geoDict['Profile_UTC'][0]
ti_elts = time.gmtime(ti)
print ti_elts
tiDt = datetime(*ti_elts[0:6])
tf = g.geoDict['Profile_UTC'][-1]
tf_elts = time.gmtime(tf)
print tf_elts
tfDt = datetime(*tf_elts[0:6])
print tiDt, tfDt

plt.show()
#plt.plot(zip(g.geoDict['Longitude'][:], g.geoDict['Latitude'][:]), marker='.')
#plt.show()
#pprint(zip(g.geoDict['Longitude'][:], g.geoDict['Latitude'][:]))
