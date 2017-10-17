#-----------------------------------------------------------------------------
# Name:        orbitTableGenerator.py
# Purpose:     Generate orbit table pickle.
#
# Author:      Gerald Manipon
#
# Created:     Fri Apr 14 10:12:36 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, datetime, time, csv, glob, re
import MySQLdb as db

DUPLICATE_ENTRY_RE = re.compile(r'Duplicate entry')

CREATE_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS %s (
        id INTEGER NOT NULL AUTO_INCREMENT,
        objectid VARCHAR(128) NOT NULL,
        starttime DATETIME NOT NULL,
        endtime DATETIME NOT NULL,
        min_lat REAL NOT NULL,
        max_lat REAL NOT NULL,
        min_lon REAL NOT NULL,
        max_lon REAL NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (objectid),
        KEY starttime (starttime),
        KEY endtime (endtime),
        KEY starttime_endtime (starttime, endtime),
        KEY min_lat_index (min_lat),
        KEY max_lat_index (max_lat),
        KEY min_lon_index (min_lon),
        KEY max_lon_index (max_lon)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;'''

INSERT_SQL_TMPL = '''INSERT INTO %s (objectid, starttime, endtime, min_lat, max_lat, min_lon, max_lon)
VALUES
('%s', '%s', '%s', '%s', '%s', '%s', '%s');'''

TRIGGER = 1000

datasetName = sys.argv[1]
if datasetName == 'MODIS-Terra': geolocName = 'TERRA'
elif datasetName == 'MODIS-Aqua': geolocName = 'AQUA'
else: raise RuntimeError, "Unknown dataset %s." % datasetName

#get geoMeta with:
#$ wget --mirror -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/AQUA or
#$ wget --mirror -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/TERRA

conn = db.connect(host="127.0.0.1", port=3306, user="root", passwd="sciflo", db="test_nospatial")
cursor = conn.cursor()
cursor.execute(CREATE_TABLE_SQL % geolocName)
#cursor.fetchall()

#set dataset attributes
metaDir = os.path.join('ladsweb.nascom.nasa.gov', 'geoMeta', geolocName)
metaFiles = glob.glob(os.path.join(metaDir, '????', 'M?D03_????-??-??.txt'))
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
    r = csv.reader(open(metaFile, "rb"))
    for i, row in enumerate(r):
        if row[0].startswith('#'): continue
        
        (GranuleID, StartDateTime, ArchiveSet, OrbitNumber, DayNightFlag, EastBoundingCoord,
         NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord, GRingLongitude1,
         GRingLongitude2, GRingLongitude3, GRingLongitude4, GRingLatitude1, GRingLatitude2,
         GRingLatitude3, GRingLatitude4) = row
        file = GranuleID
        date0 = datetime.datetime(*time.strptime(StartDateTime, '%Y-%m-%d %H:%M')[:-3])
        date1 = date0 + datetime.timedelta(minutes=minutesPerGranule)
        try:
            cursor.execute(INSERT_SQL_TMPL % (geolocName, GranuleID, str(date0), str(date1), 
                                              SouthBoundingCoord, NorthBoundingCoord,
                                              WestBoundingCoord, EastBoundingCoord))
        except Exception, e:
            if DUPLICATE_ENTRY_RE.search(str(e)): pass
            else: raise

        count+= 1
        if count >= TRIGGER:
            conn.commit()
            count = 0

conn.commit()
conn.close()
