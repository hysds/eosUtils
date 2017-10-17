import os, sys, sqlite3, json
from datetime import datetime

from misc import getDatetimeFromDateString

#configured datasets
CONFIGURED_DATASETS = ['AIRS', 'MODIS-Terra', 'MODIS-Aqua', 'ALOS']

#select by time
SELECT_BY_TIME = '''select * from %s where
(starttime between :startTime and :endTime) or 
(endtime between :startTime and :endTime) or
(starttime <= :startTime and endtime >= :endTime);'''

#select by time and space
SELECT_BY_TIME_AND_SPACE = '''select * from %s where
(
 (starttime between :startTime and :endTime) or 
 (endtime between :startTime and :endTime) or
 (starttime <= :startTime and endtime >= :endTime)
) and
(
 (min_lat between :minLat and :maxLat) or
 (max_lat between :minLat and :maxLat) or
 (min_lat <= :minLat and max_lat >= :maxLat)
) and
(
 (min_lon between :minLon and :maxLon) or 
 (max_lon between :minLon and :maxLon) or
 (min_lon <= :minLon and max_lon >= :maxLon) or
 (min_lon > max_lon and 
  (
   min_lon between :minLon and :maxLon or
   (max_lon + 360.) between :minLon and :maxLon or
   (min_lon <= :minLon and (max_lon + 360.) >= :maxLon)
  )
 )
);'''

def queryDataset(dataset, starttime, endtime, latMin, latMax,
                 lonMin, lonMax, returnTimeSpaceInfo=False):
    """Return time/space info of granules that match query."""

    #get sqlite database file and table name
    if dataset.startswith('MYD'):
        tableId = 'AQUA'
        dbFile = os.path.join(sys.prefix, 'sqlite_data', 'MODIS-Aqua.db')
    elif dataset.startswith('MOD'):
        tableId = 'TERRA'
        dbFile = os.path.join(sys.prefix, 'sqlite_data', 'MODIS-Terra.db')
    elif dataset.startswith('AIRS'):
        tableId = 'AIRS'
        dbFile = os.path.join(sys.prefix, 'sqlite_data', 'AIRS.db')
    elif dataset.startswith('CloudSat'):
        tableId = 'CloudSat'
        dbFile = os.path.join(sys.prefix, 'sqlite_data', 'CloudSat.db')
    elif dataset == 'ALOS':
        tableId = 'ALOS'
        dbFile = os.path.join(sys.prefix, 'sqlite_data', 'ALOS.db')
    else:
        raise RuntimeError("Unrecognized dataset: %s" % dataset)

    #get datetimes
    starttime = getDatetimeFromDateString(starttime) 
    endtime = getDatetimeFromDateString(endtime) 

    #get sqlite connection and cursor
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    #if spatial query is global, just use time
    if (latMin <= -85. and latMax >= 85. and lonMin <= -175. and lonMax >= 175.) or \
        tableId == 'CloudSat':
        select = SELECT_BY_TIME % tableId
    else:
        select = SELECT_BY_TIME_AND_SPACE % tableId

    #query
    c.execute(select, {'startTime': starttime, 'endTime': endtime,
                       'minLon': lonMin, 'maxLon': lonMax,
                       'minLat': latMin, 'maxLat': latMax})
    
    #build dict of information
    infoDict = {}
    for fields in c:
        if dataset == 'ALOS':
            (objectid, st_t, end_t, bbox, min_lat, max_lat, min_lon, max_lon,
             frame_number, orbit_number, orbit_repeat, track_number) = fields
        else:
            (objectid, st_t, end_t, min_lat, max_lat, min_lon, max_lon) = fields

        #get MODIS-* objectids
        if tableId == 'AQUA':
            objectid = objectid.replace('MYD03', 'MYD*')[0:18]
        elif tableId == 'TERRA':
            objectid = objectid.replace('MOD03', 'MOD*')[0:18]

        #if CloudSat, just send nulls
        if dataset == 'CloudSat':
            infoDict[objectid] = {
                                  'starttime': getDatetimeFromDateString(st_t).isoformat(),
                                  'endtime': end_t,
                                  'lonMin': min_lon,
                                  'lonMax': max_lon,
                                  'latMin': min_lat,
                                  'latMax': max_lat
                                 }
        elif dataset == 'ALOS':
            infoDict[objectid] = {
                                  'starttime': getDatetimeFromDateString(st_t).isoformat(),
                                  'endtime': getDatetimeFromDateString(end_t).isoformat(),
                                  'bbox': json.loads(bbox),
                                  'lonMin': min_lon,
                                  'lonMax': max_lon,
                                  'latMin': min_lat,
                                  'latMax': max_lat,
                                  'frameNumber': frame_number,
                                  'orbitNumber': orbit_number,
                                  'orbitRepeat': orbit_repeat,
                                  'trackNumber': track_number
                                 }
        else:
            infoDict[objectid] = {
                                  'starttime': getDatetimeFromDateString(st_t).isoformat(),
                                  'endtime': getDatetimeFromDateString(end_t).isoformat(),
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
