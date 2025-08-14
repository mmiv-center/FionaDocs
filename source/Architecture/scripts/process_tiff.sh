#!/usr/bin/env bash
: '
process_tiff.sh
===============

Whole-slide image file upload the research PACS using the Attach application. The application supports two modes, a DICOM conversion (from wsi) and a direct copy of the wsi-files to a shared import folder for research PACS.

- user: processing
- depends-on:
  - /ifs/hvn/dma/forskning/pat/forskning_short/SPIS_Import/{projname}/
  - /var/www/html/applications/Attach/uploads_done/
  - /var/www/html/applications/Attach/uploads/
- log-file:
  - ${SERVERDIR}/logs/Pathology_process_tiff.log
- pid-file: ${SERVERDIR}/.pids/Pathology_process_tiff.pid
- start: 
  */1 * * * * /usr/bin/flock -n /home/processing/.pids/Pathology_process_tiff.pid /var/www/html/applications/Attach/process_tiff.sh >> /home/processing/logs/Pathology_process_tiff.log 2>&1


' #end-doc


# check if user is processing
if [ ! `whoami` = "processing" ]; then
    print "Error: should be run by user processing only"
    exit -1
fi



uploads_done_dir="/var/www/html/applications/Attach/uploads_done"
if [ ! -d "$uploads_done_dir" ]; then
    mkdir "${uploads_done_dir}"
fi

#echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: process_tiff.sh start..."

# pick the next json for processing
OIFS="$IFS"
IFS=$'\n'
# FYI: This loop will only process a single file and exit.
for json_file in $(find /var/www/html/applications/Attach/uploads -type f -name "*.json"); do
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] INFO: testing \"${json_file}\""
    start=$(date +%s)
    # now we process file
    image_file=`jq -r ".file" "${json_file}"`
    image_file="/var/www/html/applications/Attach/${image_file}"
    extension="${image_file##*.}"

    # change names to match the once in REDCap
    InstitutionName=`jq -r ".project_name" "${json_file}"`
    Event=`jq -r ".redcap_event_name" "${json_file}"`
    Participant=`jq -r ".record_id" "${json_file}"`
    Block=`jq -r ".patho_block_nr" "${json_file}"`
    Stain=`jq -r ".patho_stain" "${json_file}"`
    Biopsy=`jq -r ".patho_biopsy_nr" "${json_file}"`
    BiopsyID=`jq -r ".patho_biopsy_id" "${json_file}"`
    SlideID=`jq -r ".patho_slide_id" "${json_file}"`
    SlideNR=`jq -r ".patho_slide_nr" "${json_file}"`
    Specimen=`jq -r ".patho_specimen" "${json_file}"`
    REK=`jq -r ".patho_rek" "${json_file}"`
    Department=`jq -r ".patho_department" "${json_file}"`
    DatabaseID=`jq -r ".patho_databaseid" "${json_file}"`
    Path=`jq -r ".project_pat_import_folder" "${json_file}"`
    DoNotRemoveMacro=`jq -r ".do_not_remove_macro_image" "${json_file}"`
    Scanner=""
    ImageSizeX=""
    ImageSizeY=""
    Manufacturer=""
    AppMag=""
    Paramset=""
    Resolution=""
    if [[ "${extension}" == "svs" ]]; then
	Manufacturer="Aperio"
	# tiffinfo  'kidney_00729_00836_006524_007516_02_16_OUS_Toluidine blue.svs' | grep "ScanScope ID" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "ScanScope ID =" | cut -d'=' -f2 | head -1 | tr -d ' '
	Scanner=`tiffinfo "${image_file}" 2> /dev/null | grep "ScanScope ID" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "ScanScope ID =" | cut -d'=' -f2 | tr -d ' '`
	AppMag=`tiffinfo "${image_file}" 2> /dev/null | grep "AppMag" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "AppMag =" | cut -d'=' -f2 | tr -d ' '`
	Parmset=`tiffinfo "${image_file}" 2> /dev/null | grep "Parmset" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "Parmset =" | cut -d'=' -f2- | tr -d ' '`
	MPP=`tiffinfo "${image_file}" 2> /dev/null | grep "MPP" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "MPP =" | cut -d'=' -f2- | tr -d ' '`
	ScanDate=`tiffinfo "${image_file}" 2> /dev/null | grep "Date" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "Date =" | cut -d'=' -f2- | tr -d ' '`
	#ScanTime=`tiffinfo "${image_file}" 2> /dev/null | grep "Time" | head -1 | awk -F'|' '{for(i=2; i<=NF; i++) {print $i}}' | grep "Time =" | cut -d'=' -f2- | tr -d ' '`
	# add this information to the input json_file (for import into REDCap)
	/usr/bin/jq ". += { \"patho_scanner_model\": \"${Scanner}\", \"patho_scanner_manufacturer\": \"${Manufacturer}\", \"patho_app_mag\": \"${AppMag}\", \"patho_parmset\": \"${Parmset}\", \"patho_mpp\": \"${MPP}\", \"patho_scan_date\": \"${ScanDate}\" }" "${json_file}" > /tmp/tmp_added_scanner.json
	/bin/mv /tmp/tmp_added_scanner.json "${json_file}"
	# the scanner should now be visible in the uploaded json
	#   Image Width: 132327 Image Length: 43029 Image Depth: 1
	res=`tiffinfo "${image_file}" 2> /dev/null | grep "Image Width:" | head -1 | awk '{$1=$1;print}'`
	ImageSizeX=`echo "${res}" | cut -d':' -f2 | cut -d' ' -f2`
	ImageSizeY=`echo "${res}" | cut -d':' -f3 | cut -d' ' -f2`
	/usr/bin/jq ". += { \"patho_image_size_x\": \"${ImageSizeX}\", \"patho_image_size_y\": \"${ImageSizeY}\" }" "${json_file}" > /tmp/tmp_added_size.json
	/bin/mv /tmp/tmp_added_size.json "${json_file}"	
    elif [[ "${extension}" == "ndpi" ]]; then
	Manufacturer="Hamamatsu"
	# tiffinfo kidney_00036_00128_001199_002187_02_04_SOH_51567006.ndpi | grep "Product" | head -1 | cut -d'=' -f2
	Scanner=`tiffinfo "${image_file}" 2> /dev/null | grep "Product" | head -1 | cut -d'=' -f2 | tr -d '\r'`
	# the following two fields can be removed if we get the magnification from the openslide.mpp-x and openslide.mpp-y fields instead
	Resolution=`tiffinfo "${image_file}" 2> /dev/null | grep Resolution |awk '{$1=$1;print}' | sed -e 's/Resolution: //g' | tr '\n' '-'`
	ObjectiveLensMag=`tiffinfo "${image_file}" 2> /dev/null | grep "^Objective.Lens.Magnificant" | awk '{$1=$1;print}' | head -1 | cut -d'=' -f2 | tr -d '\r'`
	MPP=`tiffinfo "${image_file}" 2> /dev/null | grep Resolution |awk '{$1=$1;print"10000/"$0}' | sed -e 's/Resolution: //g' | cut -d',' -f1  | bc -l | sort -n | head -1`
	ScanDate=`tiffinfo "${image_file}" 2> /dev/null | grep "DateTime:" | sed -e 's/DateTime: //g' | head -1 | awk '{$1=$1;print}' | cut -d' ' -f1`
	# add this information to the input json_file (for import into REDCap)
	/usr/bin/jq ". += { \"patho_scanner_model\": \"${Scanner}\", \"patho_scanner_manufacturer\": \"${Manufacturer}\", \"patho_resolution\": \"${Resolution}\", \"patho_objective_lens_magnificant\": \"${ObjectiveLensMag}\", \"patho_mpp\": \"${MPP}\", \"patho_scan_date\": \"${ScanDate}\" }" "${json_file}" > /tmp/tmp_added_scanner.json
	/bin/mv /tmp/tmp_added_scanner.json "${json_file}"
	# the scanner should now be visible in the uploaded json

	# Image Width: 84224 Image Length: 45696
	# Resolution: 22614, 22614 pixels/cm
	res=`tiffinfo "${image_file}" 2> /dev/null | grep "Image Width:" | head -1 | awk '{$1=$1;print}'`
	ImageSizeX=`echo "${res}" | cut -d' ' -f3`
	ImageSizeY=`echo "${res}" | cut -d' ' -f6`
	# add this information to the input json_file (for import into REDCap)
	/usr/bin/jq ". += { \"patho_image_size_x\": \"${ImageSizeX}\", \"patho_image_size_y\": \"${ImageSizeY}\" }" "${json_file}" > /tmp/tmp_added_size.json
	/bin/mv /tmp/tmp_added_size.json "${json_file}"
    else
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Error: unknown file extension \"${extension}\". Scanner extraction only supported for svs and ndpi files"
    fi

    
    ExamId="${Participant}"
    LabId="${Department}"
    SlideN="${SlideNR}"
    ImageID="${SlideID}"
    # the Request ID seems to be mapped to the Participant ID
    # With the following we get some duplicate images (images are uploaded but do not appear)
    #RequestId="${Participant}_${Biopsy}_${DatabaseID}"
    # With this entry it seems to work, just bad that the participant ID contains the biopsy-ID.
    RequestId="${Participant}_${BiopsyID}"
    # Haukeland, Radiology at MMIV and Research and Innovation department, UiB Associated Prof. in Computer Science, Visualization grou, part of writing team for federated learning, 
    
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Path: ${Path}"
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] image_file: ${image_file}"

    if [ -n "$Path" ]; then
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Importing path based data - keep WSI format when adding to PACS"
	# We need to pseudonymize the imported file by changing the filename and the barcode.
	# Example:  docker run -it --rm --entrypoint /wsi-anon/bin/wsi-anon.out wsi_anon
	# No filename specified.
	#
	#Usage: bin/wsi-anon.out [FILE] [-OPTIONS]
	#
	#OPTIONS:
	#-c     Only check file for vendor format and metadata
	#-n     Specify pseudo label name (e.g. -n "labelname")
	#-m     If flag is set, macro image will NOT be deleted
	#-i     If flag is set, anonymization will be done in-place
	#-u     If flag is set, tiff directory will NOT be unlinked
	#
	#       Note: For file formats using JPEG compression this does not work currently.

	# create a shorter specimen name (if we use SNOMED style)
	if [[ "${Specimen}" == *"["* ]]; then
	    # remove the text
	    Specimen=$(echo "${Specimen}" | cut -d'[' -f 2 | cut -d']' -f 1)
	fi
	if [[ "${Stain}" == *"["* ]]; then
	    # remove the general name and remove trailing and leading spaces
	    Stain=$(echo "${Stain}" | cut -d']' -f 2 | awk '{$1=$1;print}')
	    Stain="${SlideN} ${Stain}"
	fi
	if [ -z "${Specimen}" ]; then
	    Specimen="unknown"
	fi
	if [ -z "${Stain}" ]; then
	    Stain="unknown"
	fi
	if [ -z "${Scanner}" ]; then
	    Scanner="unknown"
	fi
	
	# need to add all the fields below to make the name more unique
	new_name="${Specimen}_${Biopsy}_${SlideNR}_${ImageID}_${SlideN}_${RequestId}_${ExamId}_${LabId}_${Block}_${Department}_${Stain}"
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Suggested name is: ${new_name}"
	
	# import_json=$(basename "$image_file")
	import_json="${new_name}.${extension}"
	# the import file needs to keep the full filename including the extension .svs (make .svs.import)
	import_json_filename="${import_json}.import"
	full_path_import_json="${Path}/${import_json_filename}"
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] full_path: ${full_path_import_json}"
	jq -n \
	   --arg RequestId "$RequestId" \
	   --arg ExamId "$ExamId" \
	   --arg LabId "$LabId" \
	   --arg StainingName "$Stain" \
	   --arg SpecimenName "$Specimen" \
	   --arg BlockName "$Block" \
	   '{
	       "RequestId": $RequestId,
	       "ExamId": $ExamId,
               "LabId": $LabId,
               "Staining": { "Name": $StainingName },
               "Specimen": { "Name": $SpecimenName },
               "Block": { "Name": $BlockName }
    	   }' > "$full_path_import_json"

	input_fname=$(basename "${image_file}")
	# TODO: some projects might want to keep data imported as is. That means using the -m option.
	#
	#Usage: bin/wsi-anon.out [FILE] [-OPTIONS]
	#
	#OPTIONS:
	#  -c     Only check file for vendor format and metadata
	#  -n     Specify pseudo label name (e.g. -n "labelname")
	#  -m     If flag is set, macro image will NOT be deleted
	#  -i     If flag is set, anonymization will be done in-place
	#  -u     If flag is set, tiff directory will NOT be unlinked
	#
	#  Note: For file formats using JPEG compression this does not work currently.
	
	# this might fail (Error Could not find IFD of label image in Aperio format...)
	add_opt=""
	if [ "${DoNotRemoveMacro}" == "1" ]; then	    
	    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] INFO add option -m to wsi_anon"
	    add_opt=" -m "
	fi
	docker run --rm -v /var/www/html/applications/Attach/uploads:/data --entrypoint /wsi-anon/bin/wsi-anon.out wsi_anon:latest "/data/${input_fname}" ${add_opt} -n "${new_name}"
	# if the above worked we should have a new svs file in the uploads folder
	anonymized="${image_file}"
	if [ -e "/var/www/html/applications/Attach/uploads/${new_name}.${extension}" ]; then
	    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Found a new file at: /var/www/html/applications/Attach/uploads/${new_name}.${extension}"
	    anonymized="/var/www/html/applications/Attach/uploads/${new_name}.${extension}"
	else
	    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Error: could not find the output file after running: docker run --rm -v /var/www/html/applications/Attach/uploads:/data --entrypoint /wsi-anon/bin/wsi-anon.out wsi_anon:latest \"/data/${input_fname}\" -i -n \"${new_name}\""
	    anonymized="${image_file}"
	fi
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] cp \"${anonymized}\" \"${Path}/${new_name}.${extension}\""
	cp "${anonymized}" "${Path}/${new_name}.${extension}"

	# add the info to REDCap as well
	# ../process_tiff_importREDCap.py --importData kidney_00040_00133_001233_002221_02_05_SOH_117018006.json
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] /var/www/html/applications/Attach/process_tiff_importREDCap.py --importData \"${json_file}\""
	/var/www/html/applications/Attach/process_tiff_importREDCap.py --importData "${json_file}"

	#
	# We have one project who wants to keep a cache of the files around. They need to send those to
	# a third party soon. Instead of manually retrieving them from Sectra we can store them in a project
	# folder. For now, if the project folder exists make a copy.
	#
	copy_folder_location="/export2/Attach/project_cache/${InstitutionName}/"
	if [ -d "${copy_folder_location}" ]; then
	    echo "`date +'%Y-%m-%d %H-%M-%S.%06N'`: [process_tiff.sh] INFO found project_cache folder for \"${InstitutionName}\" in ${copy_folder_location}, copy json and image there."
	    upload_date=`date +'%Y-%m-%d-%H-%M'`
	    # We need write permissions here
	    mkdir -p "${copy_folder_location}/${upload_date}"
	    if [ ! -d "${copy_folder_location}/${upload_date}" ]; then
		echo "`date +'%Y-%m-%d %H-%M-%S.%06N'`: [process_tiff.sh] ERROR creating project_cache folder (${copy_folder_location}/${upload_date}) for project \"${InstitutionName}\"."
	    fi
	    # todo, we would like to add the MD5SUM for this file in the JSON as a new field
	    MD5=$(/usr/bin/md5sum -b "${image_file}" | cut -d' ' -f1)
	    echo "$(jq '. += {"md5": "'${MD5}'"}' "${json_file}")" > /tmp/md5temp && mv /tmp/md5temp "${json_file}"
	    cp "$image_file" "${json_file}" "${copy_folder_location}/${upload_date}/"
	fi
	
	# the next entries will fill up the disk (all original files end up in the uploads_done_dir)
	# Instead we should only copy the json and remove the raw data instead.
	# We are now removing the svs/ndpi files after 7 days from the uploads_done folder.
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] mv \"$image_file\" \"${json_file}\" \"${uploads_done_dir}\""
	#mv "$image_file" "${json_file}" "${uploads_done_dir}"
	rm -f "$image_file"
	mv "${json_file}" "${uploads_done_dir}"
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] Done processing path-based import for ${InstitutionName}"
	exit
    fi

    SeriesDescription="${Specimen}, ${Stain}, Block: ${Block} Biopsy: ${Biopsy} Slide: ${SlideNR} Department: ${Department} REK: ${REK}"
    StudyDescription="${SeriesDescription}"

    # 0020,0010 needs to be unique for this participant
    StudyID="${Block}${Biopsy}${SlideNR}"
    
    # do all processing in a temporary folder
    tmp_dir=`/bin/mktemp -d -t create_dicom_XXXXXX`
    
    tiff_file_path="${image_file}"
    tiff_filepath=`/usr/bin/dirname "${tiff_file_path}"`
    tiff_file=`/usr/bin/basename "${tiff_file_path}"`
    output_dir="${tmp_dir}"
    anonymized_dir=`/bin/mktemp -d -t anonymize_dicom_XXXXXX`
    
    # 1. Convert tiff to DICOM
    echo "docker run -i --rm -v \"${tiff_filepath}\":/data -v \"${tmp_dir}\":/output dicom_wsi:latest --input \"/data/$tiff_file\" --seriesDescription \"${SeriesDescription}\" --outFolder /output --sparse 2>&1 | jq -Rsa ."
    convert_message=`docker run -i --rm -v "${tiff_filepath}":/data -v "${tmp_dir}":/output dicom_wsi:latest --input "/data/${tiff_file}" --seriesDescription "${SeriesDescription}" --outFolder /output --sparse 2>&1 | jq -Rsa .`

    # 2. Anonymize DICOMs
    echo "/home/processing/bin/anonymize --input \"${tmp_dir}\"  --output \"${anonymized_dir}\" -j \"${InstitutionName}\" --tagchange \"0008,0080=PROJECTNAME\" --patientid \"${Participant}\" --tagchange \"0040,2001=EventName:${Event}\" --tagchange \"0040,1002=EventName:${Event}\" --tagchange \"0008,0090=EventName:${Event}\" -b -m --numthreads 2"

    #
    # There are some tags that should be coded on research PACS (Sectra) for pathology.
    # Information for this is from the PIE Image Import API document.
    #  0008,0050 Accession Number, PIE case key, Example=ASDHFJANCAWK
    #  0008,0080 InstitutionName, not used yet
    #  0010,0010 Patient Name
    #  0010,0020 Patient ID
    #  0020,000E Series Instance UID, same for all files in the slide
    #  0020,0010 StudyID, reportIT/T number of the sending lab, T16-12345
    #  0040,0560 Specimen Description Sequence, Specimen, block and staining information, Example: IIB HE, based on Specimen, block and staining information is read from this sequence according to supplement 122 (ftp://medical.nema.org/medical/dicom/final/sup122_ft2.pdf). Specimen and block name is read using code P3-4000A / 111709 (or 121041 if missing). Staining is read from P3-00003 / F-61D98
    
    #
    
    StudyDate=`date +%Y%m%d`
    StudyTime=`date +%H%M%S`
    anon_output=`/home/processing/bin/anonymize --input "$tmp_dir" --output "$anonymized_dir" -j "${InstitutionName}" --tagchange "0008,0080=PROJECTNAME" --patientid "${Participant}" --tagchange "0040,2001=EventName:${Event}" --tagchange "0040,1002=EventName:${Event}" --tagchange "0008,0090=EventName:${Event}" --tagchange "0008,1030=${StudyDescription}" --tagchange "0020,0010=${StudyID}" --tagchange "0010,4000=${Stain}" --tagchange "0008,0020=${StudyDate}" --tagchange "0008,0030=${StudyTime}" -b -m --numthreads 2 2>&1 | jq -Rsa .`
    
    # 3. Send anonymized output to the research PACS
    # storescu
    storescu_output=`/usr/bin/storescu -xf /var/www/html/applications/Attach/storescu.cfg Default -nh -aec DICOM_STORAGE -aet FIONA +sd +r -v vir-app5274.ihelse.net 7810 "${anonymized_dir}" 2>&1 | jq -Rsa .`

    # get the StudyInstanceUID, SeriesInstanceUID for this upload -- needs to be tested
    StudyInstanceUID=`find "${anonymized_dir}" -type f | grep -v "json" | head -1 | xargs -I'{}' dcmdump +P StudyInstanceUID {} | cut -d'[' -f2 | cut -d']' -f1`
    SeriesInstanceUID=`find "${anonymized_dir}" -type f | grep -v "json" | head -1 | xargs -I'{}' dcmdump +P SeriesInstanceUID {} | cut -d'[' -f2 | cut -d']' -f1`
    
    # copy json to "done"-folder and delete the input ndpi/svs
    fname=`basename "${json_file}"`
    /bin/mv "${json_file}" "${uploads_done_dir}"
    # TODO: add some information to the file
    #  jq '.[] += { "SeriesInstanceUID": "'${SeriesInstanceUID}'" }'
    /usr/bin/jq ". += { \"import_date\": \"`date`\" }" "${uploads_done_dir}/${fname}" > /tmp/tmp_added_message.json
    /bin/mv /tmp/tmp_added_message.json "${uploads_done_dir}/${fname}"
    /usr/bin/jq ". += { \"convert_message\": ${convert_message}, \"anon_message\": ${anon_output}, \"storescu_message\": ${storescu_output}, \"patho_study_instance_uid\": \"${StudyInstanceUID}\", \"patho_series_instance_uid\": \"${SeriesInstanceUID}\" }" "${uploads_done_dir}/${fname}" > /tmp/tmp_added_message.json
    /bin/mv /tmp/tmp_added_message.json "${uploads_done_dir}/${fname}"

    
    # TODY: add some information to REDCap for this project - we need a transfer request + all the structured information in the project
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] INFO: start updatePathologyREDCap.py with \"${uploads_done_dir}/${fname}\""
    /var/www/html/applications/Attach/updatePathologyREDCap.py "${uploads_done_dir}/${fname}"
    
    # cleanup storage in tmp for tmp_dir and anonymized_dir
    # we are removing files from uploads and uploads_done based on the 7 days rule now (keeping the json files around)
    if [ -e "${image_file}" ]; then
	echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] delete files: ${image_file} ${output_dir} ${anonymized_dir}"
	#/bin/rm -Rf "${image_file}"
	## echo "should delete file ${image_file}"
	#/bin/rm -Rf "${output_dir}"
	#/bin/rm -Rf "${anonymized_dir}"
    fi
    end=$(date +%s)
    # add the end time to the json file
    procTimeInSeconds=$(($end-$start))
    /usr/bin/jq ". += { \"transfer_active_proc_time\": \"${procTimeInSeconds}\" }" "${uploads_done_dir}/${fname}" > /tmp/tmp_added_message.json
    /bin/mv /tmp/tmp_added_message.json "${uploads_done_dir}/${fname}"
    
    echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: [process_tiff.sh] done in $(($end-$start)) seconds"
    exit
done
#echo "`date +'%Y-%m-%d %H:%M:%S.%06N'`: process_tiff.sh done"

