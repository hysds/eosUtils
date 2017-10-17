import os, sys, csv, datetime, time, glob
import Polygon as P
import cPickle as pickle
from pyhdf.SD import *
from cartography.geometry import Geometry, Point, LinearRing, Polygon
from cartography.proj.srs import SpatialReference
from matplotlib.transforms import Bbox, Value
from matplotlib.transforms import Point as Point2

geolocName = 'TERRA'
metaDir = os.path.join('ladsweb.nascom.nasa.gov', 'geoMeta', geolocName)
metaFiles = glob.glob(os.path.join(metaDir, '????', 'M?D03_????-??-??.txt'))
metaFiles.sort()

dataDir = '/data/df3/modis/orbitTable'

for metaFile in metaFiles:
    r = csv.reader(open(metaFile, "rb"))
    for i, row in enumerate(r):
        if row[0].startswith('#'): continue
        (GranuleID, StartDateTime, ArchiveSet, OrbitNumber, DayNightFlag, EastBoundingCoord,
         NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord, GRingLongitude1,
         GRingLongitude2, GRingLongitude3, GRingLongitude4, GRingLatitude1, GRingLatitude2,
         GRingLatitude3, GRingLatitude4) = row
        file = GranuleID
        dt = datetime.datetime(*time.strptime(StartDateTime, '%Y-%m-%d %H:%M')[:-2])
        GRingLongitude1 = float(GRingLongitude1)
        GRingLongitude2 = float(GRingLongitude2)
        GRingLongitude3 = float(GRingLongitude3)
        GRingLongitude4 = float(GRingLongitude4)
        GRingLatitude1 = float(GRingLatitude1)
        GRingLatitude2 = float(GRingLatitude2)
        GRingLatitude3 = float(GRingLatitude3)
        GRingLatitude4 = float(GRingLatitude4)
        if GranuleID == 'MOD03.A2000278.0015.005.2008197025710.hdf':
            print "#" * 80
            print GranuleID
            #polygon = P.Polygon(((GRingLongitude1, GRingLatitude1),
            #                     (GRingLongitude2, GRingLatitude2),
            #                     (GRingLongitude3, GRingLatitude3),
            #                     (GRingLongitude4, GRingLatitude4)))
            #print "polygon.boundingBox():", polygon.boundingBox()
            #p2 = P.Polygon(((-1., 40.), (-1., 45.), (1., 45.), (1., 40.)))
            #print "overlaps:", p2.overlaps(polygon)
            t1 = time.time()
            srs = SpatialReference(epsg=4326)
            print "GR:", GRingLongitude1, GRingLatitude1, GRingLongitude2, \
            GRingLatitude2, GRingLongitude3, GRingLatitude3, GRingLongitude4, GRingLatitude4, GRingLongitude1, GRingLatitude1
            shell = LinearRing([Point(GRingLongitude1, GRingLatitude1),
                                Point(GRingLongitude2, GRingLatitude2),
                                Point(GRingLongitude3, GRingLatitude3),
                                Point(GRingLongitude4, GRingLatitude4),
                                Point(GRingLongitude1, GRingLatitude1)], srs=srs)
            poly = Polygon(shell, srs=srs)
            print "polyEnvelope:", poly.envelope()
            p3 = Polygon(LinearRing([Point(-1., 40.),
                                     Point(-1., 45.),
                                     Point(1., 45.),
                                     Point(1., 40.),
                                     Point(-1., 40.)], srs=srs), srs=srs)
            print "poly.boundary():", poly.boundary()
            print "intersects:", p3.intersects(poly)
            print "p3Envelope:", p3.envelope()
            t2 = time.time()
            print "cartography took %f seconds." % (t2-t1)
            t3 = time.time()
            print EastBoundingCoord, NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord
            bbox = Bbox(Point2(Value(WestBoundingCoord), Value(SouthBoundingCoord)),
                Point2(Value(EastBoundingCoord), Value(NorthBoundingCoord)))
            bbox2 = Bbox(Point2(Value(-1.), Value(40.)), Point2(Value(1.), Value(45.)))
            print "bbox overlaps:", bbox.overlaps(bbox2)
            t4 = time.time()
            print "matplotlib Bbox took %f seconds." % (t4-t3)
            raise SystemExit, "Done."
        '''
        dataFile = os.path.join(dataDir, file)
        if os.path.isfile(dataFile):
            try: sd = SD(dataFile)
            except:
                print "Failed on dataFile: %s" % dataFile
                raise
            latData = sd.select('Latitude')[:]
            lonData = sd.select('Longitude')[:]
            corner1 = (lonData[0,0], latData[0,0])
            corner2 = (lonData[0,-1], latData[0,-1])
            corner3 = (lonData[-1,-1], latData[-1,-1])
            corner4 = (lonData[-1,0], latData[-1,0])
            polygonPoints = [corner1, corner2, corner3, corner4]
            print "#" * 80
            print "dataFile:", dataFile
            print (file, dt, polygon, GRingLongitude1, GRingLongitude2, GRingLongitude3,
                   GRingLongitude4, GRingLatitude1, GRingLatitude2, GRingLatitude3,
                   GRingLatitude4)
            print "polygon.boundingBox():", polygon.boundingBox()
            print "bounding box from data:", Polygon.Polygon(polygonPoints).boundingBox()
            print EastBoundingCoord, NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord
        '''
