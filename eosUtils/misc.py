#-----------------------------------------------------------------------------
# Name:        misc.py
# Purpose:     Miscellaneous functions.
#
# Author:      Gerald Manipon
#
# Created:     Wed Apr 12 11:40:46 2006
# Copyright:   (c) 2006, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
try:
    from matplotlib.toolkits import basemap
except:
    from mpl_toolkits import basemap
from matplotlib.transforms import Bbox
import re
import datetime

def bound_vertices(verts):
    """Retrun the Bbox of the sequence of x,y tuples in verts."""
    return Bbox(verts)

def transformLonsLatsToMapCoords(lons,lats,projection='cyl',radius=6370997.):
    proj=basemap.proj.Proj({'proj':projection,'R':radius},-180.,-90.,180.,90.)
    return proj(lons,lats)

def boundingBoxesOverlap(lonsLatsBox1, lonsLatsBox2):
    """Return True if boxes overlap and False otherwise.  Arguments are
    a tuple/list of lons and lats, i.e. ((-180,180),(-90,90)) or
    ((-123,145),(43.3,-34)).  Order does not matter as a box will be
    calculated that bounds all.
    """
    box1=bound_vertices(lonsLatsBox1)
    box2=bound_vertices(lonsLatsBox2)
    if box1.overlaps(box2):
        return True
    else:
        return False

DT_REGEX = re.compile(r'^(\d{4})[/-](\d{2})[/-](\d{2})[\s*T](\d{2}):(\d{2}):(\d{2}).*$')
DT2_REGEX = re.compile(r'^(\d{4})[/-](\d{2})[/-](\d{2}).*$')

def getDatetimeFromDateString(dateStr):
    """Return datetime object from date string."""
    
    match = DT_REGEX.match(dateStr)
    if match:
        (year,month,day,hour,minute,second)=map(int,match.groups())
    else:

        match = DT2_REGEX.match(dateStr)
        if match:
            (year,month,day)=map(int,match.groups())
            (hour,minute,second)=(0,0,0)
        else:
            raise RuntimeError, "Failed to recognize date format: %s" % dateStr
    return datetime.datetime(year=year,month=month,day=day,hour=hour,minute=minute,
                             second=second)

def getDateStringFromDatetime(dt):
    """Return datetime object from date string."""
    
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (dt.year, dt.month, dt.day,
                                               dt.hour, dt.minute, dt.second)

def getBbox(llLon, llLat, urLon, urLat):
    """Return Bbox object of the bounding box specified by ll/ur.
    """
    
    return Bbox([[llLon, llLat], [urLon, urLat]])
