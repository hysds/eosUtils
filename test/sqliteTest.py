#-----------------------------------------------------------------------------
# Name:        sqliteTest.py
# Purpose:     Various unittests for db module.
#
# Author:      Gerald Manipon
#
# Created:     Wed Apr 12 15:18:11 2011
# Copyright:   (c) 2011, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import unittest
import os
from lxml.etree import XML
import re
import gzip
import datetime
import time
import glob
import numpy as N

from eosUtils.db import queryDataset

thisDir=os.path.dirname(os.path.abspath(__file__))

class sqliteTestCase(unittest.TestCase):
    """Test case for functions/classes in db module."""

    def testShortTimespanGlobalCoverage(self):
        """Test new queryDataset function with a short timespan
        and global coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2005-11-03 00:03:07'
        endtime='2005-11-04 23:59:59'
        minLat=-90.
        maxLat=90.
        minLon=-180.
        maxLon=180.

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions - 576 granules returned by ECHO's WIST tool
        self.assertEqual(len(ids), 576)

        print "\ntestShortTimespanGlobalCoverage took: %02.2f seconds (%d results)." % (t2-t, len(ids))

    def testLongTimespanGlobalCoverage(self):
        """Test new queryDataset function with a long timespan
        and global coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2004-11-03 00:01:19'
        endtime='2005-11-04 23:57:43'
        minLat=-90.
        maxLat=90.
        minLon=-180.
        maxLon=180.

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids),105531)

        print "\ntestLongTimespanGlobalCoverage took: %02.2f seconds (%d results)." % (t2-t, len(ids))
        
    def testLongTimespanGlobalCoverage2(self):
        """Test new queryDataset function with a long timespan (past table data)
        and global coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2006-11-03 00:01:19'
        endtime='2010-11-04 23:57:43'
        minLat=-90.
        maxLat=90.
        minLon=-180.
        maxLon=180.

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids), 419442)

        print "\ntestLongTimespanGlobalCoverage2 took: %02.2f seconds (%d results)." % (t2-t, len(ids))

    def testShortTimespanSmallCoverage(self):
        """Test new queryDataset function with a short timespan
        and small coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2005-11-03 00:00:00'
        endtime='2005-11-04 23:59:59'
        minLat=-10.56
        maxLat=0.34
        minLon=-106.3
        maxLon=-85.3

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids),13)

        print "\ntestShortTimespanSmallCoverage took: %02.2f seconds (%d results)." % (t2-t, len(ids))

    def testLongTimespanSmallCoverage(self):
        """Test new queryDataset function with a long timespan
        and small coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2004-11-03 00:00:00'
        endtime='2005-11-04 23:59:59'
        minLat=-10.56
        maxLat=0.34
        minLon=-106.3
        maxLon=-85.3

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids), 2452)

        print "\ntestLongTimespanSmallCoverage took: %02.2f seconds (%d results)." % (t2-t, len(ids))
        
    def testLongTimespanSmallCoverage2(self):
        """Test new queryDataset function with a long timespan (past table data)
        and small coverage."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2006-11-03 00:00:00'
        endtime='2007-11-04 23:59:59'
        minLat=-10.56
        maxLat=0.34
        minLon=-106.3
        maxLon=-85.3

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids), 2433)

        print "\ntestLongTimespanSmallCoverage2 took: %02.2f seconds (%d results)." % (t2-t, len(ids))

    def testGranuleidMatch(self):
        """Test that granuleid generation matches actual metadata file."""

        #dataset
        dataset='MODIS-Terra'

        #met files before/during/after orbit table
        preMetFile=os.path.join(thisDir,'MOD03.A2001204.0225.005.2006075045356.hdf.xml.gz')
        durMetFile=os.path.join(thisDir,'MOD03.A2001242.0505.005.2006103203832.hdf.xml.gz')
        postMetFile=os.path.join(thisDir,'MOD03.A2006103.0205.005.2006103103133.hdf.xml.gz')
        metFiles=[preMetFile,durMetFile,postMetFile]

        #loop
        for metFile in metFiles:

            #get elt
            f=gzip.GzipFile(metFile)
            xmlStr=f.read()
            f.close()
            elt=XML(xmlStr)

            #get center datetime
            rbd=elt.xpath('.//RangeBeginningDate')[0].text
            rbt=elt.xpath('.//RangeBeginningTime')[0].text[:8]
            red=elt.xpath('.//RangeEndingDate')[0].text
            ret=elt.xpath('.//RangeEndingTime')[0].text[:8]
            starttime="%s %s" % (rbd,rbt)
            endtime="%s %s" % (red,ret)

            #get bounds of file and scale it down by .1
            pts=elt.xpath('.//Boundary/Point')
            lats = []
            lons = []
            for pt in pts:
                lons.append(float(pt.xpath('PointLongitude')[0].text))
                lats.append(float(pt.xpath('PointLatitude')[0].text))
            lats = N.array(lats); lons = N.array(lons)
            xmin = lats.min(); xmax = lats.max()
            ymin = lons.min(); ymax = lons.max()

            #get ids
            ids=queryDataset(dataset, starttime, endtime, -90., 90., -180., 180.)

            #check that one of the ids can be globbed to get the met file
            found=False
            for id in ids:
                files=glob.glob(id)
                if files>0:
                    found=True
            if not found: raise AssertionError, "Failed to get id that matches met file."

    def testTimeAndSpace(self):
        """Test new queryDataset function with a short timespan
        and small coverage and retrieving time/space info."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2005-11-03 00:00:00'
        endtime='2005-11-04 23:59:59'
        minLat=-10.56
        maxLat=0.34
        minLon=-106.3
        maxLon=-85.3

        #get ids
        t=time.time()
        infoDict=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon,
                          returnTimeSpaceInfo=True)
        t2=time.time()

        #make assertions
        self.assertEqual(len(infoDict),13)

        print "\ntestTimeAndSpace took: %02.2f seconds (%d results)." % (t2-t, len(infoDict))

    def testShortTimespanSmallCoverageVsLadsweb(self):
        """Test new queryDataset function with a long timespan (past table data)
        and small coverage vs. ladsweb results."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2000-01-01 00:00:00'
        endtime='2000-03-01 23:59:59'
        minLat=16.
        maxLat=18.
        minLon=-24.
        maxLon=-21.

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids),18)
        self.assertEqual(ids, ['MOD*.A2000055.1155', 'MOD*.A2000056.0025',
                               'MOD*.A2000056.0030', 'MOD*.A2000056.2330',
                               'MOD*.A2000057.1145', 'MOD*.A2000057.1320',
                               'MOD*.A2000058.0015', 'MOD*.A2000058.2320',
                               'MOD*.A2000059.1130', 'MOD*.A2000059.1310',
                               'MOD*.A2000060.0000', 'MOD*.A2000060.0005',
                               'MOD*.A2000060.1215', 'MOD*.A2000060.2310',
                               'MOD*.A2000061.0045', 'MOD*.A2000061.1255',
                               'MOD*.A2000061.1300', 'MOD*.A2000061.2350'])

        print "\ntestShortTimespanSmallCoverageVsLadsweb took: %02.2f seconds (%d results)." % (t2-t, len(ids))
        
    def testDataTableAfterLastDate(self):
        """Test data table for query after last date."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2007-01-01 00:00:00'
        endtime='2008-03-01 23:59:59'
        minLat=16.
        maxLat=18.
        minLon=-24.
        maxLon=-21.

        #get ids
        t=time.time()
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)
        t2=time.time()

        #make assertions
        self.assertEqual(len(ids), 1199)

        print "\ntestDataTableAfterLastDate took: %02.2f seconds (%d results)." % (t2-t, len(ids))
        
    def testGranuleidQuery(self):
        """Test granuleid query (Susan P.'s match2.py test)."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2006-01-01 23:41:33'
        endtime='2006-01-01 23:43:33'
        minLat=53.
        maxLat=54.
        minLon=170.
        maxLon=171.

        #get ids
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)

        #get ids
        idsGlobal=queryDataset(dataset,starttime, endtime, -90., 90., -180., 180.)

        #make assertions
        self.assertEqual(ids, idsGlobal)
        
    def testGranuleidQuery2(self):
        """Test another granuleid query (Susan P.'s match3.py test)."""

        #spatio/temporal parameters
        dataset='MODIS-Terra'
        starttime='2004-09-21 23:15:00'
        endtime='2004-09-21 23:19:00'
        minLat=25.
        maxLat=26.
        minLon=53.
        maxLon=54.

        #get ids
        ids=queryDataset(dataset,starttime, endtime, minLat, maxLat, minLon, maxLon)

        #make assertions
        self.assertEqual(ids, [])
        
#create testsuite function
def getTestSuite():
    """Creates and returns a test suite."""
    #run tests
    myTestSuite = unittest.TestSuite()
    myTestSuite.addTest(sqliteTestCase("testShortTimespanGlobalCoverage"))
    myTestSuite.addTest(sqliteTestCase("testLongTimespanGlobalCoverage"))
    myTestSuite.addTest(sqliteTestCase("testLongTimespanGlobalCoverage2"))
    myTestSuite.addTest(sqliteTestCase("testShortTimespanSmallCoverage"))
    myTestSuite.addTest(sqliteTestCase("testLongTimespanSmallCoverage"))
    myTestSuite.addTest(sqliteTestCase("testLongTimespanSmallCoverage2"))
    myTestSuite.addTest(sqliteTestCase("testGranuleidMatch"))
    myTestSuite.addTest(sqliteTestCase("testTimeAndSpace"))
    myTestSuite.addTest(sqliteTestCase("testShortTimespanSmallCoverageVsLadsweb"))
    myTestSuite.addTest(sqliteTestCase("testDataTableAfterLastDate"))
    myTestSuite.addTest(sqliteTestCase("testGranuleidQuery"))
    myTestSuite.addTest(sqliteTestCase("testGranuleidQuery2"))

    #return
    return myTestSuite

#main
if __name__=="__main__":

    #get testSuite
    testSuite=getTestSuite()

    #run it
    runner=unittest.TextTestRunner()
    runner.run(testSuite)


