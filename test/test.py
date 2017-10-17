from eosUtils.granule2 import getGranuleIdsByOrbitTable, DATASETINFO_TO_TABLE_MAP
import sciflo
import types
import os
import re
import sys

infoDict = getGranuleIdsByOrbitTable('MODIS-Terra', '2001-09-01 00:00:00', 
'2001-09-30 23:59:59', -30, 0, 0, 30, True)
print infoDict['MOD*.A2001246.2300']
