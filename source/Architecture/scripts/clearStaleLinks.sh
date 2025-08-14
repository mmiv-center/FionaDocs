#!/bin/bash
: '
clearStaleLinks.sh
==================

Delete links that do not point to real images in archive.

Just to be sure we have a clear /data/site/raw folder we remove broken symbolic link and empty folders.

- user: processing
- depends-on:
  - /data/site/raw
- log-file:
  - ${SERVERDIR}/logs/clearStaleLinks.log
- pid-file: ${SERVERDIR}/.pids/clearStaleLinks.pid
- start: 
  2 3 * * * /usr/bin/flock -n /home/processing/.pids/clearStaleLinks.pid /home/processing/bin/clearStaleLinks.sh >> /home/processing/logs/clearStaleLinks.log 2>&1


' #end-docs


echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] start clearStaleLinks"
dirs=(/data/site/raw/ /data/site/participants/ /data/site/srs/)
for dir in "${dirs[@]}"; do
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Work on ${dir}..."
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Delete symbolic links pointing to no archive files..."
    find "${dir}" -type l ! -exec test -e {} \; -exec rm {} \;
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Deleting empty directories..."
    find "${dir}" -empty -type d -delete
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Deleting .json files for empty directories..."
    find "${dir}" -type f -name "*.json" -print0 | while read -d $'\0' file; do a="$file"; ! test -d "${a%%.json}" && rm -rf "${file}"; done
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Deleting empty directories..."
    find "${dir}" -empty -type d -delete
done
echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [clearStaleLinks.sh] Done"
