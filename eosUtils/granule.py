#-----------------------------------------------------------------------------
# Name:        granule.py
# Purpose:     Various classes/functions related to EOS granules.
#
# Author:      Gerald Manipon
#
# Created:     Wed Apr 12 12:21:15 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import datetime
import os
import matplotlib
matplotlib.use("Agg")
import cPickle

from misc import getDatetimeFromDateString, bound_vertices

#dataset -> orbit table mapping
DATASETINFO_TO_TABLE_MAP={
    'AIRS': {'orbitTableTup': cPickle.load(open(os.path.join(os.path.dirname(__file__),'AIRSOrbitTable.pkl'))),
             'daysPerCycle': 16,
             'orbitsPerCycle': 233,
             'granuleidTemplate': 'AIRS.%(year)04d.%(month)02d.%(day)02d.%(num)03d'
    }
}

def getGranuleIdsByOrbitTable(dataset, starttime, endtime, minLat=-90., maxLat=90.,
                              minLon=-180., maxLon=180.):
    """Code originally written by Dominic Mazzoni.  Return list of
    generated granuleids that match dataset and geospatial/temporal
    query.
    """
    
    #print "orig ctrdate:",ctrdate
    if (minLat==-90. and maxLat==90. and minLon==-180. and maxLon==180.):
        boundingBox=None
    else:
        boundingBox=bound_vertices(((minLon,maxLon),(minLat,maxLat)))

    #create start and ending datetime objects
    start_date=getDatetimeFromDateString(starttime)
    end_date=getDatetimeFromDateString(endtime)
    
    #get search_date and delta
    search_date = start_date
    time_range = datetime.timedelta(days=1, hours=0)

    #dict to accumulate granuleids
    granulesStringDict={}

    #get dataset's table tuple
    tableTuple=DATASETINFO_TO_TABLE_MAP[dataset]['orbitTableTup']
    
    #dataset's days per cycle
    daysPerCycle=DATASETINFO_TO_TABLE_MAP[dataset]['daysPerCycle']
    
    #get dataset's granuleid template
    granuleidTemplate=DATASETINFO_TO_TABLE_MAP[dataset]['granuleidTemplate']
    
    #get dataset's orbits per cycle
    orbitsPerCycle=DATASETINFO_TO_TABLE_MAP[dataset]['orbitsPerCycle']

    #get cycle start date from table
    cyclestartdate=tableTuple[0][0]
    #print cyclestartdate

    #loop over date range
    while search_date<=end_date:

        #print "################################"
        #print "searchdate:",search_date

        #get the timedelta of the end_date and search_date
        enddatedelta=end_date-search_date

        #get the diff of the search_date and cyclestartdate
        cyclediffdelta=search_date-cyclestartdate
        (cycleMult,cycleMod)=divmod(cyclediffdelta.days,daysPerCycle)

        #print "enddatedelta is",enddatedelta
        #print "cycleMult,cycleMod is",cycleMult, cycleMod

        #if there is at least daysPerCycle days left to check,
        #and it falls on the start of a cycle,
        #then we can just infer the granules from the
        #entire cycle
        if enddatedelta>=datetime.timedelta(days=daysPerCycle) and cycleMod==0:

            #how many cycles can be extracted from the current range
            (enddateMult,enddateMod)=divmod(enddatedelta.days,daysPerCycle)

            #set increment time
            increment_time = datetime.timedelta(days=daysPerCycle*enddateMult, hours=0)

            #print "Got in here."

            #loop over table
            for tableLine in tableTuple:

                #get info from table line
                (ctrdate, path, row0, row1, orbit0, orbit1, num, W, N, E, S)=tableLine

                #bounding box is entire globe or it overlaps with swath
                if (boundingBox is None or boundingBox.overlaps(bound_vertices(((W,E),(S,N))))):
                    
                    #print "GOT HERE1"

                    #loop over each cycle within this date range
                    thisMult=0
                    while thisMult<=(enddateMult-1):

                        #move ctrdate to our date
                        thisctrdate=ctrdate+cyclediffdelta
                        thisctrdate+=datetime.timedelta(days=(daysPerCycle*thisMult))

                        #print "new ctrdate[%s]:" % thisMult,thisctrdate
                        
                        #build dict for string subs
                        templateDict={'year': thisctrdate.year,
                                      'month': thisctrdate.month,
                                      'day': thisctrdate.day,
                                      'num': num,
                        }

                        #get granule string
                        granuleString=granuleidTemplate % templateDict

                        #check if this was already found
                        if not granulesStringDict.has_key(granuleString):
                            granulesStringDict[granuleString]=1

                        #increment by 1
                        thisMult+=1

        #otherwise just do one day
        else:

            #loop over table
            for tableLine in tableTuple:

                #get info from table line
                (ctrdate, path, row0, row1, orbit0, orbit1, num, W, N, E, S)=tableLine

                #bounding box is entire globe or it overlaps with swath
                if (boundingBox is None or boundingBox.overlaps(bound_vertices(((W,E),(S,N))))):
                    
                    #print "GOT HERE2"
                    
                    # Get date to within daysPerCycle
                    diffdate1=ctrdate-search_date
                    #print "ctrdate-search_date=diffdate1",ctrdate,search_date,diffdate1.days
                    (mult,mod)=divmod(diffdate1.days,daysPerCycle)
                    if mult>0:
                        ctrdate-=datetime.timedelta(days=(daysPerCycle*mult))
                        orbit0-=(orbitsPerCycle*mult)
                        orbit1-=(orbitsPerCycle*mult)

                    diffdate2=search_date-ctrdate
                    (mult,mod)=divmod(diffdate2.days,daysPerCycle)
                    if mult>0:
                        ctrdate+=datetime.timedelta(days=(daysPerCycle*mult))
                        orbit0+=(orbitsPerCycle*mult)
                        orbit1+=(orbitsPerCycle*mult)

                    # If so, move forward/backwards in time until the granule is within
                    # no more than 1/2 daysPerCycle of the requested time
                    #print "Going into first loop:"
                    while(ctrdate - search_date > datetime.timedelta(days=daysPerCycle/2)):
                        ctrdate -= datetime.timedelta(days=daysPerCycle)
                        orbit0 -= orbitsPerCycle
                        orbit1 -= orbitsPerCycle
                        #print "ctrdatea,orbit0a,orbit1a:",ctrdate,orbit0,orbit1

                    #print "Going into second loop:"
                    while(search_date - ctrdate > datetime.timedelta(days=daysPerCycle/2)):
                        ctrdate += datetime.timedelta(days=daysPerCycle)
                        orbit0 += orbitsPerCycle
                        orbit1 += orbitsPerCycle
                        #print "ctrdateb,orbit0b,orbit1b:",ctrdate,orbit0,orbit1

                    # Now see if this particular granule happened to fall within the time
                    # range the user requested, and if so, print out the results:
                    delta = abs(search_date - ctrdate)
                    if ctrdate>=start_date and ctrdate <=end_date and orbit0>0:
                    #if (delta <= time_range and orbit0>0):

                        #print "DELTA:",delta

                        #build dict for string subs
                        templateDict={'year': ctrdate.year,
                                      'month': ctrdate.month,
                                      'day': ctrdate.day,
                                      'num': num,
                        }

                        #get granule string
                        granuleString=granuleidTemplate % templateDict
                        
                        #check if this was already found
                        if not granulesStringDict.has_key(granuleString):
                            granulesStringDict[granuleString]=1
                            
            #set time range
            increment_time = datetime.timedelta(days=1, hours=0)

        #increment search_date by time_range
        #print "increment_time is",increment_time
        search_date+=increment_time

    #return list of list
    granuleIds=granulesStringDict.keys()
    granuleIds.sort()
    return granuleIds
