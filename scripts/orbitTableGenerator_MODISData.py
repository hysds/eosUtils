#-----------------------------------------------------------------------------
# Name:        orbitTableGenerator_MODISData.py
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

datasetName = sys.argv[1]
if datasetName == 'MODIS-Terra': geolocName = 'TERRA'
elif datasetName == 'MODIS-Aqua': geolocName = 'AQUA'
else: raise RuntimeError, "Unknown dataset %s." % datasetName

#set dataset attributes
metaDir = os.path.join('ladsweb.nascom.nasa.gov', 'geoMeta', geolocName)
metaFiles = glob.glob(os.path.join(metaDir, '????', 'M?D03_????-??-??.txt'))
metaFiles.sort()
minutesPerGranule = 5
daysPerCycle = 16

#initialize variables to do orbit table generation
count = 0
periodCount = 0
currentTime = None
timeIncr = datetime.timedelta(minutes=minutesPerGranule)
granulesPerDay = 86400/(minutesPerGranule*60)
granulesPerCycle = granulesPerDay*daysPerCycle
table = []
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
        EastBoundingCoord = float(EastBoundingCoord)
        NorthBoundingCoord = float(NorthBoundingCoord)
        SouthBoundingCoord = float(SouthBoundingCoord)
        WestBoundingCoord = float(WestBoundingCoord)
        GRingLongitude1 = float(GRingLongitude1)
        GRingLongitude2 = float(GRingLongitude2)
        GRingLongitude3 = float(GRingLongitude3)
        GRingLongitude4 = float(GRingLongitude4)
        GRingLatitude1 = float(GRingLatitude1)
        GRingLatitude2 = float(GRingLatitude2)
        GRingLatitude3 = float(GRingLatitude3)
        GRingLatitude4 = float(GRingLatitude4)
        
        #get center datetime
        timeslop = (date1-date0)/2
        ctrdate = date0 + timeslop
        if currentTime is None:
            currentTime = ctrdate
        if (currentTime-timeIncr) == ctrdate:
            print "Duplicate time file found: %s" % file
            continue
        
        #get orbit
        orbit = int(OrbitNumber)
        
        #granule num
        granuleNum=0
        
        #get bounds
        srs = SpatialReference(epsg=4326)
        shell = LinearRing([Point(GRingLongitude1, GRingLatitude1),
                            Point(GRingLongitude2, GRingLatitude2),
                            Point(GRingLongitude3, GRingLatitude3),
                            Point(GRingLongitude4, GRingLatitude4),
                            Point(GRingLongitude1, GRingLatitude1)], srs=srs)
        poly = Polygon(shell, srs=srs)
        minx, miny, maxx, maxy = poly.envelope().totuple()
        if abs(minx-maxx) >= 180.: p = (maxx, miny, minx, maxy)
        else: p = (minx, miny, maxx, maxy)
    
        #print currentTime, ctrdate, periodCount, granulesPerCycle
        while (periodCount%granulesPerCycle)<granulesPerCycle and currentTime!=ctrdate:
            print "Missing currentTime", currentTime
            if periodCount<granulesPerCycle: table.append(None)
            currentTime+=timeIncr
            periodCount+=1
        
        if periodCount<granulesPerCycle:
            table.append((p,ctrdate,granuleNum))
            print file, ctrdate, timeslop, '--.--', orbit, granuleNum, count, periodCount
        else:
            perIdx=periodCount%granulesPerCycle
            if table[perIdx] is None:
                table[perIdx]=(p,ctrdate,granuleNum)
            else:
                pxmin, pymin, pxmax, pymax=p
                pshell = LinearRing([Point(pxmin, pymin),
                    Point(pxmin, pymax),
                    Point(pxmax, pymax),
                    Point(pxmax, pymin),
                    Point(pxmin, pymin)], srs=srs)
                pPoly=Polygon(pshell, srs=srs)
                txmin, tymin, txmax, tymax=table[perIdx][0]
                tshell = LinearRing([Point(txmin, tymin),
                    Point(txmin, tymax),
                    Point(txmax, tymax),
                    Point(txmax, tymin),
                    Point(txmin, tymin)], srs=srs)
                tPoly=Polygon(tshell, srs=srs)
                #print pPoly.area(), p
                #print tPoly.area(), table[perIdx][0]
                overlap=tPoly.intersection(pPoly)
                perc=(100.0*(overlap.area()/tPoly.area()))
                if perc>100.0:
                    table[perIdx]=(p,ctrdate,granuleNum)
                    print "Replacing table element perIdx %s." % perIdx
                    print file, ctrdate, timeslop, '--.--', orbit, granuleNum, count, periodCount
                else:
                    percStr="%04.2f" % perc
                    print file, ctrdate, timeslop, percStr, orbit, granuleNum, count, periodCount
                    #if perc>=90.: print file, ctrdate, timeslop, percStr, orbit, granuleNum, count, periodCount
        #sys.exit()
        count+=1
        currentTime+=timeIncr
        periodCount+=1

if None in table:
    print "Table was not filled."
    print len(table)
    print table.index(None)
    raise SystemExit
else:
    print "Writing out table."
    timeSlop=timeIncr/2
    tableTuple=tuple(table)
    p=cPickle.dump((minutesPerGranule,daysPerCycle,granulesPerDay,
                    granulesPerCycle,timeSlop,tableTuple),
        open('%sOrbitTable.pkl' % datasetName,'w'))
    #getFlashMovie(pngFiles, os.path.join(imageDir, 'movie.swf'))

    

