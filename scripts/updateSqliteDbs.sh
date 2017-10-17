#!/bin/sh
source $HOME/sciflo/etc/sciflo-env.sh

cd $HOME/dev/eosUtils/scripts

#MODIS-Terra:
wget -N -r -l inf --no-remove-listing --no-use-server-timestamps -c --tries=3 --waitretry=3 -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/6/TERRA
python allGranulesImportDb_sqlite.py MODIS-Terra $HOME/sciflo/sqlite_data/MODIS-Terra.db $HOME/dev/eosUtils/scripts/ladsweb.nascom.nasa.gov/geoMeta/TERRA

#MODIS-Aqua:
wget -N -r -l inf --no-remove-listing --no-use-server-timestamps -c --tries=3 --waitretry=3 -nv ftp://ladsweb.nascom.nasa.gov/geoMeta/6/AQUA
python allGranulesImportDb_sqlite.py MODIS-Aqua $HOME/sciflo/sqlite_data/MODIS-Aqua.db $HOME/dev/eosUtils/scripts/ladsweb.nascom.nasa.gov/geoMeta/AQUA

#AIRS:
wget --mirror -nv -np -nH -A *.hdf.xml --directory-prefix=$HOME/dev/eosUtils/scripts/airs_xml --cut-dirs=5 ftp://airspar1u.ecs.nasa.gov/ftp/data/s4pa/Aqua_AIRS_Level2/AIRX2RET.006
python allGranulesImportDb_AIRS_sqlite.py $HOME/sciflo/sqlite_data/AIRS.db $HOME/dev/eosUtils/scripts/airs_xml
