CREATE TABLE dataset1 (
        id INTEGER NOT NULL AUTO_INCREMENT,
        objectid VARCHAR(128) NOT NULL,
        starttime DATETIME NOT NULL,
        endtime DATETIME NOT NULL,
        georing POLYGON NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (objectid),
        KEY starttime (starttime),
        KEY endtime (endtime),
        KEY starttime_and_endtime (starttime, endtime),
        SPATIAL INDEX(georing)
)ENGINE=MyISAM DEFAULT CHARSET=utf8;

#INSERT
INSERT into dataset1 (objectid, starttime, endtime, georing) VALUES ('obj1', '2003-01-01 00:00:00', '2003-01-01 00:04:00', PolygonFromText('POLYGON ((73.2387725365540945 75.2948375836047035, 8.9042959101474395 66.3373323558296022, -41.3987199283289016 70.6019091749043071, -152.3703765440519931 85.2542670032671026, 73.2387725365540945 75.2948375836047035))', 4326));
