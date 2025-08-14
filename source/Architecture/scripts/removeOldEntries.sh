#!/bin/bash
: '
removeOldEntries.sh
===================

The Assign application keeps a jobs file /var/www/html/applications/Assign/incoming.txt around with job entries. This script will remove entries from that list if they are older than 7 days. If studies are send again they will appear again in incoming.txt.

- user: processing
- depends-on:
  - /var/www/html/applications/Assign/incoming.txt
- log-file:
  - ${SERVERDIR}/logs/removeOldEntries.log
- pid-file: ${SERVERDIR}/.pids/removeOldEntries.pid
- start: 
  2 */4 * * * /usr/bin/flock -n /home/processing/.pids/removeOldEntries.pid /var/www/html/applications/Assign/php/removeOldEntries.sh >> /home/processing/logs/removeOldEntries.log 2>&1

Note
----

This will not remove such studies from FIONA, it will only make them inaccessible by Assign. They will be deleted if there is not enough space left on the data partition.


' #end-doc

# 7*60*24*60
#oldtime=86400
oldtime=604800

echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [removeOldEntries.sh] Start removing old entries from incoming.txt"
keep=""
tfile="/tmp/.tfile"
# set file to 0 size
echo -n "" > "${tfile}"
chmod 777 "${tfile}"
# append ok entries to that file
while read line
do
    #echo "${line}"
    sft=`echo ${line} | cut -d' ' -f1`
    if [ "$(( $(date +"%s") - $sft ))" -lt "$oldtime" ]; then
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [removeOldEntries.sh] keep ${line}, seconds is: $(( $(date +"%s") - $sft ))"
	echo "$line" >> ${tfile}
    else
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [removeOldEntries.sh] remove, file is older than $oldtime seconds (${sft})."
    fi
done <<< "$(cat /var/www/html/applications/Assign/incoming.txt)"
# now overwrite the incoming file again (atomic)
mv "$tfile" /var/www/html/applications/Assign/incoming.txt
chmod 777 /var/www/html/applications/Assign/incoming.txt

echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [removeOldEntries.sh] Done"
