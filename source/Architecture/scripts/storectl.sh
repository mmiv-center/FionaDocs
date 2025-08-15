#!/usr/bin/env bash
: '
storectl.sh
===========

Start the service class provider (SCP) for the storage service class. DICOM files received this way will be stored in ``/data/site/archive/``. This service will also announce each incoming image to processSingleFile3.py using a pipe. Processed files will appear in ``/data/site/raw`` and ``/data/site/participant`` as symbolic link sorted by study/patient and image series with JSON summary files on a series level.


- user: processing
- depends-on:

  - ``/data/config/config.json``,
  - ``storescpFIONA``,
  - ``receiveSingleFile.sh``,
  - ``processSingleFile3.py``,
  - ``heartbeat.sh`` will try to contact the DICOM listener and restart this service in case of error

- log-file:

  - ``${SERVERDIR}/logs/storescpd${projname}.log``,
  - ``${SERVERDIR}/logs/storescpd-start.log``

- pid-file: ``${SERVERDIR}/.pids/storescpd${projname}.pid``
- start:

   .. code-block:: bash

      */10 * * * * env USER=$LOGNAME /var/www/html/server/bin/storectl.sh start >> /var/www/html/server/logs/storectl.log 2>&1

Notes
-----

This system service will stop if a control file /data/enabled exists and its first character is a "0".

' #end-doc



if [[ $USER !=  "processing" ]]; then
   echo "[$(date)] : This script must be run from the processing user account"
   exit 1
fi


SERVERDIR=`dirname "$(readlink -f "$0")"`/../

DATADIR=`cat /data/config/config.json | jq -r ".DATADIR"`
# if datadir has not be set in config
if [ "$DATADIR" == "null" ]; then
   echo "`date +'%Y-%m-%d %H:%M:%S'`: no datadir set in config file, assume ABCD default directory /data/"
   DATADIR="/data"
fi


port=`cat /data/config/config.json | jq -r ".DICOMPORT"`
pidfile=${SERVERDIR}/.pids/storescpd.pid
pipe=/tmp/.processSingleFilePipe

projname="$2"
if [ -z "$projname" ]; then
    projname="ABCD"
else
    if [ "$projname" != "ABCD" ]; then
	DATADIR=`cat /data/config/config.json | jq -r ".SITES.${projname}.DATADIR"`
	port=`cat /data/config/config.json | jq -r ".SITES.${projname}.DICOMPORT"`
	pidfile=${SERVERDIR}/.pids/storescpd${projname}.pid
	pipe=/tmp/.processSingleFilePipe${projname}
    fi
fi
ARRIVEDDIR=${DATADIR}/site/.arrived

#echo $projname
#echo $DATADIR
#echo $port

od="${DATADIR}/site/archive"

scriptfile=${SERVERDIR}/bin/receiveSingleFile.sh

export DCMDICTPATH=/usr/share/dcmtk/dicom.dic

#
# the received file will be written to a named pipe which is evaluated by processSingleFile.py
#
case $1 in
    'start')
        if [[ -f ${DATADIR}/config/enabled ]] && [[ -r ${DATADIR}/config/enabled ]]; then
           v=`cat ${DATADIR}/config/enabled | head -c 1`
           if [[ "$v" == "0" ]]; then
              echo "`date +'%Y-%m-%d %H:%M:%S'`: service disabled using ${SERVERDIR}/config/enabled control file" >> ${SERVERDIR}/logs/storescpd${projname}.log
              echo "`date +'%Y-%m-%d %H:%M:%S'`: service disabled using ${SERVERDIR}/config/enabled control file"
              exit
           fi
        fi

        if [ ! -d "$od" ]; then
          mkdir $od
        fi
        # check if we have a pipe to send events to
        if [[ "$(/usr/bin/test -p ${pipe})" != "0" ]]; then
            echo "`date +'%Y-%m-%d %H:%M:%S'`: Found pipe ${pipe}..."
        else
            echo "`date +'%Y-%m-%d %H:%M:%S'`: Error: the pipe of processSingleFile.py \"$pipe\" could not be found for ${projname}"
            exit -1
        fi
        echo "`date +'%Y-%m-%d %H:%M:%S'`: Check if storescp daemon is running..."
        /usr/bin/pgrep -f -u processing "storescpFIONA .*${port}" 2>&1 > /dev/null
        RETVAL=$?
        [ $RETVAL = 0 ] && exit || echo "`date +'%Y-%m-%d %H:%M:%S'`: storescpd process not running, start now.."
        echo "`date +'%Y-%m-%d %H:%M:%S'`: Starting storescp daemon..."
        echo "`date +'%Y-%m-%d %H:%M:%S'`: we try to start storescp by: /usr/bin/nohup /var/www/html/server/bin/storescpFIONA --fork --promiscuous --write-xfer-little --exec-on-reception \"$scriptfile '#a' '#c' '#r' '#p' '#f' &\" --sort-on-study-uid scp --output-directory \"$od\" $port &>${SERVERDIR}/logs/storescpd.log &" >> ${SERVERDIR}/logs/storescpd-start.log
	# set the LD_LIBRARY_PATH to make this work on Ubuntu
	export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/var/www/html/server/bin/backage
        DCMDICTPATH=/usr/share/dcmtk/dicom.dic /usr/bin/nohup /var/www/html/server/bin/storescpFIONA -v --fork \
	    --aetitle FIONA \
	    --datadir ${ARRIVEDDIR} \
	    --datapipe ${pipe} \
	    --promiscuous \
	    --write-xfer-little \
            --exec-on-reception "PleaseLookAtThis '#a' '#c' '#r' '#p' '#f'" \
            --sort-on-study-uid scp \
            --output-directory "$od" \
            $port >> ${SERVERDIR}/logs/storescpd${projname}.log 2>&1  &
	# new options
	#             --accept-all
        #             --write-xfer-same

        pid=$!
        echo $pid > $pidfile
        ;;
    'stop')
        #/usr/bin/pkill -F $pidfile
        /usr/bin/pkill -u processing "storescpFIONA .*${port}"
        RETVAL=$?
        # [ $RETVAL -eq 0 ] && rm -f $pidfile
        [ $RETVAL = 0 ] && rm -f ${pidfile}
        ;;
    *)
        echo "usage: storescpd { start | stop }"
        ;;
esac
exit 0
