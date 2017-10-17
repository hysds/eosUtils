#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        updateSqlite_AIRS.py
# Purpose:     Update sqlite metadata db for AIRS.
#
# Author:      Gerald Manipon
#
# Created:     Tue Jan 31 10:12:36 2011
# Copyright:   (c) 2011, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, datetime, time, csv, glob, re
import sqlite3

from sciflo.utils import runXpath, getXmlEtree

STDRET_RE = re.compile(r'L2\.RetStd\.v6.*\.hdf\.xml$')
EAST_XP = './/EastBoundingCoordinate/text()'
WEST_XP = './/WestBoundingCoordinate/text()'
NORTH_XP = './/NorthBoundingCoordinate/text()'
SOUTH_XP = './/SouthBoundingCoordinate/text()'
STARTDATE_XP = './RangeDateTime/RangeBeginningDate/text()'
STARTTIME_XP = './RangeDateTime/RangeBeginningTime/text()'
ENDDATE_XP = './RangeDateTime/RangeEndingDate/text()'
ENDTIME_XP = './RangeDateTime/RangeEndingTime/text()'
GRANULEID_RE = re.compile(r'(AIRS\.\d{4}\.\d{2}\.\d{2}\.(\d{3}))\.L2')

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

datasetName = 'AIRS'
geolocName = 'AIRS'

TRIGGER = 1000

dbFile = os.path.abspath(sys.argv[1])
rootDataDir = os.path.abspath(sys.argv[2])
conn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(CREATE_TABLE_SQL % geolocName)
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

count = 0
for root, dirs, files in os.walk(rootDataDir):
    dirs.sort()
    files.sort()
    for file in files:
        if STDRET_RE.search(file):
            #get space and time info
            try:
                file = os.path.join(root, file)
                et, nsDict = getXmlEtree(file)
                east = eval(runXpath(et, EAST_XP, nsDict))
                west = eval(runXpath(et, WEST_XP, nsDict))
                north = eval(runXpath(et, NORTH_XP, nsDict))
                south = eval(runXpath(et, SOUTH_XP, nsDict))
                startDate = runXpath(et, STARTDATE_XP, nsDict)
                startTime = runXpath(et, STARTTIME_XP, nsDict)
                date0 = datetime.datetime(*time.strptime("%s %s" % (startDate, startTime.split('.')[0]),
                                          '%Y-%m-%d %H:%M:%S')[:-3])
                endDate = runXpath(et, ENDDATE_XP, nsDict)
                endTime = runXpath(et, ENDTIME_XP, nsDict)
                date1 = datetime.datetime(*time.strptime("%s %s" % (endDate, endTime.split('.')[0]),
                                          '%Y-%m-%d %H:%M:%S')[:-3])
                granuleIdMatch = GRANULEID_RE.search(file)
                if granuleIdMatch:
                    granuleId = granuleIdMatch.group(1)
                    granuleNum = int(granuleIdMatch.group(2))
                else: raise RuntimeError("no granuleid found")
                #print "%s:" % file, east, west, north, south, date0, date1, granuleId, granuleNum

                cursor.execute(INSERT_SQL_TMPL % geolocName, (granuleId, date0, date1,
                               south, north, west, east))

                count+= 1
                if count >= TRIGGER:
                    conn.commit()
                    count = 0
            except Exception, e:
                print "Got exception for file %s: %s" % (file, str(e))

conn.commit()
conn.close() 
