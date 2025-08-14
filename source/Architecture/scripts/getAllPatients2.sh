#!/bin/bash
: '
getAllPatients2.sh
==================

Populate the WhatIsInIDS7 table in REDCap for a specific project using findscu. This script is part of a sequence of scripts: getAllPatients2.sh - parseAllPatients.sh - whatIsInIDS7.py.

- user: processing
- depends-on:
  - /tmp/parseAllPatients{projname}/
  - /tmp/pullStudies{projname}/
- log-file:
  - ${SERVERDIR}/logs/whatIsInIDS7{projname}.log,
- pid-file: ${SERVERDIR}/.pids/whatIsInIDS7{projname}.pid
- start: 
  */48 * * * * /usr/bin/flock -n /home/processing/.pids/getAllPatients2{projname}.pid /bin/bash -c "/home/processing/bin/utils/getAllPatients2.sh 10000 "{proejct}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1 \
  && /home/processing/bin/utils/parseAllPatients.sh "{projname}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1 \
  && /home/processing/bin/utils/whatIsInIDS7.py "{projname}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1"


Notes
-----

We can provide an argument to this program, the maximum number of days we would like to pull. In general we might get away with a very short period because new scans will come in as recent scans. But some test data migth be very old. So we should do one long run at night and short runs during the day.

As a second argument allow a specific project name. 

TODO: This runs too long. Treat some project as special here.

' #end-doc


numberOfDays=7000
InstitutionName=""
if [ "$#" -eq 1 ]; then
    numberOfDays="$1"
fi
if [ "$#" -eq 2 ]; then
    # use first argument as number of days
    numberOfDays="$1"
    # second argument as InstitutionName
    InstitutionName="$2"
fi
if [ "$#" -eq 0 ]; then
   echo "Usage: <days since today> [<project name>]"
fi

  
# store the result in the following folder:
od="/tmp/allPatients${InstitutionName}"
if [ ! -d "$od" ]; then
    mkdir "$od"
else
    # clear the directory
    \rm -fR "${od}/"
    mkdir "$od"
fi

containsElement () {
    local e match="$1"
    shift
    for e; do [[ "$e" == "$match" ]] && return 0; done
    return 1
}

# IF we are trying to get stuff for individual projects, can we speed up the
# pull of patients? Let try to get them all at once for one project, only
# if that does not work we can try with individual month or individual days.
if [ ! -z "${InstitutionName}" ]; then
    # try to get all at once, no dates
    
    DCMDICTPATH="/usr/share/dcmtk/dicom.dic"
    mkdir "${od}/all_at_once"
    name_site="-k \"(0008,0080)=${InstitutionName}\""
    #echo "/usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID\" ${name_site} -od \"${od}/all_at_once\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'"
    res=`/usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k "0008,0052=STUDY" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientID" -k "InstitutionName=${InstitutionName}" -od "${od}/all_at_once" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'`
    echo "$res" | grep -q " Received Final Find Response (Success)"
    if [ "$?" -ne "0" ]; then
	sleep 0.5
	# we got an error, handle below in the script
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] ERROR failed to pull all patients at once using findscu for project ${InstitutionName}. Trying to pull patients in 10 groups next"
	#echo "Try to pull patients in 10 groups (assume patient names end with numbers)"
	for ((i=0; i<10; i++)); do
	    mkdir -p "${od}/all_at_once${i}"
	    pat_name="*${i}"
	    #echo "export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840"
	    sleep 0.1
	    cmd="export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'"
	    #echo "${cmd}"
	    res=$(eval "${cmd}")
	    echo "$res" | grep -q " Received Final Find Response (Success)"
	    if [ "$?" -ne "0" ]; then
		echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] failed to pull all patients based on numbers as last characters (${pat_name}) for project ${InstitutionName}. Try with 10 more groups"
		for ((j=0; j<10; j++)); do
		    mkdir -p "${od}/all_at_once${j}${i}"
		    pat_name="*${j}${i}"
		    #echo "export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840"
		    sleep 0.1
		    cmd="export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${j}${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'"
		    #echo "${cmd}"
		    res=$(eval "${cmd}")
		    #res=`export DCMDICTPATH="${DCMDICTPATH}"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k "0008,0052=STUDY" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientID=${pat_name}" ${name_site} -od "${od}/all_at_once${i}" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'`
		    echo "$res" | grep -q " Received Final Find Response (Success)"
		    if [ "$?" -ne "0" ]; then
			echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] failed to pull all patients based on numbers as last characters (${pat_name}) for project ${InstitutionName}"
			for ((k=0; k<10; k++)); do
			    mkdir -p "${od}/all_at_once${k}${j}${i}"
			    pat_name="*${k}${j}${i}"
			    #echo "export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840"
			    sleep 0.4
			    cmd="export DCMDICTPATH=\"${DCMDICTPATH}\"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k \"0008,0052=STUDY\" -k \"(0010,0020)\" -k \"(0010,0040)\" -k \"(0020,1200)\" -k \"PatientID=${pat_name}\" ${name_site} -od \"${od}/all_at_once${k}${j}${i}\" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'"
			    #echo "${cmd}"
			    res=$(eval "${cmd}")
			    #res=`export DCMDICTPATH="${DCMDICTPATH}"; /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k "0008,0052=STUDY" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientID=${pat_name}" ${name_site} -od "${od}/all_at_once${i}" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'`
			    echo "$res" | grep -q " Received Final Find Response (Success)"
			    if [ "$?" -ne "0" ]; then
				echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] ERROR (final) failed to pull all patients based on numbers as last characters (${pat_name}) for project ${InstitutionName}"
				#echo "Error: $res"
			    else
				OIFS="$IFS"
				IFS=$'\n'
				for f in $( find "${od}/all_at_once${k}${j}${i}/" -type f ); do
  				    #for f in "${od}/all_at_once${k}${j}${i}/"*; do
				    fff=`basename $f`
				    if [ -n "$(ls -A "$f" 2>/dev/null)" ]; then
					cp -- "$f" "${od}/all_at_once/${k}${j}${i}_$fff"
				    fi
				done
				IFS="$OIFS"
			    fi
			done
		    else
			OIFS="$IFS"
			IFS=$'\n'
			for f in $( find "${od}/all_at_once${j}${i}/" -type f ); do
  			    #for f in "${od}/all_at_once${j}${i}/"*; do
			    fff=`basename $f`
			    cp -- "$f" "${od}/all_at_once/${j}${i}_$fff"
			done
			IFS="$OIFS"
		    fi
		done
	    else
		OIFS="$IFS"
		IFS=$'\n'
		for f in $( find "${od}/all_at_once${i}/" -type f ); do
  		    #for f in "${od}/all_at_once${i}/"*; do
		    fff=`basename $f`
		    cp -- "$f" "${od}/all_at_once/${i}_$fff"
		done
		IFS="$OIFS"
	    fi
	done	
    fi
    # it worked, we are done
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] done with getAllPatients2.sh for project ${InstitutionName}, number of days ${numberOfDays}, data in ${od}/all_at_once"
    exit 0
fi

# we would like to pull all studies, maybe we do this by time?
# Here 2020/1990=30  *356=11,000
# I would like to be able to delete data in the WhatIsInIDS7 project on REDCap,
# right now the easiest way to do this is to use REDCaps erase all data function.
count="-100"
while [ $count -le $numberOfDays ]
do
    da=`date --date="${count} days ago" +%Y%m%d`
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] testing date $da"
    DCMDICTPATH=/usr/share/dcmtk/dicom.dic
    mkdir "${od}/$da"
    name_site=""
    if [ ! -z "$InstitutionName" ]; then
	name_site="-k \"InstitutionName=${InstitutionName}\""
    fi
    res=`/usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k "0008,0052=STUDY" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientID" -k "StudyDate=$da" ${name_site} -od "${od}/$da" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 2>&1 | tr -d '\n'`
    echo "$res" | grep -q " Received Final Find Response (Success)"
    if [ "$?" -ne "0" ]; then
	# In case we received a "Received Final Find Response (Failed: UnableToProcess)"
	# we want to query again with added patient IDs so we can find out cases where
	# a single day has too many scans for findscu to list.
	declare -a searches
	searches=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 ^)
	for i in "${searches[@]}"; do
	    mkdir "${od}/${da}_${i}"
	    DCMDICTPATH=/usr/share/dcmtk/dicom.dic
	    /usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --study -k "0008,0052=STUDY" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientID=*${i}" -k "StudyDate=$da" -od "${od}/${da}_${i}" -X +sr --repeat 2 vir-app5274.ihelse.net 7840 > /dev/null 2>&1
	    files=$(shopt -s nullglob dotglob; echo ${od}/${da}_${i}/*)
	    if (( ${#files} ))
	    then
		echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] found a file in ${od}/${da}_${i}/"
	    else
		# remove this directory again to make output cleaner - only show dates that contain values
		\rm -fR "${od}/${da}_${i}"
	    fi
	    sleep 0.2
	done
    fi
    # only if we have some files in that directory keep it around
    files=$(shopt -s nullglob dotglob; echo ${od}/${da}/*)
    if (( ${#files} ))
    then
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [getAllPatients2.sh] found a file in ${od}/${da}/"
    else
	# remove this directory again to make output cleaner - only show dates that contain values
	\rm -fR "${od}/${da}"
    fi
    sleep 0.2
    count=$[$count + 1]
done


# get a list of all patient names
#declare -a searches
#searches=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 ^ "NAKKE 0" "NAKKE 1" "NAKKE 2" "NAKKE 3" "NAKKE 4" "NAKKE 5" "NAKKE 6" "NAKKE 7" "NAKKE 8" "NAKKE 9")
# append to these all other searches again
#searchSecondLevel=(N "NAKKE 0" "NAKKE 1" "NAKKE 2" "NAKKE 3" "NAKKE 4" "NAKKE 5" "NAKKE 6" "NAKKE 7" "NAKKE 8" "NAKKE 9")
#searches=(A B)
#for i in "${searches[@]}"; do
#    DCMDICTPATH=/usr/share/dcmtk/dicom.dic
#    if containsElement "${i}" "${searchSecondLevel[@]}"; then#
	# loop a second time over all searches and do a sub-se#arch for each - should result in less answers, but is this sufficient for large projects?
#	for j in "${searches[@]}"; d#o
#            mkdir "${od}/$i$j#"
#	    /usr/bin/findscu #-v -aet FIONA -aec DICOM_QR_SCP --patient -k "0008,0052=PATIENT" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientName=${i}${j}*" -od "${od}/$i$j" -X +sr --repeat 2 vir-app5274.ihelse.net 784#0#####
#	done
#    else
#        mkdir "${od}/$i"
#	/usr/bin/findscu -v -aet FIONA -aec DICOM_QR_SCP --patient -k "0008,0052=PATIENT" -k "(0010,0020)" -k "(0010,0040)" -k "(0020,1200)" -k "PatientName=${i}*" -od "${od}/$i" -X +sr --repeat 2 vir-app5274.ihelse.net 7840
#    fi
#    sleep 1
#done
