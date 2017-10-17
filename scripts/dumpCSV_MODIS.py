import os, sys, datetime, re, cPickle, gzip, time, csv, glob
from cartography.geometry import Geometry, Point, LinearRing, Polygon
from cartography.proj.srs import SpatialReference

from jpltime import adoytoaymd

GRANULE_RE = re.compile(r'^(M(?:Y|O)D).*?\.(A\d{7}\.\d{4})')

CSV_LINE = "%s,%f,%f,%f,%f,%s,%s"

dataDirs = ['TERRA', 'AQUA']
datasetName = 'MODIS'
minutesPerGranule = 5
daysPerCycle = 16

#get data files
metaFiles = []
for dataDir in dataDirs:
    metaDir = os.path.join('ladsweb.nascom.nasa.gov', 'geoMeta',
                           dataDir)
    metaFiles.extend(glob.glob(os.path.join(metaDir, '????',
                                            'M?D03_????-??-??.txt')))
metaFiles.sort()

#initialize variables to do orbit table generation
count = 0
currentTime = None
timeIncr = datetime.timedelta(minutes=minutesPerGranule)
granulesPerDay = 86400/(minutesPerGranule*60)
granulesPerCycle = granulesPerDay*daysPerCycle
table = []
doneFlag = False
currentPickleYear = None

print "id,latMin,latMax,lonMin,lonMax,startDate,endDate"

for metaFile in metaFiles:
    r = csv.reader(open(metaFile, "rb"))
    for i, row in enumerate(r):
        if row[0].startswith('#'): continue
            
        (GranuleID, StartDateTime, ArchiveSet, OrbitNumber, DayNightFlag, EastBoundingCoord,
         NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord, GRingLongitude1,
         GRingLongitude2, GRingLongitude3, GRingLongitude4, GRingLatitude1, GRingLatitude2,
         GRingLatitude3, GRingLatitude4) = row
        granuleIdMatch = GRANULE_RE.search(GranuleID)
        if not granuleIdMatch: raise RuntimeError("Failed to match %s" % GranuleID)
        granuleId = "%s*.%s" % granuleIdMatch.groups()
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
    
        print CSV_LINE % (granuleId, p[1], p[3], p[0], p[2], 
            date0.isoformat()+'Z', date1.isoformat()+'Z')
