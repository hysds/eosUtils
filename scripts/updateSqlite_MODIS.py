#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        updateSqlite_MODIS.py
# Purpose:     Update MODIS-Terra/Aqua metadata db.
#
# Author:      Gerald Manipon
#
# Created:     Tue Jan 14 10:12:36 2011
# Copyright:   (c) 2011, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, datetime, time, csv, glob, re
import sqlite3

from sciflo.data.localize import localizeUrl

META_RE = re.compile(r'M.D03_\d{4}-\d{2}-\d{2}\.txt')
DUPLICATE_ENTRY_RE = re.compile(r'Duplicate entry')

CREATE_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS %s (
        objectid text not null primary key,
        starttime date not null,
        endtime date not null,
        min_lat real not null,
        max_lat real not null,
        min_lon real not null,
        max_lon real not null
)'''

INSERT_SQL_TMPL = '''INSERT OR IGNORE INTO %s (objectid, starttime, endtime, 
min_lat, max_lat, min_lon, max_lon)
VALUES
(?, ?, ?, ?, ?, ?, ?);'''

datasetName = os.path.abspath(sys.argv[1])
dbFile = os.path.abspath(sys.argv[2])
metaDir = os.path.abspath(sys.argv[3])
if datasetName == 'MODIS-Terra': geolocName = 'TERRA'
elif datasetName == 'MODIS-Aqua': geolocName = 'AQUA'
else: raise RuntimeError, "Unknown dataset %s." % datasetName

TRIGGER = 1000

#get geoMeta with:
#$ wget --mirror -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/AQUA or
#$ wget --mirror -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/TERRA

conn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(CREATE_TABLE_SQL % geolocName)
#cursor.fetchall()

#set dataset attributes
metaFiles = []
for root, dirs, files in os.walk(metaDir):
    dirs.sort()
    files.sort()
    if META_RE.search(file): metaFiles.append(os.path.join(root, file))
metaFiles.sort()
minutesPerGranule = 5
daysPerCycle = 16

#initialize variables to do orbit table generation
count = 0
currentTime = None
timeIncr = datetime.timedelta(minutes=minutesPerGranule)
granulesPerDay = 86400/(minutesPerGranule*60)
granulesPerCycle = granulesPerDay*daysPerCycle
table = []
doneFlag = False
currentPickleYear = None
for metaFile in metaFiles:
    tries = 0
    while True:
        print "Doing %s" % metaFile
        r = csv.reader(open(metaFile, "rb"))
        try:
            for i, row in enumerate(r):
                if row[0].startswith('#'): continue
                
                try:
                    (GranuleID, StartDateTime, ArchiveSet, OrbitNumber, DayNightFlag, EastBoundingCoord,
                     NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord, GRingLongitude1,
                     GRingLongitude2, GRingLongitude3, GRingLongitude4, GRingLatitude1, GRingLatitude2,
                     GRingLatitude3, GRingLatitude4) = row
                except Exception, e:
                    raise RuntimeError("Failed to parse fields from row %d in file %s: %s" % (i, metaFile, row))
                file = GranuleID
                date0 = datetime.datetime(*time.strptime(StartDateTime, '%Y-%m-%d %H:%M')[:-3])
                date1 = date0 + datetime.timedelta(minutes=minutesPerGranule)
                cursor.execute(INSERT_SQL_TMPL % geolocName, (GranuleID, date0, date1,
                                                              SouthBoundingCoord,
                                                              NorthBoundingCoord,
                                                              WestBoundingCoord,
                                                              EastBoundingCoord))
        
                count+= 1
                if count >= TRIGGER:
                    conn.commit()
                    count = 0
            break
        except Exception, e:
            if 'line contains NULL byte' in str(e): break
            tries += 1
            if tries == 3: raise
            print "Bad meta file: %s. Removing and downloading again." % metaFile
            dlTries = 0
            while True:
                if os.path.exists(metaFile): os.unlink(metaFile)
                time.sleep(3)
                try:
                    localizeUrl('ftp://' + metaFile, os.path.dirname(metaFile))
                    break
                except Exception, e:
                    dlTries += 1
                    if dlTries == 3: raise
    
conn.commit()
conn.close()
