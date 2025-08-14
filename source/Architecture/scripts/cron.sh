#!/bin/bash
: '
cron.sh
========

System service for the ASTTT service of the profile page on FIONA. Sends out emails if data arrives for projects the user is a member off. 

- user: processing
- depends-on:
  - /var/www/html/applications/User/asttt/
- log-file:
  - ${SERVERDIR}/logs/User_asttt.log
- pid-file: ${SERVERDIR}/.pids/User_asttt.pid
- start: 
  */30 * * * * /usr/bin/flock -n /home/processing/.pids/User_asttt.pid /var/www/html/applications/User/asttt/code/cron.sh >> /home/processing/logs/User_asttt.log 2>&1

' #end-doc


# read in all the links as separate lines
data=`jq -c ".[]" /var/www/html/applications/User/asttt/code/links.json`

triggers=`ls -d /var/www/html/applications/User/asttt/code/events/*`
actions=`ls -d /var/www/html/applications/User/asttt/code/actions/*`

while IFS= read -r line ; do
    # now for each line call the trigger to find out if we should call the event
    event=`echo $line | jq -r ".event"`
    action=`echo $line | jq -r ".action"`
    user=`echo $line | jq -r ".user"`
    id=`echo $line | jq -r ".id"`
    param=`echo $line | jq -r ".action_param[]"`
    while IFS= read -r line2 ; do
        name=`cat ${line2}/info.json | jq -r ".name"`

        if [ "$name" == "$event" ]; then
            script=${line2}/`cat ${line2}/info.json | jq -r ".script"`
            # echo "trigger is defined in ${line2}/info.json, call script \"${script}\" with ${line}"
            ret=`eval "${script} '${line}'"`

            if [ "$?" -eq "1" ]; then
                echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [cron.sh] action will be performed"
                # what action?
                while IFS= read -r line3 ; do
                    name=`cat ${line3}/info.json | jq -r ".name"`
		    echo $name
                    if [ "$name" == "$action" ]; then
                        script2=${line3}/`cat ${line3}/info.json | jq -r ".script"`
			process_dir=`mktemp -d -t asst_cronXXXXX`
                        echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [cron.sh] action is defined in ${line3}/info.json, call script \"${script2}\" with ${line}"
			# any output is expected to be in the process_dir directory
                        ret2=`eval "${script2} '${line}' '${process_dir}'" 2>> ${script2}_log`
                        echo "${ret2}"
			if [ -e "${process_dir}/email.txt" ]; then
                            # The output ret2 should now be send as an email to the current user
                            # cat "${process_dir}/email.txt" | /var/www/html/applications/User/asttt/code/sendAsEmail.sh "${user}" "${action} (${param})" -
			    attachment="none"
			    if [ -e "${process_dir}/attachment.csv" ]; then
				attachment="${process_dir}/attachment.csv"
			    fi
			    /var/www/html/applications/User/asttt/code/sendAsEmail.sh "${user}" "${action} (${param})" "${process_dir}/email.txt" "$attachment"
			fi
			# Delete the directory afterwards again
			
                    fi
                done <<< "$actions"
            fi
            #echo "trigger returned: $ret"
        fi
    done <<< "$triggers"
done <<< "$data"
