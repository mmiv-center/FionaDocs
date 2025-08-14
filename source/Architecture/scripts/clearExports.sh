#!/usr/bin/env bash
: '
clearExports.sh
===============

Delete old entries in the /export2/Export/ folder (temporary folders older than 1000 minutes, requires permissions for processing user) and the oldest created zip files in /export2/Export/files/ until at least 90% of space is available on this partition.

- user: processing
- depends-on:
  - /export2/Export/files/
  - /export2/Export/tmp_*
- log-file:
  - ${SERVERDIR}/logs/clearExports.log
- pid-file: ${SERVERDIR}/.pids/clearExports.pid
- start: 
  0 23 * * 3,6 /usr/bin/flock -n /home/processing/.pids/clearExports.pid /home/processing/bin/clearExports.sh >> /home/processing/logs/clearExports.log 2>&1


' #end-doc



echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearExports.sh] Start deleting export files"

# start by deleting old directories that start with tmp_ (leftovers)
# the time is in minutes, this might take a long time if we have large research studies
find /export2/Export/ -mindepth 1 -maxdepth 1 -name "tmp_*" -type d -cmin +1000 | xargs rm -rf

# how much free space
filled=0
freeSpace() {
  fs=`df -h /export2/Export/files | tail -1 | awk -e '{ print($5) }'`
  filled="${fs%%\%}"
}

declare -a sops

# fill in all files based on age (oldest first)
OLDIFS=$IFSN
IFS=$'\n'
sops=($(find /export2/Export/files/ -mindepth 1 -maxdepth 1 -type f -name \*.zip -printf '%T+ %p\n' | sort))
IFS=$OLDIFS

# loop through and remove until freeSpace returns something smaller than 80 (percent)
threshold=90
c=0
for i in "${sops[@]}"; do
    #echo "i is: ${i}"
    freeSpace
    #echo $filled
    if [ "$filled" -le $threshold ]; then
	## skip out
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearExports.sh] sufficient space on /files after deleting $c directories in /export2/Export/files"
	break;
    fi
    # delete now
    p=`echo "${i}" | cut -d' ' -f2-`
    d="${p}"
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearExports.sh] delete zip file $c: $d $filled"
    # we should also remove the corresponding directory in raw
    \rm -f "${d}"
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
echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearExports.sh] Done"
