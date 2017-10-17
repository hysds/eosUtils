'''
#select by space and time
mysql> select objectid from TERRA where ((starttime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00")
or (endtime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00")) and
MBRIntersects(georing, PolygonFromText('POLYGON ((128.9607539029420025 -44.7809179012696035,
97.8391610400708061 -49.2303845881480981, 96.2475422096106996 -30.9974293283074012,
120.7540961187829964 -27.7149472763621993, 128.9607539029420025 -44.7809179012696035))', 4326)) limit 10;
+-------------------------------------------+
| objectid                                  |
+-------------------------------------------+
| MOD03.A2002054.1125.005.2008223111432.hdf |
| MOD03.A2002055.1030.005.2008223105213.hdf |
| MOD03.A2002054.0420.005.2008223114113.hdf |
| MOD03.A2002054.1130.005.2007115153902.hdf |
| MOD03.A2002054.0100.005.2007115132622.hdf |
| MOD03.A2002055.1710.005.2007116032940.hdf |
| MOD03.A2002055.2130.005.2007116043647.hdf |
| MOD03.A2002054.1625.005.2007115154550.hdf |
| MOD03.A2002054.2225.005.2007115224153.hdf |
| MOD03.A2002055.1530.005.2007116031929.hdf |
+-------------------------------------------+
10 rows in set (0.08 sec)
mysql> explain select objectid from TERRA where ((starttime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00") or (endtime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00")) and MBRIntersects(georing, PolygonFromText('POLYGON ((128.9607539029420025 -44.7809179012696035, 97.8391610400708061 -49.2303845881480981, 96.2475422096106996 -30.9974293283074012, 120.7540961187829964 -27.7149472763621993, 128.9607539029420025 -44.7809179012696035))', 4326)) limit 10;
+----+-------------+-------+-------+---------------------------------------------+---------+---------+------+-------+-------------+
| id | select_type | table | type  | possible_keys                               | key     | key_len | ref  | rows  | Extra       |
+----+-------------+-------+-------+---------------------------------------------+---------+---------+------+-------+-------------+
|  1 | SIMPLE      | TERRA | range | starttime,endtime,starttime_endtime,georing | georing | 34      | NULL | 11682 | Using where |
+----+-------------+-------+-------+---------------------------------------------+---------+---------+------+-------+-------------+
1 row in set (0.00 sec)

#Select by space and time ignoring indices
mysql> select objectid from TERRA ignore index (georing,starttime,endtime,starttime_endtime) where ((starttime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00") or (endtime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00")) and MBRIntersects(georing, PolygonFromText('POLYGON ((128.9607539029420025 -44.7809179012696035, 97.8391610400708061 -49.2303845881480981, 96.2475422096106996 -30.9974293283074012, 120.7540961187829964 -27.7149472763621993, 128.9607539029420025 -44.7809179012696035))', 4326)) limit 10;
+-------------------------------------------+
| objectid                                  |
+-------------------------------------------+
| MOD03.A2002054.0100.005.2007115132622.hdf |
| MOD03.A2002054.0105.005.2007115132652.hdf |
| MOD03.A2002054.0110.005.2007115131604.hdf |
| MOD03.A2002054.0240.005.2007115154520.hdf |
| MOD03.A2002054.0245.005.2007115154745.hdf |
| MOD03.A2002054.0420.005.2007115153002.hdf |
| MOD03.A2002054.0425.005.2007115152922.hdf |
| MOD03.A2002054.1120.005.2007115153904.hdf |
| MOD03.A2002054.1125.005.2007115153935.hdf |
| MOD03.A2002054.1130.005.2007115153902.hdf |
+-------------------------------------------+
10 rows in set (0.37 sec)

mysql> explain select objectid from TERRA ignore index (georing,starttime,endtime,starttime_endtime) where ((starttime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00") or (endtime between "2002-02-23 00:00:00" and "2002-02-25 00:00:00")) and MBRIntersects(georing, PolygonFromText('POLYGON ((128.9607539029420025 -44.7809179012696035, 97.8391610400708061 -49.2303845881480981, 96.2475422096106996 -30.9974293283074012, 120.7540961187829964 -27.7149472763621993, 128.9607539029420025 -44.7809179012696035))', 4326)) limit 10;
+----+-------------+-------+------+---------------+------+---------+------+---------+-------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows    | Extra       |
+----+-------------+-------+------+---------------+------+---------+------+---------+-------------+
|  1 | SIMPLE      | TERRA | ALL  | NULL          | NULL | NULL    | NULL | 1040360 | Using where |
+----+-------------+-------+------+---------------+------+---------+------+---------+-------------+
1 row in set (0.00 sec)
'''
import sys, MySQLdb
from cartography.geometry import Geometry
from cartography.proj.srs import SpatialReference
from string import Template

srs = SpatialReference(epsg=4326)

db = MySQLdb.connect(db='test', host='127.0.0.1', port=8979, user='root', passwd='sciflo')
c = db.cursor()
c.execute('select objectid, starttime, endtime, AsText(georing) from AQUA limit 10;')
for objectid, starttime, endtime, wkt in c.fetchall():
    xmin, ymin, xmax, ymax = Geometry.fromWKT(wkt, srs=srs).envelope().totuple()
    print objectid, starttime, endtime, xmin, ymin, xmax, ymax

#select by time and space    
SELECT_TMPL = Template('''SELECT objectid, starttime, endtime, AsText(georing) from $table \
where ((starttime between "$starttime" and "$endtime") or \
(endtime between "$starttime" and "$endtime")) and \
MBRIntersects(georing, PolygonFromText('POLYGON (($lonmin $latmin,$lonmin $latmax,\
$lonmax $latmax,$lonmax $latmin,$lonmin $latmin))', 4326));''')

selectSt = SELECT_TMPL.substitute(table='TERRA', starttime='2001-01-01 00:00:00',
           endtime='2001-01-01 10:00:00', latmin='-30.', latmax='10.', lonmin='0.',
           lonmax='30.')
print >>sys.stderr, selectSt
c.execute(selectSt)
for objectid, starttime, endtime, wkt in c.fetchall():
    xmin, ymin, xmax, ymax = Geometry.fromWKT(wkt, srs=srs).envelope().totuple()
    print objectid, starttime, endtime, xmin, ymin, xmax, ymax
