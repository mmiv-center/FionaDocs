#!/bin/bash
# remove any old entries from incoming.txt

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
