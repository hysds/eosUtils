'''
#select by time
sqlite> select * from TERRA where
   ...> ((starttime between "2006-01-01 00:00:00" and "2006-01-01 01:00:00") or
   ...> (endtime between "2006-01-01 00:00:00" and "2006-01-01 01:00:00") or
   ...> (starttime <= "2006-01-01 00:00:00" and endtime >= "2006-01-01 01:00:00"));
MOD03.A2005365.2355.005.2010167205848.hdf|2005-12-31 23:55:00|2006-01-01 00:00:00|-30.8302849551217|-9.8128903324997|-31.8020178479243|-5.11001021082979
MOD03.A2006001.0000.005.2010169205915.hdf|2006-01-01 00:00:00|2006-01-01 00:05:00|-12.8604044623969|8.07458597893059|-35.4204540365314|-10.6263903756006
MOD03.A2006001.0005.005.2010169205845.hdf|2006-01-01 00:05:00|2006-01-01 00:10:00|5.02620734128787|25.9967605304294|-40.3216461225069|-14.6172836324813
MOD03.A2006001.0010.005.2010169210008.hdf|2006-01-01 00:10:00|2006-01-01 00:15:00|22.687120402003|43.9346390626826|-47.6719752046014|-17.6584915467621
MOD03.A2006001.0015.005.2010169205844.hdf|2006-01-01 00:15:00|2006-01-01 00:20:00|39.8955601116046|61.8387258140415|-60.7747408637319|-19.8742492985363
MOD03.A2006001.0020.005.2010169210047.hdf|2006-01-01 00:20:00|2006-01-01 00:25:00|56.0134604900696|79.761681219165|-90.2009453792733|-14.9232162059047
MOD03.A2006001.0025.005.2010169205853.hdf|2006-01-01 00:25:00|2006-01-01 00:30:00|68.6267786492026|89.9976153645794|-180.0|180.0
MOD03.A2006001.0030.005.2010169205916.hdf|2006-01-01 00:30:00|2006-01-01 00:35:00|58.045662589029|82.2731274299537|131.476107396637|-143.121412318902
MOD03.A2006001.0035.005.2010169210016.hdf|2006-01-01 00:35:00|2006-01-01 00:40:00|42.1852949599224|64.3509981056117|140.452883347482|-176.210448020624
MOD03.A2006001.0040.005.2010169210037.hdf|2006-01-01 00:40:00|2006-01-01 00:45:00|25.07365215449|46.4501698930583|138.367319900398|169.346772779395
MOD03.A2006001.0045.005.2010169210051.hdf|2006-01-01 00:45:00|2006-01-01 00:50:00|7.45553474390958|28.5162189473993|135.443225964754|161.491453117887
MOD03.A2006001.0050.005.2010169210557.hdf|2006-01-01 00:50:00|2006-01-01 00:55:00|-10.3847839868478|10.587230431271|131.614321197399|156.346020750185
MOD03.A2006001.0055.005.2010169210023.hdf|2006-01-01 00:55:00|2006-01-01 01:00:00|-28.2933907406256|-7.23847911848129|126.402709362883|152.601832401582
MOD03.A2006001.0100.005.2010169205944.hdf|2006-01-01 01:00:00|2006-01-01 01:05:00|-46.1733455431796|-24.8046327762835|118.474966713401|149.767005816523

#select by time
sqlite> select * from TERRA where
   ...> ((starttime between "2006-01-01 00:00:00" and "2006-01-01 01:00:00") or
   ...> (endtime between "2006-01-01 00:00:00" and "2006-01-01 01:00:00") or
   ...> (starttime <= "2006-01-01 00:00:00" and endtime >= "2006-01-01 01:00:00")) and
   ...> ((min_lat between -15.2 and 0.1) or (max_lat between -15.2 and 0.1) or
   ...> (min_lat <= -15.2 and max_lat >= 0.1)) and
   ...> ((min_lon between 120.1 and 154.1) or (max_lon between 120.1 and 154.1) or
   ...> (min_lon <= 120.1 and max_lon >= 154.1));
MOD03.A2006001.0050.005.2010169210557.hdf|2006-01-01 00:50:00|2006-01-01 00:55:00|-10.3847839868478|10.587230431271|131.614321197399|156.346020750185
MOD03.A2006001.0055.005.2010169210023.hdf|2006-01-01 00:55:00|2006-01-01 01:00:00|-28.2933907406256|-7.23847911848129|126.402709362883|152.601832401582
'''
import sqlite3
from datetime import datetime
from string import Template

#select by time
SELECT_BY_TIME = '''select * from TERRA where
 (starttime between ? and ?) or (endtime between ? and ?) or
 (starttime <= ? and endtime >= ?);'''

#select by time and space
SELECT_BY_TIME_AND_SPACE = '''select * from TERRA where
((starttime between ? and ?) or (endtime between ? and ?) or
 (starttime <= ? and endtime >= ?)) and
((min_lat between ? and ?) or (max_lat between ? and ?) or
 (min_lat <= ? and max_lat >= ?)) and
((min_lon between ? and ?) or (max_lon between ? and ?) or
 (min_lon <= ? and max_lon >= ?));'''

#query params
starttime = datetime(2006, 1, 1, 0, 0, 0)
endtime = datetime(2006, 1, 1, 1, 0, 0)
min_lat = -15.2
max_lat = 0.1
min_lon = 120.1
max_lon = 154.1

#conn = sqlite3.connect("MODIS-Terra.db")
conn = sqlite3.connect("MODIS-Aqua.db")
c = conn.cursor()

#select by time
print "select by time"
c.execute(SELECT_BY_TIME, (starttime, endtime, starttime, endtime,
                           starttime, endtime))
for row in c:
    print row

print "\n\n"

#select by time and space
print "select by time and space"
c.execute(SELECT_BY_TIME_AND_SPACE, (starttime, endtime, starttime, endtime,
                                     starttime, endtime, min_lat, max_lat,
                                     min_lat, max_lat, min_lat, max_lat,
                   min_lon, max_lon, min_lon, max_lon,
                   min_lon, max_lon))
for row in c:
    print row
