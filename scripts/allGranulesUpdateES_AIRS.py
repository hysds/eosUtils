import os, sys, datetime, time, csv, glob, re, types, json, httplib2, traceback
from urllib import urlopen
from StringIO import StringIO
import lxml.etree
from shapely.geometry import Polygon, MultiPolygon
import shapely.wkt
from pyes import ES

import cartopy.crs as ccrs


# global http object
http = httplib2.Http()


def getNamespacePrefixDict(xmlString):
    """Take an xml string and return a dict of namespace prefixes to
    namespaces mapping."""

    nss = {}
    matches = re.findall(r'\s+xmlns:?(\w*?)\s*=\s*[\'"](.*?)[\'"]', xmlString)
    for match in matches:
        prefix = match[0]; ns = match[1]
        if prefix == '': prefix = '_default'
        nss[prefix] = ns
    return nss


def runXpath(xml, xpathStr, nsDict={}):
    """Run XPath on xml and return result."""

    lxml.etree.clear_error_log()
    if isinstance(xml, lxml.etree._Element):
        root = xml
    else: root,nsDict = getXmlEtree(xml)
    
    #add '_' as default namespace prefix also
    if nsDict.has_key('_default'): nsDict['_'] = nsDict['_default']
    
    gotException = False
    if re.search(r'(?:/|\[|@){.*}', xpathStr):
        expr = lxml.etree.ETXPath(xpathStr)
        res = expr.evaluate(root)
    else:
        try: res = root.xpath(xpathStr)
        except Exception, e:
            if isinstance(e,lxml.etree.XPathSyntaxError):
                if re.search(r'XPATH_UNDEF_PREFIX_ERROR', str(e.error_log)): pass
                else: raise RuntimeError, "Error in xpath expression %s: %s" % (xpathStr,e.error_log)
            try: res = root.xpath(xpathStr,namespaces=nsDict)
            except lxml.etree.XPathSyntaxError, e:
                raise RuntimeError, "Error in xpath expression %s: %s" % (xpathStr,e.error_log)
            except:
                gotException = True
                res = []
        if isinstance(res, (types.ListType, types.TupleType)) and (gotException or len(res) == 0):
            xpathStr = addDefaultPrefixToXpath(xpathStr)
            lxml.etree.clear_error_log()
            try: res = root.xpath(xpathStr,namespaces=nsDict)
            except lxml.etree.XPathSyntaxError, e:
                raise RuntimeError, "Error in xpath expression %s: %s" % (xpathStr,e.error_log)
            except: raise
    if isinstance(res, (types.ListType, types.TupleType)):
        for i in range(len(res)):
            if isinstance(res[i], lxml.etree._Element): res[i] = lxml.etree.tostring(res[i],pretty_print=True)
            if isinstance(res[i], lxml.etree._ElementStringResult): res[i] = str(res[i])
    elif isinstance(res, lxml.etree._Element): res = lxml.etree.tostring(res,pretty_print=True)
    elif isinstance(res, lxml.etree._ElementStringResult): res = str(res)
    else: pass
    if len(res) == 1: return res[0]
    else: return res


def addDefaultPrefixToXpath(xpathStr):
    """Add default prefixes to xpath and return new xpath."""

    for sep in '/@[':
        xpathTokens = [i.strip() for i in xpathStr.split(sep)]
        for i in range(len(xpathTokens)):
            if xpathTokens[i] == '' or \
               xpathTokens[i].startswith('.') or \
               re.search(r'^\w+(\s*:|\()', xpathTokens[i]): pass
            else: xpathTokens[i] = '_default:' + xpathTokens[i]
        xpathStr = sep.join(xpathTokens)
    return xpathStr


def getXmlEtree(xml):
    """Return a tuple of [lxml etree element, prefix->namespace dict].
    """
    
    parser = lxml.etree.XMLParser(remove_blank_text=True)
    if xml.startswith('<?xml') or xml.startswith('<'):
        return (lxml.etree.parse(StringIO(xml), parser).getroot(), getNamespacePrefixDict(xml))
    else:
        try: xmlStr = urlopen(xml).read()
        except Exception, e:
            if re.search(r'unknown url type', str(e), re.IGNORECASE): xmlStr = urllibopen(xml).read()
            else: raise e
        return (lxml.etree.parse(StringIO(xmlStr), parser).getroot(), getNamespacePrefixDict(xmlStr))


STDRET_RE = re.compile(r'L2\.RetStd\.v6.*\.hdf\.xml$')
EAST_XP = './/EastBoundingCoordinate/text()'
WEST_XP = './/WestBoundingCoordinate/text()'
NORTH_XP = './/NorthBoundingCoordinate/text()'
SOUTH_XP = './/SouthBoundingCoordinate/text()'
STARTDATE_XP = './RangeDateTime/RangeBeginningDate/text()'
STARTTIME_XP = './RangeDateTime/RangeBeginningTime/text()'
ENDDATE_XP = './RangeDateTime/RangeEndingDate/text()'
ENDTIME_XP = './RangeDateTime/RangeEndingTime/text()'
GRANULEID_RE = re.compile(r'(AIRS\.\d{4}\.\d{2}\.\d{2}\.(\d{3}))\.L2')

datasetName = 'AIRS'
geolocName = 'AIRS'
doctype = 'swath'
index = datasetName.lower()

with open('es_settings.json') as f:
    settings = json.load(f)

with open('es_doctype_swath.json') as f:
    mapping = json.load(f)

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
            if STDRET_RE.search(file):
                #get space and time info
                try:
                    file = os.path.join(root, file)
                    et, nsDict = getXmlEtree(file)
                    east = eval(runXpath(et, EAST_XP, nsDict))
                    west = eval(runXpath(et, WEST_XP, nsDict))
                    north = eval(runXpath(et, NORTH_XP, nsDict))
                    south = eval(runXpath(et, SOUTH_XP, nsDict))
                    poly = Polygon((
                        ( west, north ),
                        ( east, north ),
                        ( east, south ),
                        ( west, south ),
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
                    startDate = runXpath(et, STARTDATE_XP, nsDict)
                    startTime = runXpath(et, STARTTIME_XP, nsDict)
                    date0 = datetime.datetime(*time.strptime("%s %s" % (startDate, startTime.split('.')[0]),
                                              '%Y-%m-%d %H:%M:%S')[:-3])
                    endDate = runXpath(et, ENDDATE_XP, nsDict)
                    endTime = runXpath(et, ENDTIME_XP, nsDict)
                    date1 = datetime.datetime(*time.strptime("%s %s" % (endDate, endTime.split('.')[0]),
                                              '%Y-%m-%d %H:%M:%S')[:-3])
                    granuleIdMatch = GRANULEID_RE.search(file)
                    if granuleIdMatch:
                        granuleId = granuleIdMatch.group(1)
                        granuleNum = int(granuleIdMatch.group(2))
                    else: raise RuntimeError("no granuleid found")
                    #print "%s:" % file, east, west, north, south, date0, date1, granuleId, granuleNum

                    # json
                    update_json = {
                        'dataset': 'AIRS',
                        'id': granuleId,
                        'data_product_name': 'AIRX2RET',
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

                    conn = ES('http://localhost:9200')
                    if not conn.indices.exists_index(index):
                        conn.indices.create_index(index, settings)
                    conn.indices.put_mapping(doctype, mapping, index)
                    ret = conn.index(update_json, index, doctype, update_json['id'])

                except Exception, e:
                    print "Got exception for file %s: %s" % (file, str(e))
                    print traceback.format_exc()
