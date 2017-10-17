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
import Polygon
import hdfeos
import os
import sys
from lxml.etree import XML
import datetime
import re
import cPickle
import gzip

#set dataset attributes
if sys.argv[1]=='MODIS-Terra':
    datadir='MODISTerraMetXml'
    datasetName='MODISTerra'
    minutesPerGranule=5
    daysPerCycle=16
elif sys.argv[1]=='MODIS-Aqua':
    datadir='MODISAquaMetXml'
    datasetName='MODISAqua'
    minutesPerGranule=5
    daysPerCycle=16
elif sys.argv[1]=='AIRS':
    datadir='AIRSMetXml'
    datasetName='AIRS'
    minutesPerGranule=6
    daysPerCycle=16
else:
    raise SystemExit, "Unknown dataset: %s." % sys.argv[1]

#initialize variables to do orbit table generation
filelist=os.listdir(datadir)
filelist.sort()
count=0
periodCount=0
currentTime=None
timeIncr=datetime.timedelta(minutes=minutesPerGranule)
granulesPerDay=86400/(minutesPerGranule*60)
granulesPerCycle=granulesPerDay*daysPerCycle
table=[]
for file in filelist:
    xmlFile=os.path.join(datadir,file)
    #print xmlFile
    try:
        f=gzip.GzipFile(xmlFile)
        xmlStr=f.read()
        f.close()
        elt=XML(xmlStr)
    except:
        print "Failed on xmlFile: %s" % xmlFile
        #continue
        raise
    
    #get center datetime
    rbd=elt.xpath('.//RangeBeginningDate')[0].text
    rbt=elt.xpath('.//RangeBeginningTime')[0].text
    red=elt.xpath('.//RangeEndingDate')[0].text
    ret=elt.xpath('.//RangeEndingTime')[0].text
    (y0, m0, d0) = map(int, re.split('-', rbd))
    (y1, m1, d1) = map(int, re.split('-', red))
    (hh0, mm0, ss0) = re.split(':', rbt)
    (hh1, mm1, ss1) = re.split(':', ret)
    date0 = datetime.datetime(year=y0, month=m0, day=d0, hour=int(hh0),
                              minute=int(mm0), second=int(float(ss0)))
    date1 = datetime.datetime(year=y1, month=m1, day=d1, hour=int(hh1),
                              minute=int(mm1), second=int(float(ss1)))
    timeslop=(date1-date0)/2
    ctrdate = date0 + timeslop
    if currentTime is None:
        currentTime=ctrdate
    if (currentTime-timeIncr)==ctrdate:
        print "Duplicate time file found: %s" % file
        continue
    #print date0, date1, ctrdate
    
    #get orbit
    if datasetName=='AIRS':
        orbit=int(elt.xpath(".//PSA[PSAName='OrbitPath']/PSAValue")[0].text)
    else:
        orbit=int(elt.xpath('.//OrbitNumber')[0].text)
    
    #granule num
    if datasetName=='AIRS':
        granuleNum=int(elt.xpath(".//PSA[PSAName='AIRSGranuleNumber']/PSAValue")[0].text)
    else:
        granuleNum=int(elt.xpath(".//PSA[PSAName='GRANULENUMBER']/PSAValue")[0].text)
    
    #get bounds
    if datasetName=='AIRS':
        minLon=float(elt.xpath(".//WestBoundingCoordinate")[0].text)
        maxLon=float(elt.xpath(".//EastBoundingCoordinate")[0].text)
        minLat=float(elt.xpath(".//SouthBoundingCoordinate")[0].text)
        maxLat=float(elt.xpath(".//NorthBoundingCoordinate")[0].text)
        p=Polygon.Polygon(((minLon,minLat),(maxLon,minLat),(maxLon,maxLat),(minLon,maxLat)))
    else:
        pts=elt.xpath('.//Boundary/Point')
        polygonPoints=[]
        for pt in pts:
            ptLon=float(pt.xpath('PointLongitude')[0].text)
            ptLat=float(pt.xpath('PointLatitude')[0].text)
            polygonPoints.append((ptLon,ptLat))
        #print minLat, maxLat, minLon, maxLon
        p=Polygon.Polygon(polygonPoints)
    
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
            overlap=p & table[perIdx][0]
            perc=(100.0*(overlap.area()/table[perIdx][0].area()))
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

    

