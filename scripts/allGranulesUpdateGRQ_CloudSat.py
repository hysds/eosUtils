import os, sys, time, csv, glob, re, types, json, httplib2
from datetime import datetime
from urllib import urlopen
from StringIO import StringIO
import lxml.etree
from string import Template

from wvcc.cloudsat.GeoProf import GeoProf


# global http object
http = httplib2.Http()


GEOPROF_RE = re.compile(r'((?P<year>\d{4})(?P<doy>\d{3})(?P<misc>\d{6}_\d{5})_CS)_2B-GEOPROF_GRANULE_.*\.hdf$')

datasetName = 'CloudSat'
geolocName = 'CloudSat'

rootDataDir = os.path.abspath(sys.argv[1])

yearDirs = os.listdir(rootDataDir)
yearDirs.sort()
yearDirs = [os.path.realpath(os.path.join(rootDataDir, i)) for i in yearDirs]
count = 0
for rootDir in yearDirs:
    for root, dirs, files in os.walk(rootDir):
        dirs.sort()
        files.sort()
        for file in files:
            match = GEOPROF_RE.search(file)
            if match:
                #get space and time info
                try:
                    file = os.path.join(root, file)
                    gp = GeoProf(file)
                    gp.simplify()
                    west, south, east, north = gp.getBbox()
                    date0 = datetime(*time.gmtime(gp.geoDict['Profile_UTC'][0])[0:6])
                    date1 = datetime(*time.gmtime(gp.geoDict['Profile_UTC'][-1])[0:6])
                    objectid = match.group(1)
                    #print "%s:" % file, date0, date1, objectid

                    # json
                    update_json = {
                        'dataset': 'CloudSat',
                        'id': objectid,
                        'urls': [],
                        'browse_urls': [],
                        'metadata': {
                            'data_product_name': 'CloudSat',
                            'version': 'R04',
                            'starttime': date0.isoformat() + 'Z',
                            'endtime': date1.isoformat() + 'Z',
                            'min_lat': south,
                            'max_lat': north,
                            'min_lon': west,
                            'max_lon': east,
                            'location': {
                                'type': gp.getLineType(),
                                'coordinates': gp.getLineStrings()
                            },
                            'center': {
                                'type': 'point',
                                'coordinates': gp.getCenter()
                            }
                        }
                    }
                    #print json.dumps(update_json, indent=2)
                    res, cont = http.request('http://grq.jpl.nasa.gov:8878/update', 'POST',
                                             json.dumps(update_json),
                                             {'Content-type': 'application/json'})
                    if res.status != 200:
                        raise RuntimeError(json.loads(cont)['message'])
                    #logger.info("res: %s" % res)
                    #logger.info("cont: %s" % cont)
    
                except Exception, e:
                    print json.dumps(update_json, indent=2)
                    print "Got exception for file %s: %s" % (file, str(e))
