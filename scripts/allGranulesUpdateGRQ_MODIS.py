import os, sys, datetime, time, csv, glob, re, types, json, httplib2
from urllib import urlopen
from shapely.geometry import Polygon, MultiPolygon
import shapely.wkt

import cartopy.crs as ccrs


# global http object
http = httplib2.Http()


MET_RE = re.compile(r'^M[OY]D03_\d{4}-\d{2}-\d{2}\.txt$')
GRANULEID_RE = re.compile(r'^(M[OY]D03\.A\d{7}\.\d{4}).*')

rootDataDir = os.path.abspath(sys.argv[1])

count = 0
for root, dirs, files in os.walk(rootDataDir):
    dirs.sort()
    files.sort()
    for file in files:
        if file == '.listing': continue
        print file
        if MET_RE.search(file):
            metaFile = os.path.join(root, file)
            r = csv.reader(open(metaFile, 'rb'))
            for i, row in enumerate(r):
                if row[0].startswith('#'): continue
                (GranuleID, StartDateTime, ArchiveSet, OrbitNumber, DayNightFlag, EastBoundingCoord,
                 NorthBoundingCoord, SouthBoundingCoord, WestBoundingCoord, GRingLongitude1,
                 GRingLongitude2, GRingLongitude3, GRingLongitude4, GRingLatitude1, GRingLatitude2,
                 GRingLatitude3, GRingLatitude4) = row
                east = float(EastBoundingCoord)
                west = float(WestBoundingCoord)
                south = float(SouthBoundingCoord)
                north = float(NorthBoundingCoord)
                GRingLongitude1 = float(GRingLongitude1)
                GRingLongitude2 = float(GRingLongitude2)
                GRingLongitude3 = float(GRingLongitude3)
                GRingLongitude4 = float(GRingLongitude4)
                GRingLatitude1 = float(GRingLatitude1)
                GRingLatitude2 = float(GRingLatitude2)
                GRingLatitude3 = float(GRingLatitude3)
                GRingLatitude4 = float(GRingLatitude4)
                poly = Polygon((
                    ( GRingLongitude1, GRingLatitude1 ),
                    ( GRingLongitude2, GRingLatitude2 ),
                    ( GRingLongitude3, GRingLatitude3 ),
                    ( GRingLongitude4, GRingLatitude4 ),
                ))
                src_proj = ccrs.PlateCarree()
                if west == -180. or east == 180.:
                    if south > 0: tgt_proj = ccrs.RotatedPole(0., 90.)
                    else: tgt_proj = ccrs.RotatedPole(0., -90.)
                else: tgt_proj = src_proj
                multipolygons = tgt_proj.project_geometry(poly, src_proj)
                multipolygons = multipolygons.simplify(10.)
                center_lon = multipolygons.centroid.x
                center_lat = multipolygons.centroid.y
                if isinstance(multipolygons, Polygon):
                    multipolygons = [ multipolygons ]
                polygons = []
                for p in multipolygons:
                    if not p.is_valid: p = p.buffer(0)
                    polygons.append(list(p.exterior.coords))
                poly_type = 'polygon'
                if len(polygons) > 1:
                    #print r, polygons
                    polygons = [[p] for p in polygons]
                    poly_type = 'multipolygon'
                date0 = datetime.datetime(*time.strptime(StartDateTime, '%Y-%m-%d %H:%M')[:-3])
                date1 = date0 + datetime.timedelta(minutes=5)
                granuleIdMatch = GRANULEID_RE.search(GranuleID)
                if granuleIdMatch:
                    granuleId = granuleIdMatch.group(1)
                    dataset = granuleId[0:3]
                else: raise RuntimeError("no granuleid found")
                #print "%s:" % file, east, west, north, south, date0, date1, granuleId, granuleNum

                # json
                update_json = {
                    'dataset': dataset,
                    'id': granuleId,
                    'urls': [],
                    'browse_urls': [],
                    'metadata': {
                        'data_product_name': 'MODIS',
                        'version': 6,
                        'starttime': date0.isoformat() + 'Z',
                        'endtime': date1.isoformat() + 'Z',
                        'min_lat': south,
                        'max_lat': north,
                        'min_lon': west,
                        'max_lon': east,
                        'location': {
                            'type': poly_type,
                            'coordinates': polygons,
                        },
                        'center': {
                            'type': 'point',
                            'coordinates': [ center_lon, center_lat ],
                        }
                    }
                }
                #print json.dumps(update_json, indent=2)
                res, cont = http.request('http://grq.jpl.nasa.gov:8878/update', 'POST',
                                         json.dumps(update_json),
                                         {'Content-type': 'application/json'})
                if res.status != 200:
                    res_json = json.loads(cont)
                    #with open('/tmp/bad_json/%s.json' % granuleId, 'w') as f:
                    #    json.dump(res_json['update_json'], f, indent=2)
                    print json.dumps(res_json, indent=2)
                    print row
                    raise RuntimeError(res_json['message'])
                    #print res_json['message']
                #logger.info("res: %s" % res)
                #logger.info("cont: %s" % cont)
