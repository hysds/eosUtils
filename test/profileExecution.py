from tempfile import mktemp
import hotshot, hotshot.stats

import Numeric as Num
import sys
import os
import datetime
import eosservice.saveimage
import eosservice
import time
import re

from eosUtils.granule2 import getGranuleIdsByOrbitTable
from eosUtils.misc import getDatetimeFromDateString

try:
    set
except:
    from sets import Set as set

def main():
    
    #tests
    testConds=[
        ['short time/global','2005-11-03 00:00:00','2005-11-04 23:59:59',
         90.,-90.,-180.,180.,2],
        ['long time/global','2004-11-03 00:00:00','2005-11-04 23:59:59',
         90.,-90.,-180.,180.,2],
        ['short time/small area','2005-11-03 00:00:00','2005-11-04 23:59:59',
         20.,10.,134.,154.,2],
        ['long time/small area','2004-11-03 00:00:00','2005-11-04 23:59:59',
         20.,10.,134.,154.,2],
              ]
    
    for dataset in ['AIRS']:
    
        for tcond in testConds:
            testName,starttime,endtime,north,south,west,east,daynight=tcond
        
            #create start and ending datetime objects
            start_date=getDatetimeFromDateString(starttime)
            end_date=getDatetimeFromDateString(endtime)
    
            #get time range
            time_range=end_date-start_date
        
            #get middle search date and time range to pass to eosservice
            timeRangeArg=time_range/2
            searchDateArg=start_date+timeRangeArg
            
            #get bounds
            northArg=float(north)
            southArg=float(south)
            eastArg=float(east)
            westArg=float(west)
        
            ###########################################################
            #get via eosservice
            ###########################################################
            t=time.time()
            ids1=[]
            #'''
            # Find matching granules
            EOS = eosservice.eosservice(dataset)
            
            fileids = EOS.get_fileids_box(northArg,westArg,southArg,eastArg)
            #print fileids
            (matches, fileids) = EOS.filter_fileids(fileids,
                                                    searchDateArg, timeRangeArg,
                                                    daynight)
            
            
            for i in range(len(matches)):
                (prefix, year, month, day, julian_day, hour, minute) = matches[i]
                fileid = fileids[i]
                #pct = pcts[i]
            
                grid = EOS.get_match_grid([fileid])
                lats = 89-(Num.nonzero(grid)/360)
                lons = (Num.nonzero(grid)%360)-180
                (N, S) = (max(lats)+1, min(lats))
                (W, E) = (min(lons), max(lons)+1)
                if (E - W) > 180: # special case for cyclical longitude
                    lons = (lons + 360) % 360 # map to 0...359
                    (W, E) = (min(lons), max(lons)+1)
                    if (W%360)==(E%360):
                        W = -180
                        E = 180
                    if W>180:
                        W -= 360
                    if E>180:
                        E -= 360
            
                #do cases for datasets
                granule = 1 + ((hour * 60) + minute) / 6
                ids1.append("AIRS.%04d.%02d.%02d.%03d" % (year, month, day, granule))
            #'''
            t2=time.time()
            
            ###########################################################
            #get via table
            ###########################################################
            #ids2=[]
            ids2=getGranuleIdsByOrbitTable(dataset,starttime, endtime, southArg,
                                           northArg, westArg, eastArg)
            t3=time.time()
            
            #ids
            ids1.sort()
            #f=open('ids1','w')
            #f.write('\n'.join(ids1))
            #f.close()
            ids2.sort()
            #f2=open('ids2','w')
            #f2.write('\n'.join(ids2))
            #f2.close()
            set1=set(ids1)
            set2=set(ids2)
            print "#"*80
            print "Test on %s: %s" % (dataset,testName)
            print "starttime:", starttime
            print "endtime:",endtime
            print "north:",north
            print "south:",south
            print "west:",west
            print "east:",east
            print "daynight:",daynight
            print "# of granuleids generated: eosservice/orbit table: %s/%s" % \
                (len(set1),len(set2))
            set1Diff=list(set1-set2)
            set1Diff.sort()
            print "# of granuleids from eosservice - granuleids from orbit table: %s" % \
                len(set1Diff)
            if len(set1Diff)<10:
                print "granuleids:",set1Diff
            #f=open('diff1','w')
            #f.write('\n'.join(set1Diff))
            #f.close()
            set2Diff=list(set2-set1)
            set2Diff.sort()
            print "# of granuleids from orbit table - granuleids from eosservice: %s" % \
                len(set2Diff)
            if len(set2Diff)<10:
                print "granuleids:",set2Diff
            #f2=open('diff2','w')
            #f2.write('\n'.join(set2Diff))
            #f2.close()
            print "Time for eosservice is:", t2-t
            print "time for orbit table is:", t3-t2

if __name__=="__main__":
    profFile=mktemp('.prof')
    print "profFile:",profFile
    prof = hotshot.Profile(profFile)
    print prof.runcall(main)
    prof.close()
    stats = hotshot.stats.load(profFile)
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(20)
