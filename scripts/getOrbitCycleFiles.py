#-----------------------------------------------------------------------------
# Name:        getOrbitCycleFiles.py
# Purpose:     Get orbit cycle files.
#
# Author:      Gerald Manipon
#
# Created:     Fri Apr 14 10:12:36 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, re, glob
from string import Template

from eosUtils.granule2 import getOrbitCycleIds

dataDir = '/data/df3/modis/orbitTable'
if not os.path.isdir(dataDir): os.makedirs(dataDir)

objectids = getOrbitCycleIds('MODIS-Terra_2000')

urlTpl = Template('ftp://ladsweb.nascom.nasa.gov/allData/5/MOD03/$year/$doy/MOD03.A${year}${doy}.${hour}${minute}.005.*.hdf')
wgetTpl = Template('wget --retr-symlinks -P $dataDir $url')

for objectid in objectids:
    #generate url and local file glob.
    match = re.search(r'^MOD\*\.A(\d{4})(\d{3})\.(\d{2})(\d{2})$', objectid)
    if not match: raise RuntimeError, "Couldn't extract date elements."
    year, doy, hour, minute = match.groups()
    url = urlTpl.substitute(year=year, doy=doy, hour=hour, minute=minute)
    fileGlob = os.path.join(dataDir, os.path.basename(url))
    localFiles = glob.glob(fileGlob)
    
    #if local files found, skip.  otherwise download.
    if len(localFiles) == 0:
        wgetCmd = wgetTpl.substitute(dataDir=dataDir, url=url)
        os.system(wgetCmd)
    elif len(localFiles) == 1:
        print "Local file already here: %s" % localFiles[0]
    else: raise RuntimeError, "Too many files found: %s" % localFiles