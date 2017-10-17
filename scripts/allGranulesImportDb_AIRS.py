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
from cartography.geometry import Geometry, Point, LinearRing, Polygon
from cartography.proj.srs import SpatialReference
import MySQLdb as db

STDRET_RE = re.compile(r'L2\.RetStd\.v5.*\.hdf$')
EAST_RE = re.compile(r'OBJECT = EASTBOUNDINGCOORDINATE.*?VALUE = (.*?)\n', re.S)
WEST_RE = re.compile(r'OBJECT = WESTBOUNDINGCOORDINATE.*?VALUE = (.*?)\n', re.S)
NORTH_RE = re.compile(r'OBJECT = NORTHBOUNDINGCOORDINATE.*?VALUE = (.*?)\n', re.S)
SOUTH_RE = re.compile(r'OBJECT = SOUTHBOUNDINGCOORDINATE.*?VALUE = (.*?)\n', re.S)
STARTDATE_RE = re.compile(r'OBJECT = RANGEBEGINNINGDATE.*?VALUE = "(.*?)"\n', re.S)
STARTTIME_RE = re.compile(r'OBJECT = RANGEBEGINNINGTIME.*?VALUE = "(\d{2}:\d{2}:\d{2}).*?"\n', re.S)
ENDDATE_RE = re.compile(r'OBJECT = RANGEENDINGDATE.*?VALUE = "(.*?)"\n', re.S)
ENDTIME_RE = re.compile(r'OBJECT = RANGEENDINGTIME.*?VALUE = "(\d{2}:\d{2}:\d{2}).*?"\n', re.S)
GRANULEID_RE = re.compile(r'(AIRS\.\d{4}\.\d{2}\.\d{2}\.(\d{3}))\.L2')

DUPLICATE_ENTRY_RE = re.compile(r'Duplicate entry')

CREATE_TABLE_SQL = '''DROP TABLE IF EXISTS %s;
CREATE TABLE %s (
        id INTEGER NOT NULL AUTO_INCREMENT,
        objectid VARCHAR(128) NOT NULL,
        starttime DATETIME NOT NULL,
        endtime DATETIME NOT NULL,
        georing POLYGON NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (objectid),
        KEY starttime (starttime),
        KEY endtime (endtime),
        KEY starttime_endtime (starttime, endtime),
        SPATIAL INDEX(georing)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;'''

INSERT_SQL_TMPL = '''INSERT INTO %s (objectid, starttime, endtime, georing)
VALUES
('%s', '%s', '%s', PolygonFromText('%s', 4326));'''

TRIGGER = 1000

datasetName = 'AIRS'
geolocName = 'AIRS'

conn = db.connect(host="127.0.0.1", port=3306, user="root", passwd="sciflo", db="geoInfo")
cursor = conn.cursor()
#cursor.execute(CREATE_TABLE_SQL % (geolocName, geolocName))
#cursor.fetchall()

#set dataset attributes
minutesPerGranule = 6
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

rootDataDir = '/home/sflops/sciflo/share/sciflo/data/gdaac/v5'
yearDirs = os.listdir(rootDataDir)
yearDirs.sort()
yearDirs = [os.path.realpath(os.path.join(rootDataDir, i)) for i in yearDirs]
for rootDir in yearDirs:
    for root, dirs, files in os.walk(rootDir):
        dirs.sort()
        files.sort()
        for file in files:
            if STDRET_RE.search(file):
                file = os.path.join(root, file)
                met = file + '.met'
                if os.path.isfile(met):
                    #get space and time info
                    f = open(met, 'r'); metStr = f.read(); f.close()
                    eastMatch = EAST_RE.search(metStr)
                    if eastMatch: east = eval(eastMatch.group(1))
                    else: raise RuntimeError("no east found")
                    westMatch = WEST_RE.search(metStr)
                    if westMatch: west = eval(westMatch.group(1))
                    else: raise RuntimeError("no west found")
                    northMatch = NORTH_RE.search(metStr)
                    if northMatch: north = eval(northMatch.group(1))
                    else: raise RuntimeError("no north found")
                    southMatch = SOUTH_RE.search(metStr)
                    if southMatch: south = eval(southMatch.group(1))
                    else: raise RuntimeError("no south found")
                    startDateMatch = STARTDATE_RE.search(metStr)
                    if startDateMatch: startDate = startDateMatch.group(1)
                    else: raise RuntimeError("no startdate found")
                    startTimeMatch = STARTTIME_RE.search(metStr)
                    if startTimeMatch: startTime = startTimeMatch.group(1)
                    else: raise RuntimeError("no starttime found")
                    date0 = datetime.datetime(*time.strptime("%s %s" % (startDate, startTime),
                                              '%Y-%m-%d %H:%M:%S')[:-3])
                    endDateMatch = ENDDATE_RE.search(metStr)
                    if endDateMatch: endDate = endDateMatch.group(1)
                    else: raise RuntimeError("no enddate found")
                    endTimeMatch = ENDTIME_RE.search(metStr)
                    if endTimeMatch: endTime = endTimeMatch.group(1)
                    else: raise RuntimeError("no endtime found")
                    date1 = datetime.datetime(*time.strptime("%s %s" % (endDate, endTime),
                                              '%Y-%m-%d %H:%M:%S')[:-3])
                    granuleIdMatch = GRANULEID_RE.search(met)
                    if granuleIdMatch:
                        granuleId = granuleIdMatch.group(1)
                        granuleNum = int(granuleIdMatch.group(2))
                    else: raise RuntimeError("no granuleid found")
                    print "%s:" % met, east, west, north, south, date0, date1, granuleId, granuleNum

                    #get bounds
                    srs = SpatialReference(epsg=4326)
                    shell = LinearRing([Point(west, south),
                                        Point(west, north),
                                        Point(east, north),
                                        Point(east, south),
                                        Point(west, south)], srs=srs)
                    poly = Polygon(shell, srs=srs)
                    p = poly.toWKT()
                    try: cursor.execute(INSERT_SQL_TMPL % (geolocName, granuleId, str(date0), str(date1), p))
                    except Exception, e:
                        if DUPLICATE_ENTRY_RE.search(str(e)): pass
                        else: raise

try: cursor.execute(INSERT_SQL_TMPL % (geolocName, granuleId, str(date0), str(date1), p))
except Exception, e: print e
cursor.close()
conn.close()
