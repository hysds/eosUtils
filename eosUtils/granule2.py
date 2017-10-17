#-----------------------------------------------------------------------------
# Name:        granule2.py
# Purpose:     Various classes/functions related to EOS granules using
#              new orbit table format.
#
# Author:      Gerald Manipon
#
# Created:     Wed Apr 12 12:21:15 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import datetime
import os
import cPickle
import types
import glob

from misc import getDatetimeFromDateString, getBbox, getDateStringFromDatetime

#dataset -> orbit table mapping
DATASETINFO_TO_TABLE_MAP={
    'AIRS_2002': {'pickledInfo': 'AIRSOrbitTable_2002.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2003': {'pickledInfo': 'AIRSOrbitTable_2003.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2004': {'pickledInfo': 'AIRSOrbitTable_2004.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2005': {'pickledInfo': 'AIRSOrbitTable_2005.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2006': {'pickledInfo': 'AIRSOrbitTable_2006.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2007': {'pickledInfo': 'AIRSOrbitTable_2007.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2008': {'pickledInfo': 'AIRSOrbitTable_2008.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2009': {'pickledInfo': 'AIRSOrbitTable_2009.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2010': {'pickledInfo': 'AIRSOrbitTable_2010.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS_2011': {'pickledInfo': 'AIRSOrbitTable_2011.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'AIRS': {'pickledInfo': 'AIRSOrbitTable.pkl',
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    },
    'MODIS-Terra_2000': {'pickledInfo': 'MODIS-TerraOrbitTable_2000.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2001': {'pickledInfo': 'MODIS-TerraOrbitTable_2001.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2002': {'pickledInfo': 'MODIS-TerraOrbitTable_2002.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2003': {'pickledInfo': 'MODIS-TerraOrbitTable_2003.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2004': {'pickledInfo': 'MODIS-TerraOrbitTable_2004.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2005': {'pickledInfo': 'MODIS-TerraOrbitTable_2005.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2006': {'pickledInfo': 'MODIS-TerraOrbitTable_2006.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2007': {'pickledInfo': 'MODIS-TerraOrbitTable_2007.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2008': {'pickledInfo': 'MODIS-TerraOrbitTable_2008.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2009': {'pickledInfo': 'MODIS-TerraOrbitTable_2009.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2010': {'pickledInfo': 'MODIS-TerraOrbitTable_2010.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra_2011': {'pickledInfo': 'MODIS-TerraOrbitTable_2011.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Terra': {'pickledInfo': 'MODIS-TerraOrbitTable.pkl',
             'granuleidTemplate': 'MOD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2002': {'pickledInfo': 'MODIS-AquaOrbitTable_2002.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2003': {'pickledInfo': 'MODIS-AquaOrbitTable_2003.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2004': {'pickledInfo': 'MODIS-AquaOrbitTable_2004.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2005': {'pickledInfo': 'MODIS-AquaOrbitTable_2005.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2006': {'pickledInfo': 'MODIS-AquaOrbitTable_2006.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2007': {'pickledInfo': 'MODIS-AquaOrbitTable_2007.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2008': {'pickledInfo': 'MODIS-AquaOrbitTable_2008.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2009': {'pickledInfo': 'MODIS-AquaOrbitTable_2009.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2010': {'pickledInfo': 'MODIS-AquaOrbitTable_2010.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua_2011': {'pickledInfo': 'MODIS-AquaOrbitTable_2011.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
    'MODIS-Aqua': {'pickledInfo': 'MODIS-AquaOrbitTable.pkl',
             'granuleidTemplate': 'MYD*.A%(year)04d%(doy)03d.%(hour)02d%(min)02d'
    },
}

DATASETS_WITH_TABLE_DATA = ['AIRS', 'MODIS-Terra', 'MODIS-Aqua']

#extract first & last datetimes
FIRST_DATETIME = {}
LAST_DATETIME = {}
for dataset in DATASETS_WITH_TABLE_DATA:
    dataFiles = glob.glob(os.path.join(os.path.dirname(__file__),
                       dataset + 'OrbitTable_????.pkl'))
    dataFiles.sort()
    FIRST_DATETIME[dataset] = cPickle.load(open(dataFiles[0]))[5][0][1]
    LAST_DATETIME[dataset] = cPickle.load(open(dataFiles[-1]))[5][-1][1]

class InvalidDateError(Exception): pass

def getDatasetInfo(dataset, start_date=None):
    """Return pickeled info and granuleid template for a dataset."""
    
    #get dataset's table tuple and granuleid template
    getDataset = dataset
    tableType = 'orbit'
    if dataset in DATASETS_WITH_TABLE_DATA:
        if isinstance(start_date, datetime.datetime):
            getDataset = '%s_%04d' % (dataset, start_date.year)
            tableType = 'data'
    try:
        pickledInfo = cPickle.load(open(os.path.join(os.path.dirname(__file__),
            DATASETINFO_TO_TABLE_MAP[getDataset]['pickledInfo'])))
    except KeyError, e:
        raise InvalidDateError("No data exists for %s.  Try a later date." % \
                               getDateStringFromDatetime(start_date))
    granuleidTemplate=DATASETINFO_TO_TABLE_MAP[getDataset]['granuleidTemplate']
    return (pickledInfo, granuleidTemplate, tableType)

def getGranuleIdsByOrbitTable(dataset, starttime, endtime, minLat=-90., maxLat=90.,
                              minLon=-180., maxLon=180., returnTimeSpaceInfo=False,
                              forceOrbitTable=False):
    """Return list of generated granuleids that match dataset and geospatial/temporal
    query.
    """
    #print "orig ctrdate:",ctrdate
    if (minLat==-90. and maxLat==90. and minLon==-180. and maxLon==180.):
        boundingBox=None
        wrappingBox=None
    else:
        boundingBox=getBbox(minLon, minLat, maxLon, maxLat)
        if minLon > maxLon:
            wrappingBox=getBbox(minLon, minLat, maxLon + 360., maxLat)
        else:
            wrappingBox=boundingBox

    #create start and ending datetime objects
    if isinstance(starttime, datetime.datetime): start_date = starttime
    else: start_date = getDatetimeFromDateString(starttime)
    if isinstance(endtime, datetime.datetime): end_date = endtime
    else: end_date = getDatetimeFromDateString(endtime)

    #get delta
    time_range=datetime.timedelta(days=1, hours=0)

    #dict to accumulate granuleids
    granulesStringDict={}

    #check if using data table and past last date
    if dataset in DATASETS_WITH_TABLE_DATA and \
        start_date >= LAST_DATETIME[dataset]:
        forceOrbitTable = True
    
    #get dataset's table tuple and granuleid template
    if forceOrbitTable:
        pickledInfo, granuleidTemplate, tableType = getDatasetInfo(dataset)
    else:
        pickledInfo, granuleidTemplate, tableType = getDatasetInfo(dataset, start_date)

    #dataset's table info
    (minutesPerGranule,daysPerCycle,granulesPerDay,granulesPerCycle,timeSlop,
    tableTuple)=pickledInfo
    
    #get last date
    lastTime = tableTuple[-1][1]

    #get cycle start/end date from table
    cyclestartdate=tableTuple[0][1]-timeSlop
    cycleenddate=tableTuple[-1][1]-timeSlop

    #granule time incr
    timeIncr=datetime.timedelta(minutes=minutesPerGranule)

    #match up first search date in orbit table and get its index
    search_date=start_date
    if search_date<=cyclestartdate:
        
        #skip if date is prior to beginning of data production
        if tableType == 'data' and search_date < (FIRST_DATETIME[dataset] - timeSlop):
            cyclestartdate = FIRST_DATETIME[dataset] - timeSlop
            search_date = cyclestartdate
            start_date = cyclestartdate
            if end_date < start_date: end_date = start_date

        #get the diff of the search_date and cyclestartdate
        cyclediffdelta=cyclestartdate-search_date

        #if exactly, 0 is the index
        if cyclediffdelta:

            (cycleMult,cycleMod)=divmod(cyclediffdelta.days,daysPerCycle)

            #match
            search_date+=datetime.timedelta(days=(daysPerCycle*cycleMult)+daysPerCycle, hours=0)

            #get time diff and get index of matching granule
            timeDiff=search_date-cyclestartdate
            timediffSecs=(timeDiff.days*86400)+timeDiff.seconds
            granuleStartIdx=((timediffSecs/60)/minutesPerGranule)

            #adjust start date to align with orbit table
            start_date-=datetime.timedelta(seconds=timeDiff.seconds%(minutesPerGranule*60))

        else:
            granuleStartIdx=0

    #search date is within orbit table
    elif search_date<=cycleenddate:

        #get the diff of the search_date and cyclestartdate
        cyclediffdelta=search_date-cyclestartdate

        #if exactly, 0 is the index
        if cyclediffdelta:

            #get time diff and get index of matching granule
            timediffSecs=(cyclediffdelta.days*86400)+cyclediffdelta.seconds
            granuleStartIdx=((timediffSecs/60)/minutesPerGranule)

            #adjust start date to align with orbit table
            start_date-=datetime.timedelta(seconds=cyclediffdelta.seconds%(minutesPerGranule*60))

        else:
            granuleStartIdx=len(tableTuple)-1

    #search date is past orbit table
    else:

        #get the diff of the search_date and cycleenddate
        cyclediffdelta=search_date-cycleenddate

        (cycleMult,cycleMod)=divmod(cyclediffdelta.days,daysPerCycle)

        #match
        #print search_date
        search_date-=datetime.timedelta(days=(daysPerCycle*cycleMult)+daysPerCycle, hours=0)

        #get time diff and get index of matching granule
        timeDiff=search_date-cyclestartdate
        timediffSecs=(timeDiff.days*86400)+timeDiff.seconds
        granuleStartIdx=((timediffSecs/60)/minutesPerGranule)

        #adjust start date to align with orbit table
        start_date-=datetime.timedelta(seconds=timeDiff.seconds%(minutesPerGranule*60))

    #add some slop to the index and the beginning/end of the search date range
    #if we have a boundingBox.  Otherwise, just give what was asked for.
    if boundingBox and dataset not in DATASETS_WITH_TABLE_DATA: slop=1
    else: slop=0
    searchSlop=datetime.timedelta(minutes=slop*minutesPerGranule)
    idx=granuleStartIdx-slop
    startingYear = start_date.year
    thisctrdate=start_date-searchSlop
    thisenddate=end_date+searchSlop
    while thisctrdate<=thisenddate:
        
        #check if doing table data
        if tableType == 'data':
            if thisctrdate.year > startingYear:
                nextResults =  getGranuleIdsByOrbitTable(dataset, thisctrdate, endtime, minLat,
                                                         maxLat, minLon, maxLon,
                                                         returnTimeSpaceInfo)
                #recurse
                if returnTimeSpaceInfo:
                    granulesStringDict.update(nextResults)
                    return granulesStringDict
                else:
                    granuleIds = granulesStringDict.keys()
                    granuleIds.extend(nextResults)
                    granuleIds.sort()
                    return granuleIds
            elif thisctrdate.year == startingYear and thisctrdate > lastTime:
                nextResults =  getGranuleIdsByOrbitTable(dataset, thisctrdate, endtime, minLat,
                                                         maxLat, minLon, maxLon,
                                                         returnTimeSpaceInfo,
                                                         forceOrbitTable=True)
                #recurse
                if returnTimeSpaceInfo:
                    granulesStringDict.update(nextResults)
                    return granulesStringDict
                else:
                    granuleIds = granulesStringDict.keys()
                    granuleIds.extend(nextResults)
                    granuleIds.sort()
                    return granuleIds
            else: pass
            
        #get info from table line
        tableTupleItem = tableTuple[idx%len(tableTuple)]
        #if no granule exists
        if tableTupleItem is None:
            thisctrdate+=timeIncr
            idx+=1
            continue
        (granPolygon, granCtrDate, granNum) = tableTupleItem


        #bounding box is entire globe or it overlaps with swath
        if isinstance(granPolygon, (types.TupleType, types.ListType)):
            if dataset.startswith('MOD') or dataset.startswith('AIRS'):
                granMinLon, granMinLat, granMaxLon, granMaxLat = granPolygon
            else: granMinLon, granMaxLon, granMinLat, granMaxLat = granPolygon
        else:
            granMinLon, granMaxLon, granMinLat, granMaxLat = granPolygon.boundingBox()
        granPolygon = getBbox(granMinLon, granMinLat, granMaxLon, granMaxLat)
        
        wrapAroundFlag = False
        testBbox = boundingBox
        if testBbox is not None and (granMinLon > granMaxLon or abs(granMinLon - granMaxLon) > 180.):
            wrapAroundFlag = True
            granPolygon =  getBbox(granMinLon, granMinLat, granMaxLon + 360., granMaxLat)
            testBbox = wrappingBox
        
        if testBbox is None or granPolygon.overlaps(testBbox):

            #build dict for string subs
            templateDict={
                'year': thisctrdate.year,
                'month': thisctrdate.month,
                'day': thisctrdate.day,
                'doy': (thisctrdate-datetime.datetime(year=thisctrdate.year,month=1,day=1)).days+1,
                'hour': thisctrdate.hour,
                'min': thisctrdate.minute,
                'num': granNum,
            }

            #get granule string
            granuleString=granuleidTemplate % templateDict
            
            #check if this was already found
            if not granulesStringDict.has_key(granuleString):
                if returnTimeSpaceInfo:
                    if wrapAroundFlag: lonMax = granPolygon.xmax - 360.
                    else: lonMax = granPolygon.xmax
                    lonMin = granPolygon.xmin
                    granulesStringDict[granuleString]={
                        'starttime':thisctrdate.isoformat(),
                        'endtime':(thisctrdate+datetime.timedelta(minutes=minutesPerGranule)).isoformat(),
                        'lonMin':lonMin,
                        'lonMax':lonMax,
                        'latMin':granPolygon.ymin,
                        'latMax':granPolygon.ymax,
                    }
                else:
                    granulesStringDict[granuleString]=1

        #increment by granule period and index counter
        thisctrdate+=timeIncr
        idx+=1

    #return list of list
    if returnTimeSpaceInfo:
        return granulesStringDict
    else:
        granuleIds=granulesStringDict.keys()
        granuleIds.sort()
        return granuleIds

def getOrbitCycleIds(dataset, start_date=None):
    """Return list of orbit cycle datasetids for a dataset."""
    
    #get dataset's table tuple and granuleid template
    pickledInfo, granuleidTemplate = getDatasetInfo(dataset, start_date)

    #dataset's table info
    (minutesPerGranule,daysPerCycle,granulesPerDay,granulesPerCycle,timeSlop,
    tableTuple)=pickledInfo
    polygon, thisctrdate, granule0 = tableTuple[0]
    thisctrdate -= timeSlop
    
    print "minutesPerGranule:", minutesPerGranule
    print "daysPerCycle:", daysPerCycle
    print "granulesPerDay:", granulesPerDay
    print "granulesPerCycle:", granulesPerCycle
    print "timeSlop:", timeSlop
    print "thisctrdate:", thisctrdate
    
    objectids = []
    
    while True:
        #build dict for string subs
        templateDict = {
            'year': thisctrdate.year,
            'month': thisctrdate.month,
            'day': thisctrdate.day,
            'doy': (thisctrdate-datetime.datetime(year=thisctrdate.year,month=1,day=1)).days+1,
            'hour': thisctrdate.hour,
            'min': thisctrdate.minute,
            #'num': granNum, #for now, doing for MODIS-Terra only
        }
        
        #get granule string
        objectids.append(granuleidTemplate % templateDict)
        
        thisctrdate += datetime.timedelta(minutes=granulesPerCycle * minutesPerGranule)
        
        #break if past now
        if thisctrdate > datetime.datetime.utcnow(): break
        
    return objectids
