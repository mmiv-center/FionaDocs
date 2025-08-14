#!/usr/bin/env bash
: '
clearOldFiles.sh
================

Delete the oldest files until we have at least 20% free space on the data partition. This ensures that we can always receive new data on FIONA. Existing data that is not assigned (Assign) to a research project will be deleted.

- user: processing
- depends-on:
  - /data/site/archive
- log-file:
  - ${SERVERDIR}/logs/clearOldFiles.log
- pid-file: ${SERVERDIR}/.pids/clearOldFiles.pid
- start: 
  30 * * * * /usr/bin/flock -n /home/processing/.pids/clearOldFiles.pid /home/processing/bin/clearOldFiles.sh >> /home/processing/logs/clearOldFiles.log 2>&1


Notes
-----

TODO: delete links in /data/site/participants/
TODO: delete links in /data/site/srs/

' #end-doc


echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearOldFiles.sh] Start"

# how much free space
filled=0
freeSpace() {
  fs=`df -h /data/ | tail -1 | awk -e '{ print($5) }'`
  filled="${fs%%\%}"
}

declare -a sops

# fill in all files based on age (oldest first)
OLDIFS=$IFSN
IFS=$'\n'
sops=($(find /data/site/archive/ -mindepth 1 -maxdepth 1 -type d -printf '%T+ %p\n' | sort))
IFS=$OLDIFS

# loop through and remove until freeSpace returns something smaller than 80 (percent)
threshold=80
c=0
for i in "${sops[@]}"; do
    #echo "i is: ${i}"
    freeSpace
    if [ "$filled" -le $threshold ]; then
	# skip out
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearOldFiles.sh] [INFO] sufficient space on /data after deleting $c directories in /data/site/archive"
	break;
    fi
    # delete now
    p=`echo "${i}" | cut -d' ' -f2-`
    d="${p}"
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearOldFiles.sh] delete directory $c: $d $filled"
    # we should also remove the corresponding directory in raw
    \rm -rf "${d}"
    uid=`echo "${p}" | cut -d'_' -f2-`
    if [ ! -z "${uid}" ]; then
	if [ -d "/data/site/raw/${uid}" ]; then
	    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearOldFiles.sh] delete directory /data/site/raw/${uid}/"
	    \rm -rf "/data/site/raw/${uid}/"
	fi
    fi
    c=$(($c+1))
done

# Just to be sure we have a clear /data/site/raw folder
# we should remove broken symbolic link and empty
# folders.
#echo "Delete symbolic links pointing to no archive files..."
#find /data/site/raw/ -type l ! -exec test -e {} \; -exec rm {} \;
#echo "Deleting empty directories..."
#find /data/site/raw -empty -type d -delete
#echo "Deleting .json files for empty directories..."
#find /data/site/raw/ -type f -name "*.json" -print0 | while read -d $'\0' file; do a="$file"; ! test -d "${a%%.json}" && rm -rf "${file}"; done
#echo "Deleting empty directories..."
#find /data/site/raw -empty -type d -delete
echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearOldFiles.sh] Done"
