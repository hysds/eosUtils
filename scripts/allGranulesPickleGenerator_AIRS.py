#-----------------------------------------------------------------------------
# Name:        orbitTableGenerator_AIRS.py
# Purpose:     Generate orbit table pickle.
#
# Author:      Gerald Manipon
#
# Created:     Fri Apr 14 10:12:36 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, datetime, re, cPickle, gzip, time, csv, glob
from cartography.geometry import Geometry, Point, LinearRing, Polygon
from cartography.proj.srs import SpatialReference

from jpltime import adoytoaymd

datasetName = 'AIRS'
minutesPerGranule = 6
daysPerCycle = 16

STDRET_RE = re.compile(r'L2\.RetStd\.v5.*\.hdf\.met$')
EAST_RE = re.compile(r'OBJECT\s*=\s*EASTBOUNDINGCOORDINATE.*?VALUE\s*=\s*(.*?)\n', re.S)
WEST_RE = re.compile(r'OBJECT\s*=\s*WESTBOUNDINGCOORDINATE.*?VALUE\s*=\s*(.*?)\n', re.S)
NORTH_RE = re.compile(r'OBJECT\s*=\s*NORTHBOUNDINGCOORDINATE.*?VALUE\s*=\s*(.*?)\n', re.S)
SOUTH_RE = re.compile(r'OBJECT\s*=\s*SOUTHBOUNDINGCOORDINATE.*?VALUE\s*=\s*(.*?)\n', re.S)
STARTDATE_RE = re.compile(r'OBJECT\s*=\s*RANGEBEGINNINGDATE.*?VALUE\s*=\s*"(.*?)"\n', re.S)
STARTTIME_RE = re.compile(r'OBJECT\s*=\s*RANGEBEGINNINGTIME.*?VALUE\s*=\s*"(\d{2}:\d{2}:\d{2}).*?"\n', re.S)
ENDDATE_RE = re.compile(r'OBJECT\s*=\s*RANGEENDINGDATE.*?VALUE\s*=\s*"(.*?)"\n', re.S)
ENDTIME_RE = re.compile(r'OBJECT\s*=\s*RANGEENDINGTIME.*?VALUE\s*=\s*"(\d{2}:\d{2}:\d{2}).*?"\n', re.S)
GRANULEID_RE = re.compile(r'(AIRS\.\d{4}\.\d{2}\.\d{2}\.(\d{3}))\.L2')

#initialize variables to do orbit table generation
count = 0
currentTime = None
timeIncr = datetime.timedelta(minutes=minutesPerGranule)
granulesPerDay = 86400/(minutesPerGranule*60)
granulesPerCycle = granulesPerDay*daysPerCycle
table = []
doneFlag = False
currentPickleYear = None

rootDataDir = os.path.abspath('./airs/v5')
yearDirs = os.listdir(rootDataDir)
yearDirs.sort()
yearDirs = [os.path.realpath(os.path.join(rootDataDir, i)) for i in yearDirs]
for rootDir in yearDirs:
    for root, dirs, files in os.walk(rootDir):
        dirs.sort()
        files.sort()
        for file in files:
            if STDRET_RE.search(file):
                met = os.path.join(root, file)
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
                    #print "%s:" % met, east, west, north, south, date0, date1, granuleId, granuleNum

                    #get center datetime
                    timeslop = (date1-date0)/2
                    ctrdate = date0 + timeslop
                    if currentTime is None:
                        currentTime = ctrdate
                    if (currentTime-timeIncr) >= ctrdate:
                        print "Duplicate time file found: %s" % file, currentTime, timeIncr, ctrdate
                        continue

                    if currentPickleYear is None:
                        currentPickleYear = ctrdate.year
                    elif currentPickleYear != ctrdate.year:
                        timeSlop = timeIncr/2
                        tableTuple = tuple(table)
                        p = cPickle.dump((minutesPerGranule, daysPerCycle, granulesPerDay,
                                        granulesPerCycle, timeSlop, tableTuple),
                                        open('%sOrbitTable_%04d.pkl' % (datasetName,
                                                                        currentPickleYear), 'w'))
                        table = []
                        currentPickleYear = ctrdate.year
                    else: pass

                    #get bounds
                    srs = SpatialReference(epsg=4326)
                    shell = LinearRing([Point(west, south),
                                        Point(west, north),
                                        Point(east, north),
                                        Point(east, south),
                                        Point(west, south)], srs=srs)
                    poly = Polygon(shell, srs=srs)
                    minx, miny, maxx, maxy = poly.envelope().totuple()
                    if abs(minx-maxx) >= 180.: p = (maxx, miny, minx, maxy)
                    else: p = (minx, miny, maxx, maxy)

                    timeDiff = currentTime - ctrdate
                    while currentTime != ctrdate and (timeDiff.days*86400+timeDiff.seconds) <= -(timeIncr.seconds-10):
                        print "Missing currentTime", currentTime, ctrdate
                        table.append(None)
                        currentTime += timeIncr
                        count += 1
                        timeDiff = currentTime - ctrdate
                    print met, ctrdate, currentTime
            
                    #append
                    table.append((p,ctrdate,granuleNum))
            
                    currentTime = ctrdate + timeIncr
                    count += 1

                else:
                    print "No met file for %s." % file
                    continue

#write final file
timeSlop = timeIncr/2
tableTuple = tuple(table)
p = cPickle.dump((minutesPerGranule, daysPerCycle, granulesPerDay,
                  granulesPerCycle, timeSlop, tableTuple),
                 open('%sOrbitTable_%04d.pkl' % (datasetName,
                                                 currentPickleYear), 'w'))
