#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        updateSqlite_CloudSat.py
# Purpose:     Update sqlite metadata db for CloudSat.
#
# Author:      Gerald Manipon
#
# Created:     Tue Jan 31 10:12:36 2011
# Copyright:   (c) 2011, California Institute of Technology.
#              U.S. Government Sponsorship acknowledged.
#-----------------------------------------------------------------------------
import os, sys, time, csv, glob, re
import sqlite3
from sqlalchemy import create_engine
from datetime import datetime

from sciflo.utils import runXpath, getXmlEtree

CS_RE = re.compile(r'^(\d{4})(\d{3})(\d{2})(\d{2})(\d{2})_\d{5}_CS$')

DUPLICATE_ENTRY_RE = re.compile(r'Duplicate entry')

CREATE_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS %s (
        objectid text not null primary key,
        starttime date not null,
        endtime date null,
        min_lat real null,
        max_lat real null, 
        min_lon real null,
        max_lon real null
)'''

INSERT_SQL_TMPL = '''INSERT OR IGNORE INTO %s (objectid, starttime)
VALUES (?, ?);'''

datasetName = 'CloudSat'
geolocName = 'CloudSat'

TRIGGER = 1000

dbFile = os.path.abspath(sys.argv[1])
urlCatalogUri = sys.argv[2]
objectidQuery = sys.argv[3]

#connection for urlCatalog db
urlConn = create_engine(urlCatalogUri).connect()

#connection for sqlite db
conn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(CREATE_TABLE_SQL % geolocName)
#cursor.fetchall()

#get objectids
objectids = []
res = urlConn.execute("SELECT objectid FROM urls WHERE objectid LIKE '%s'" % objectidQuery)
objectids = [row['objectid'] for row in res]

count = 0
for objectid in objectids:
    match = CS_RE.search(objectid)
    if not match:
        print "Failed to match %s. Skipping." % objectid
        continue

    #get date
    dt = datetime.strptime("%s %s %s:%s:%s" % match.groups(), 
                           "%Y %j %H:%M:%S")

    cursor.execute(INSERT_SQL_TMPL % geolocName, (objectid, dt))
    print "Indexed %s" % objectid

    count+= 1
    if count >= TRIGGER:
        conn.commit()
        count = 0

conn.commit()
conn.close() 
