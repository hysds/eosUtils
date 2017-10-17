from eosUtils.granule2 import getGranuleIdsByOrbitTable, DATASETINFO_TO_TABLE_MAP
import sciflo
import types
import os
import re
import sys

infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2001-09-01 00:00:00', 
'2001-09-01 00:04:01', -90, 90, -180, 180, True)
print infoDict, len(infoDict)
#bbox in granule
infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2001-09-01 00:00:00', 
'2001-09-01 00:04:01', 0, 10, 0, 10, True)
print infoDict, len(infoDict)
infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2001-09-01 00:00:00', 
'2001-09-01 00:04:01', -90, 90, 164, 175, True)
print infoDict, len(infoDict)
#infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2001-09-01 00:00:00', 
#'2001-09-01 00:04:01', 177, 179, -180, 180, True)
#print infoDict, len(infoDict)
'''
#bbox partially in granule
infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2003-09-01 00:00:00', 
'2003-09-01 00:04:01', -20, 10, 0, 10, True)
print infoDict, len(infoDict)
infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2003-09-01 00:00:00', 
'2003-09-01 00:04:01', -20, 10, -90, 10, True)
print infoDict, len(infoDict)
'''
