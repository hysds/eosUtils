#!/bin/bash 
source $HOME/sciflo/etc/sciflo-env.sh

CS_USER=$1
CS_PWD=$2
EMAIL=$3
USER=$4
WEATHER=$5

function sendErrorEmail {
    mail -s "$0: $1" $EMAIL < $SCIFLO_DIR/log/updateDaily.log
    exit 1
}

#get current year
YEAR=`date +%Y`

#############################################################
#crawler section
#############################################################
#sync current year's CloudSat granules from CDAAC and unzip to be ready to be crawled
echo "Syncing year $YEAR CloudSat data..."
for ds in `echo 2B-GEOPROF.R04 2B-GEOPROF-LIDAR.P2.R04 2B-CLDCLASS.R04 2B-CWC-RO.R04`; do
  ds_dir=$SCIFLO_DIR/share/sciflo/data/sensors/atrain/cloudsat/${ds}
  year_dir=${ds_dir}/${YEAR}
  mkdir -p $year_dir
  wget --mirror --user=$CS_USER --password=$CS_PWD -np -nv -nH --cut-dirs=1 \
    --directory-prefix=${ds_dir} \
    ftp://ftp1.cloudsat.cira.colostate.edu/${ds}/${YEAR} #|| sendErrorEmail 'Sync CloudSat data'

  #extract files if they don't exist
  for doy in ${year_dir}/???; do
    for zipFile in ${doy}/*.zip; do
      unzip -n -d ${doy} $zipFile #|| sendErrorEmail 'Unzip CloudSat data'
    done
  done

done
echo "Syncing year $YEAR CloudSat data...done."

#get urls catalogs on weather, scp, and untar to for crawler
echo "Retrieving AIRS catalogs from weather..."""
rm -f $HOME/tmp/catalogs.tbz2 $HOME/tmp/*_catalog.txt
ssh ${USER}@${WEATHER} ./write_catalogs_current_year.sh
scp ${USER}@${WEATHER}:catalogs.tbz2 $HOME/tmp/
tar xvfj $HOME/tmp/catalogs.tbz2 -C $HOME/tmp/
echo "Retrieving AIRS catalogs from weather...done."""

#crawl
echo "Crawling year $YEAR for all configured datasets..."
for i in $SCIFLO_DIR/etc/crawler/cron/daily/*.xml; do
  BASEFILE=`basename $i`
  TMPFILE=/tmp/$BASEFILE.$$
  sed "s#__SUBDIR__#$YEAR#g" $i > $TMPFILE
  $SCIFLO_DIR/bin/crawlAll.py $TMPFILE || sendErrorEmail $TMPFILE
  rm -f $TMPFILE
done
echo "Crawling year $YEAR for all configured datasets...done."

#############################################################
#eosUtils (AIRS & CloudSat metadata update) section
#############################################################
#sync current year's AIRS metadata
echo "Syncing year $YEAR AIRS metadata..."
wget --mirror -nv -np -nH -A *.hdf.xml --directory-prefix=$HOME/dev/eosUtils/scripts/airs_xml --cut-dirs=5 ftp://airspar1u.ecs.nasa.gov/ftp/data/s4pa/Aqua_AIRS_Level2/AIRX2RET.005/$YEAR || sendErrorEmail 'Sync AIRS metadata'
echo "Syncing year $YEAR AIRS metadata...done."

#update AIRS sqlite db
echo "Updating sqlite db for year $YEAR AIRS metadata..."
$HOME/dev/eosUtils/scripts/updateSqlite_AIRS.py $HOME/sciflo/sqlite_data/AIRS.db $HOME/dev/eosUtils/scripts/airs_xml/$YEAR || sendErrorEmail 'Update AIRS sqlite'
echo "Updating sqlite db for year $YEAR AIRS metadata...done."

#update CloudSat sqlite db (uses crawled urls to generate CloudSat metadata)
echo "Updating sqlite db for year $YEAR CloudSat metadata..."
$HOME/dev/eosUtils/scripts/updateSqlite_CloudSat.py $HOME/sciflo/sqlite_data/CloudSat.db 'mysql://root:sciflo@127.0.0.1:3306/urlCatalog' "${YEAR}%%_CS" || sendErrorEmail 'Update CloudSat sqlite'
echo "Updating sqlite db for year $YEAR CloudSat metadata...done."

#send log
sendErrorEmail 'Updated AIRS and CloudSat metadata and urls'
