import sys, MySQLdb
from cartography.geometry import Geometry
from cartography.proj.srs import SpatialReference
from datetime import datetime
from string import Template

from misc import getDatetimeFromDateString

#spatial reference
SRS = SpatialReference(epsg=4326)

#configured datasets
CONFIGURED_DATASETS = ['AIRS', 'MODIS-Terra', 'MODIS-Aqua']

#select by time
SELECT_BY_TIME = '''select objectid, starttime, endtime, min_lat, max_lat, min_lon, max_lon from $table where
(starttime between %s and %s) or
(endtime between %s and %s) or
(starttime <= %s and endtime >= %s);'''

#select by time and space
SELECT_BY_TIME_AND_SPACE = '''SELECT objectid, starttime, endtime, min_lat, max_lat, min_lon, max_lon from $table where
(
 (starttime between %s and %s) or
 (endtime between %s and %s) or
 (starttime <= %s and endtime >= %s)
) and
MBRIntersects(georing, PolygonFromText(
 'POLYGON (
  (
   %s %s,
   %s %s,
   %s %s,
   %s %s,
   %s %s
  )
)', 4326));'''

def queryDataset(dataset, starttime, endtime, latMin, latMax,
                 lonMin, lonMax, returnTimeSpaceInfo=False):
    """Return time/space info of granules that match query."""

    #get sqlite database file and table name
    if dataset.startswith('MYD'): tableId = 'AQUA'
    elif dataset.startswith('MOD'): tableId = 'TERRA'
    elif dataset.startswith('AIRS'): tableId = 'AIRS'
    else:
        raise RuntimeError("Unrecognized dataset: %s" % dataset)

    #get datetimes
    starttime = getDatetimeFromDateString(starttime) 
    endtime = getDatetimeFromDateString(endtime) 

    #get sqlite connection and cursor
    conn = MySQLdb.connect(db='test', host='127.0.0.1', port=8989,
                           user='root', passwd='sciflo')
    c = conn.cursor()

    #if spatial query is global, just use time
    if latMin <= -85. and latMax >= 85. and lonMin <= -175. and lonMax >= 175.:
        select = Template(SELECT_BY_TIME).substitute(table=tableId)
        args = (starttime, endtime, starttime, endtime, starttime, endtime)
    else:
        select = Template(SELECT_BY_TIME_AND_SPACE).substitute(table=tableId)
        args = (starttime, endtime, starttime, endtime, starttime, endtime,
                lonMin, latMin, lonMin, latMax, lonMax, latMax, lonMax,
                latMin, lonMin, latMin)

    #query
    c.execute(select, args)
    
    #build dict of information
    infoDict = {}
    for objectid, st_t, end_t, min_lat, max_lat, min_lon, max_lon in c:

        #get MODIS-* objectids
        if tableId == 'AQUA':
            objectid = objectid.replace('MYD03', 'MYD*')[0:18]
        elif tableId == 'TERRA':
            objectid = objectid.replace('MOD03', 'MOD*')[0:18]

        infoDict[objectid] = {
                              'starttime': st_t.isoformat(),
                              'endtime': end_t.isoformat(),
                              'lonMin': min_lon,
                              'lonMax': max_lon,
                              'latMin': min_lat,
                              'latMax': max_lat
                             }

    #return dict or just list of granules
    if returnTimeSpaceInfo: return infoDict
    else:
        objectids = infoDict.keys()
        objectids.sort()
        return objectids
