#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

# kick off processes from the database to update ite
sudo -i -u postgres psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'amazon' AND pid <> pg_backend_pid();"
sudo -i -u postgres psql -c "DROP DATABASE amazon;"

datadir="${1:-data/}"
if [ ! -d $datadir ] ; then
    echo "$datadir does not exist under $mybase"
    exit 1
fi

source ../.flaskenv
dbname=$DB_NAME

if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    dropdb $dbname
fi
createdb $dbname

psql -af create.sql $dbname
cd $datadir
psql -af $mybase/load.sql $dbname
psql -af $mybase/views.sql $dbname
psql -af $mybase/triggers.sql $dbname
