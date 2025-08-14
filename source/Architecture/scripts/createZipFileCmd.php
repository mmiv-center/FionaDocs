<?php
/***

createZipFileCmd.php
====================

System service used by the Export application to create zip-compressed files.

The command is called by cron approximately every 3 minutes. Data for export is requested from research PACS and
stored inside a zip file in a export-type specific format. Exports in 'PURE' format for example are sorted into
series directories.

- user: processing
- depends-on:

  - ``/export2/Export/files/``
  - ``/var/www/html/applications/Exports/php/execMeasurements.json`` (adds processing times by project)

- log-file:
  - ``${SERVERDIR}/logs/Exports_PrepareDownload.log``

- pid-file: ``${SERVERDIR}/.pids/Exports_PrepareDownload.pid``
- start:

.. code-block:: bash

   */3 * * * * /usr/bin/flock -n /home/processing/.pids/Exports_PrepareDownload.pid /usr/bin/php /var/www/html/applications/Exports/php/createZipFileCmd.php >> /home/processing/logs/Exports_PrepareDownload.log 2>&1


***/


require_once 'constants.php';
require_once '/var/www/html/php/AC.php';

/*
*
* Command line version of the script that creates a zip file.
* Cron job for processing:
*   /usr/bin/flock -n /home/processing/.pids/Exports_PrepareDownload.pid \
*         /var/www/html/applications/Exports/php/createZipFileCmd.php >> /home/processing/logs/Exports_PrepareDownload.log 2>&1
*
*/

// TODO: Check of multi-project downloads are sorted. Can it be that its alphabetically? Make sure that all projects are treated equally.
// TODO: Its ok to call this from the local machine by the PROCESSING_USER. Ignore all other calls.
$processUser = posix_getpwuid(posix_geteuid());

$configData = json_decode(file_get_contents('/data/config/config.json'), true);
$configUser = $configData['PROCESSING_USER'];
if ($processUser['name'] !== $configUser) {
    echo("Permission denied.".PHP_EOL);
    audit('createZipFileCmd', $processUser['name'], 'FAILURE');
    die();
}

function storeLog($message, $type) {
    global $user_name;
    $log_name = "/home/processing/logs/Exports_PrepareDownload.log";
    // replace all newlines with spaces and add a newline
    $now = DateTime::createFromFormat('U.u', microtime(true));
    if (is_bool($now)) {
        syslog(LOG_EMERG, "[createZipFileCmd.php] randomly get a microtime with zeroes, fall back to use 'U' only.");
        $now = DateTime::createFromFormat('U', microtime(true));
    }
    # TODO: user_name is not defined in this offline version of the script, should be added
    $msg = $now->format('Y-m-d H:i:s.u'). ": [createZipFileCmd.php] ".$type." [user ".$user_name."] ".str_replace("\n", "", $message).PHP_EOL;
    file_put_contents($log_name, $msg, FILE_APPEND | LOCK_EX);
}


// TODO: add audit calls here by project and user
storeLog("start processing", "INFO");
//echo(date("Y-m-d H:i:s").": INFO start processing...".PHP_EOL);

$timeStart = microtime(true);

// get the list of jobs (array of strings) and sort them by downloadAttempts in ASCENDING order
function getJobList() {
    $fileContents = file_get_contents("/var/www/html/applications/Exports/php/prepared_downloads_list.jobs");
    $downloadJobs = array();

    if ($fileContents !== "") {
        $downloadJobs = array_filter(explode(PHP_EOL, $fileContents));
        $downloadJobs = array_map(function ($a) { return json_decode($a, true); }, $downloadJobs);
    }

    $downloadAttempts = array_column($downloadJobs, 'downloadAttempts');
    array_multisort($downloadAttempts, SORT_ASC, $downloadJobs);

    return $downloadJobs;
}

// return the key of $job in array $jobs or return false
function findJobInJobs( $job, $jobs) {
  $found = false;
  foreach($jobs as $k => $j) {
     if ($j['studyinstanceuid'] == $job['studyinstanceuid'] && $j['exportType'] == $job['exportType'] && $j['accessionnumber'] == $job['accessionnumber']) {
        return $k;
     }
  }
  return $found;
}

// assumpt to be atomic function
function setJobList($downloadJobs, $keyToRemove) {
  $str = "";
  foreach ($downloadJobs as $job) {
    $str  = $str . json_encode($job) . "\n";
  }
  // in case there are any new jobs in $lastetJobList, add them as well
  $lastestJobList = getJobList();
  foreach ($lastestJobList as $key => $ljob) {
     if (findJobInJobs($ljob, $downloadJobs) === false && $key !== $keyToRemove) {
        // this is a new job now in the list of jobs, was not there when we started this script
        // syslog(LOG_EMERG, " adding something more : ".$str_ljob);
        $str = $str . json_encode($ljob) . "\n";
     }
  }

  file_put_contents("/var/www/html/applications/Exports/php/prepared_downloads_list.jobs", $str);
}

// Write average execution time to the measurements file
function writeAverageExecutionTime($project, $execTime)
{
    $fname = "/var/www/html/applications/Exports/php/execMeasurements.json";
    $measurements = array();

    if (file_exists($fname)) {
        storeLog("found execMeasurements.json", "INFO");
      $fileData = file_get_contents($fname);
      $measurements = json_decode($fileData, true);
    } else {
        storeLog("could not find execMeasurements.json, may be ok the first time...", "WARN");
    }

    if (array_search($project, $measurements)) {
        $measurements[$project] = ($measurements[$project] + $execTime) / 2;
    } else {
        $measurements[$project] = $execTime;
    }

    if ( file_put_contents($fname, json_encode($measurements)) === FALSE) {
        storeLog("Could not write measurements to file: ".$fname, "ERROR");
    } else {
        storeLog("Updated measurements to file: ".$fname. " as ".json_encode($measurements), "INFO");
    }
}

// Replace illegal characters from SeriesDescription tag
// Attention: Only lowercase characters will work, all other characters
// will be replaced with '-'.
function sanitizeFilename($path)
{
    //$patterns = array('/[øØ]/u', '/[åÅ]/u', '/[æÆ]/u');
    //$replacements = array('o', 'a', 'ae');
    //$path = preg_replace($patterns, $replacements, $path);
    return preg_replace( '/[^a-zA-Z0-9_^åÅøØæÆ]/u', '-', $path);
}

$downloadJobs = getJobList();

// do nothing and return early from script if job list is empty
if (count($downloadJobs) === 0) {
    //echo date("Y-m-d H:i:s").": INFO Job list is empty.".PHP_EOL;
    storeLog("JOB list is empty.", "INFO");
    return;
}

$nextJob = null;

// Some of the jobs might already be processed and the ZIP archive exists for them. Create the list of such jobs, and unset them from the prepared_downloads_list.jobs
$zipAlreadyExists = [];

// Check each job if ZIP file already exists.
// TODO: is there a way to optimize this step? That doesn't require to change permission for files for users `processing` and `www-data`
foreach ($downloadJobs as $jobKey => $job) {
    $currentJob = $job;
    $project = $currentJob['project'];
    $patientid = $currentJob['patientid'];
    $studyinstanceuid = $currentJob['studyinstanceuid'];
    $exportType = $currentJob['exportType'];
    $downloadAttempts = $currentJob['downloadAttempts'];
    $accessionnumber = $currentJob['accessionnumber'];
    $user = "";
    if (isset($currentJob['user'])) {
        $user = $currentJob['user'];
    }

    if ($downloadAttempts > DOWNLOAD_ATTEMPTS_LIMIT) {
        storeLog('job exceeded maximum download attempts (<='.DOWNLOAD_ATTEMPTS_LIMIT.'). '."Study Instance UID: $studyinstanceuid is ignored", "WARN");
        //echo date('Y-m-d H:i:s').' WARNING: The job exceeded maximux download attempts.'."Study Instance UID: $studyinstanceuid".PHP_EOL;
	    continue;
    }

    $exportFolder = "/export2/Export/files/";
    $fn = $project."_".$patientid."_*_".$studyinstanceuid."_".$accessionnumber."_".$exportType.".zip";
    $filePath = glob($exportFolder.$fn);

    if ($filePath) {
	foreach ($filePath as $f) {
            if (!file_exists($f)) {
	        $nextJob = $currentJob;
		break 2;
	    } else {
	      // file exists already
          storeLog("file exists: $f. Adding to the `already exists` list...", "INFO");
          //echo(date('Y-m-d H:i:s')."Info: file exists: $f. Adding to the `already exists` list...\n");
	      $zipAlreadyExists[] = $job;
	    }
        }
    } else {
        $nextJob = $currentJob;
	break;
    }
}

//echo date("Y-m-d H:i:s").": INFO: Checked ".count($downloadJobs)." jobs in `prepared_downloads_list.jobs` file.".PHP_EOL;
storeLog("checked ".count($downloadJobs)." jobs in `prepared_downloads_list.jobs` file.", "INFO");

if ($nextJob === null) {
    $jobs = getJobList();
    if (count($jobs) > 0) {
        storeLog("job list IS NOT empty. But there are no jobs to process further. It usually means the archived dataset is already saved. Or one of the jobs exceeded max download attempts.", "INFO");
        //echo date('Y-m-d H:i:s').": INFO Job list IS NOT empty. But there are no jobs to process further. It usually means the archived dataset is already saved. Or one of the jobs exceeded max download attempts.\n";

        // Removing already processed jobs (for which the archive is alrady saved on the disc)
        $countAlreadyExists = count($zipAlreadyExists);
        storeLog("removing already processed jobs ($countAlreadyExists) from the joblist...", "INFO");
        // echo date('Y-m-d H:i:s').": INFO: removing already processed jobs ($countAlreadyExists) from the joblist...\n";
        foreach ($zipAlreadyExists as $j) {
	      $key = array_search($j, $jobs);
	      unset($jobs[$key]);
	      setJobList($jobs, $key);
        }
    }
    storeLog("All the jobs have been processed.", "INFO");
    //echo date("Y-m-d H:i:s").": INFO: All the jobs have been processed.".PHP_EOL;
    return;
}

$project = $nextJob['project'];
$studyinstanceuid = $nextJob['studyinstanceuid'];
$accessionnumber = $nextJob['accessionnumber'];
$exportType = $nextJob['exportType'];
$patientid = $nextJob['patientid'];
$event = $nextJob['event'];
$destination = $nextJob['destination'];

// TODO: should this script send to TSD?
$allowedTSD = false;
#if (check_permission( "TSD_EXPORT_".$project )) {
#  $allowedTSD = true;
#}

function startsWith($string, $startString) {
    $len = strlen($startString);
    return (substr($string, 0, $len) === $startString);
}

if ($project == "RAM-MS") {
   $event = $patientid . '_' . $event;
   // make event name capital if it starts with w
   //if (startsWith($event,'w')) {
   //   $event = strtoupper($event);
   //}
   $event = str_replace("_w","_W",$event);
   //if (startsWith($event, "W0")) {
   //   $event = "W".ltrim($event, "W0");
   //}
   // instead of just the event name as a folder name
   // we want to use the patientid and the event name
} else if ($project == "Transpara") {
   //$event = $patientid . '_' . $event;
}

function tempdir($dir = null, $prefix = 'tmp_', $mode = 0700, $maxAttempts = 1000) {
    if (is_null($dir)) {
        $dir = sys_get_temp_dir();
    }

    $dir = rtrim($dir, DIRECTORY_SEPARATOR);

    if (!is_dir($dir) || !is_writable($dir)) {
        return false;
    }

    $attempts = 0;
    do {
        $path = sprintf('%s%s%s%s', $dir, DIRECTORY_SEPARATOR, $prefix, mt_rand(100000, mt_getrandmax()));
    } while ( !mkdir($path, $mode) && $attempts++ < $maxAttempts );

    return $path;
}

// now we should pull the data into a temp directory
$tempdir_name = tempdir('/export2/Export/');
// create a directory structure for the data
$dcmdir = $tempdir_name."/".$event."/DICOM";
if ($project == "RAM-MS") {
    $dcmdir = $tempdir_name."/DICOM_".$event."/DICOM";
}
$old_umask = umask(0);
mkdir($dcmdir, 0777, TRUE);
umask($old_umask);

// we can ask pullStudyFromIDS7 to have sub-folders for each image series...
storeLog("Start pulling ".$studyinstanceuid.", ".$accessionnumber.".", "INFO");
//echo(date("Y-m-d H:i:s").": Start pulling ".$studyinstanceuid.".\n");
$cmd = "/var/www/html/applications/Exports/php/pullStudyFromIDS7.sh ".escapeshellarg($studyinstanceuid)." ".escapeshellarg($accessionnumber)." ".escapeshellarg($project)." \"".$dcmdir."\" >> /home/processing/logs/createZipFileCmd.log 2>&1";

//syslog(LOG_EMERG, $cmd);
$o = null;
$ret_val = null;
//$o = shell_exec($cmd);
exec($cmd, $o, $ret_val);
// if we have an error value during pulling the study, we should try again
if ($ret_val != 0) {
   storeLog("Pulling ".$studyinstanceuid." error. Try ".$cmd." with pullStudyFromIDS7.sh again to make sure we can deliver all images. Stop now with createZipFileCmd.php", "ERROR");
   // mark this run so we do not get stuck on problematic bits forever
   $keyToRemove = array_search($nextJob, $downloadJobs);
   if ($keyToRemove !== false) {
     $downloadJobs[$keyToRemove]['downloadAttempts'] += 1;
     // now set this job to the end of the list
     //array_push($downloadJobs, $downloadJobs[$keyToRemove]);
     //unset($downloadJobs[$keyToRemove]);
     setJobList($downloadJobs, null);
   }

   return; // bail out here
}

//syslog(LOG_EMERG, $o. " call: ".$cmd);
storeLog("Pulling ".$studyinstanceuid." done.", "INFO");
//echo(date("Y-m-d H:i:s").": Pulling ".$studyinstanceuid." done.\n");

if (file_exists($dcmdir."/mapping.json")) {
    storeLog("We have a mapping.json in ".$dcmdir, "INFO");
    //echo(date("Y-m-d H:i:s").": We have a mapping.json in ".$dcmdir);
} else {
    storeLog("After pullStudyFromID7 no mapping.json found", "ERROR");
    //echo (date("Y-m-d H:i:s").": Error: After pullStudyFromID7 no mapping.json found");
}

// we should have a mapping.json in the tmpdir now
$StudyDate = "";
if (!file_exists($dcmdir."/mapping.json")) {
    // we could have no files at all in this case as well, todo: make error message more useful
    storeLog("no mapping.json was created by pullStudyFromIDs7.sh.", "ERROR");
    //echo date("Y-m-d H:i:s").": ERROR: no mapping.json was created by pullStudyFromIDs7.sh.".PHP_EOL;

    // now change the job order and make sure that our attempt counter is updated as well

    // unset($downloadJobs[$keyToRemove]);
    $keyToRemove = array_search($nextJob, $downloadJobs);
    if ($keyToRemove !== false) {
      $downloadJobs[$keyToRemove]['downloadAttempts'] += 1;
      // now set this job to the end of the list
      //array_push($downloadJobs, $downloadJobs[$keyToRemove]);
      //unset($downloadJobs[$keyToRemove]);
      setJobList($downloadJobs, null);
    }
    return;
} else {
    $c = json_decode(file_get_contents($dcmdir."/mapping.json"), true);
    $StudyDate = $c['StudyDate'];
    $PatientID = $c['PatientID'];

    // and remove the mapping.json file again
    unlink($dcmdir."/mapping.json");
}

// get information from REDCap
$tokens = json_decode(file_get_contents('/var/www/html/applications/Exports/php/tokens.json'), TRUE);
$token = "";

if (isset($tokens[$project])) {
    $token = $tokens[$project];
} else {
    storeLog("No token for project ".$project." found in Exports tokens.json.", "ERROR");
    //echo date("Y-m-d H:i:s").": Error: No token for this project found".PHP_EOL;
    return;
}

//
// lets create a control structure for the anonymization, store the entries we could rewrite
//
$control = array();
$control['tags'] = array();
$control['tags']["StudyDate"] = $StudyDate;
$control['tags']["PatientID"] = $PatientID;
$control['tags']["PatientBirthDate"] = "";
$control['tags']["PatientAge"] = "";
$control['tags']["PatientSex"] = "";

$data = array(
    'token' => $token,
    'content' => 'record',
    'format' => 'json',
    'type' => 'flat',
    'fields' => array('age','dob','first_name','record_id','sex'),
    'rawOrLabel' => 'raw',
    'rawOrLabelHeaders' => 'raw',
    'exportCheckboxLabel' => 'false',
    'exportSurveyFields' => 'false',
    'exportDataAccessGroups' => 'false',
    'returnFormat' => 'json'
);

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://fiona.ihelse.net:4444/api/');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_VERBOSE, 0);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_AUTOREFERER, true);
curl_setopt($ch, CURLOPT_MAXREDIRS, 10);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data, '', '&'));
$output = curl_exec($ch);
$output = json_decode($output, TRUE);
curl_close($ch);

$found = false;
foreach($output as $o) {
    if (isset($o['first_name']) && $o['first_name'] == $patientid) {
        $found = true;
        // fill in the values from this entry (dob, sex, etc..)
        if (isset($o['sex']) && $o['sex'] != "") {
            if ($o['sex'] == 0) {
                $control['tags']['PatientSex'] = "F";
	    } else if ($o['sex'] == 1) {
                $control['tags']['PatientSex'] = "M";
            }
        }

        if (isset($o['dob']) && $o['dob'] != "") {
            // could this be an array? We should check and use string value only (first array element)
            $control['tags']['PatientBirthDate'] = $o['dob'];
        }

        if (isset($o['age']) && $o['age'] != "") {
            // we should use the StudyDate and the dob to compute the PatientAge
            $control['tags']['PatientAge'] = sprintf("%03dY", $o['age']);
	    // in case we have partial dates like 0.5, we should change to the other formats for Age like:
	    // A string of characters with one of the following formats -- nnnD, nnnW, nnnM, nnnY; where
	    // nnn shall contain the number of days for D, weeks for W, months for M, or years for Y.
	    // Example: "018M" would represent an age of 18 months.
	    if ($o['age'] != floor($o['age'])) {
	       // this is a floating point number, we should store this in month instead of years
	       $control['tags']['PatientAge'] = sprintf("%03dM", $o['age']*12);
	    }
        }
    }
}

if ($found == false) {
   //echo("{ \"message\": \"No information about this participant in REDCap\" }");
   //return;
}

// now change the values based on the selected mode
if ($exportType == "RAM-MS") {
    // replace the dob with 01/01 for month and day
    if ($control['tags']['PatientBirthDate'] != "") {
        $year = substr($control['tags']['PatientBirthDate'], 0, 4);
        $pbd = new DateTime($year."-01-01");
        $control['tags']['PatientBirthDate'] = $year."0101";
    }

    // adjust the scan date $StudyDate
    $d = FALSE;
    //syslog(LOG_EMERG, "StudyDate is: ".$StudyDate);
    if ($StudyDate != "") {
        $d = date_create_from_format("Ymd", $StudyDate);
        if ($d !== FALSE) {
            $d = date_sub($d, date_interval_create_from_date_string('42 days'));
            $control['tags']['StudyDate'] = $d->format("Ymd");
        }
    }

    if ($control['tags']['PatientAge'] == "") {
        $control['tags']['PatientAge'] = ""; // recompute the patient age from the dob
        // keep the patient sex (could be from REDCap)
        // $control['tags']['PatientSex'] = "";
        // compute the PatientAge from StudyDate and PatientBirthDate
        if ($control['tags']['PatientBirthDate'] != "") {
            if ($d !== FALSE) {
                $diff = $d->diff($pbd);
                $control['tags']['PatientAge'] = sprintf('%03dY', $diff->y);
            }
        }
    }
    $control['tags']['SeriesDate'] = $control['tags']['StudyDate']; // there are more ...
    $control['tags']['AcquisitionDate'] = $control['tags']['StudyDate']; // there are more ...
    $control['tags']['ContentDate'] = $control['tags']['StudyDate']; // there are more ...

    // remove these entries
    $control['tags']['PatientWeight'] = "";
    $control['tags']['PatientSize'] = "";
    $control['tags']['InstitutionName'] = "";
    $control['tags']['StudyDescription'] = "";
    $control['tags']['PerformedProcedureStepDescription'] = "";
    // we cannot just delete the entries, they should instead be changed in REDCap - if they are wrong
    //$control['tags']['PatientAge'] = ""; // requested for RAM-MS
    //$control['tags']['PatientBirthDate'] = ""; // requested for RAM-MS

    // for RAM-MS we want to have dashes instead of underscores
    $pid = $patientid;
    $pid = str_replace("_", "-", $pid);

    //$pid = "DICOM_".$pid;
    $control['tags']['PatientID'] = $pid;
    $control['tags']['PatientName'] = $pid;
    $control['tags']['SmokingStatus'] = "";
    $control['tags']['PregnancyStatus'] = "";
    $control['tags']['LastMenstrualDate'] = "";
} else if ($exportType == "Transpara" ) {
    $control['tags']["PatientID"] = $PatientID;
    $control['tags']["PatientName"] = $PatientID;
    $control['tags']['AccessionNumber'] = $PatientID;
    $control['tags']['StudyDate'] = "";
    $control['tags']['SeriesDate'] = "";
    $control['tags']['ContentDate'] = "";
    $control['tags']['StudyTime'] = "";
    $control['tags']['SeriesTime'] = "";
    $control['tags']['ContentTime'] = "";
    $control['tags']['InstitutionName'] = "";
    $control['tags']['InstitutionAddress'] = "";
    $control['tags']['ReferringPhysician'] = "";
    $control['tags']['StationName'] = "";
    $control['tags']['InstitutionalDepartmentName'] = "";
    $control['tags']['PerformingPhysicianName'] = "";
    $control['tags']['OperatorName'] = "";
    $control['tags']['PatientBirthDate'] = "";
    $control['tags']['PatientSex'] = "";
    $control['tags']['PatientAge'] = "";
    $control['tags']['StationName'] = "";
    $control['tags']['OperatorsName'] = "";
    $control['tags']['ReferencedSOPClassUID'] = "";
    $control['tags']['ReferencedSOPInstanceUID'] = "";
}

// for each file run dcmodify
$ms = "";
foreach ($control['tags'] as $key => $value) {
    // We are using 'm'-odify here, this will produce an error
    // message if the tag does not exist yet. We should try to
    // insert as well. What about 'ma' to modifify all values?
    $ms = $ms." -i ".$key."=".$value;
}

//syslog(LOG_EMERG, "run dcmodify with  ".$ms);
// this would fail if we have too many files in this directory (length of command line error)
// instead do find here
//$cmd = "/usr/bin/dcmodify -nb -ie ".$ms." ".$dcmdir."/*";
// todo: we should use parallel here to speed up the process
$cmd = "find \"".$dcmdir."\" -type f -not -iname \"*.json\" -and -not -iname \"*.nii\" -print | xargs -I'{}' /usr/bin/dcmodify -nb -ie ".$ms." {}";

//echo($cmd);
shell_exec($cmd);

if ($exportType == "NIFTI" ) { // run this after anonymization
    // we need to run dcm2niix
    $cmd = "/usr/bin/dcm2niix -i n \"".$dcmdir."\"";
    shell_exec($cmd);
    // is this working? I think we do get all DICOM in the output as well
    // we need to remove all non .nii and non .json sidecar files
    $cmd = "find ".$dcmdir." -not -iname \"*.json\" -and -not -iname \"*.nii\" -and -not -iname \"*.bval\" -and -not -iname \"*.bvec\" -print | xargs -I'{}' rm {}";
    shell_exec($cmd);
}


$fn_folder = "/export2/Export/files/";
$fn = $project."_".$patientid."_".$event."_".$studyinstanceuid."_".$accessionnumber."_".$exportType.".zip";

// echo("Write data to ".$fn);
// now zip the folder
$zip = new ZipArchive();
$zip->open($fn_folder.$fn, ZipArchive::CREATE | ZipArchive::OVERWRITE);

try {
    $comment = "Archive created by the Research Information System, Bergen, Norway.\n".
        "\n".
        "Date of export: ". date("Y-m-d h:i")."\n".
        "Research project: ".$project."\n".
        "Export type: ".$exportType."\n".
        "Before sharing such a package check all de-identified meta data by visiting our Review application (ReviewDICOMTags/).\n".
        "\n".
        "PatientID: ".$control['tags']['PatientID']."\n".
        "Imaging Event: ".$event."\n".
        "PatientBirthDate: ".$control['tags']['PatientBirthDate']."\n".
        "PatientAge: ".$control['tags']['PatientAge']."\n".
        "StudyDate (scan date): ".$control['tags']['StudyDate']."\n";

    if ($exportType != "RAM-MS") {
        // for RAM-MS we don't want to have the txt file
        $zip->addFromString('fiona.txt', $comment);
    }

    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($tempdir_name),
        RecursiveIteratorIterator::LEAVES_ONLY
    );

    // read mapping2.json which contains information for each image - might be very large!
    $mapping2 = json_decode(file_get_contents($dcmdir."/mapping2.json"), true);

    $counter = 0;
    foreach ($files as $name => $file) {
        // Skip directories (they would be added automatically)
        if (!$file->isDir()) {
            // in some cases we want a directory tree as the output
            // right now that is only if
            // Get real and relative path for current file
            $filePath = $file->getRealPath();
            $relativePath = substr($filePath, strlen($tempdir_name) + 1);

            if (basename($filePath) == "mapping2.json") {
       	        continue;
            }

            if ($exportType == "PURE") {
	        // syslog(LOG_EMERG, "Export Type PURE for project: ". $mapping2[$fname]['InstitutionName']);
                // The mapping information is in mapping2.json (see above)
                // How about we use the information in the data/site/raw directory?
                // set a new relativePath
                $fname = $file->getFilename();

                if (isset($mapping2[$fname])) {
                    // lets look at the different variables
                    if (!isset($mapping2[$fname]['SeriesNumber']) || $mapping2[$fname]['SeriesNumber'] == "-1") {
                        $mapping2[$fname]['SeriesNumber'] = "unknown";
                    }
		    if (isset($mapping2[$fname]['SeriesDescription'])) {
		      $SeriesDescription = trim($mapping2[$fname]['SeriesDescription']);
		    } else {
		       $SeriesDescription = "unknown";
		    }
		    $SeriesDescription = sanitizeFilename($SeriesDescription);
		    if (!isset($mapping2[$fname]['InstitutionName'])) {
		      $mapping2[$fname]['InstitutionName'] = "unknown";
		    }
		    if (!isset($mapping2[$fname]['PatientID'])) {
		      $mapping2[$fname]['PatientID'] = "unknown";
		    }
		    if (!isset($mapping2[$fname]['StudyDate'])) {
		      $mapping2[$fname]['StudyDate'] = "unknown";
		    }
		    if (!isset($mapping2[$fname]['StudyTime'])) {
		      $mapping2[$fname]['StudyTime'] = "unknown";
		    }
		    if (!isset($mapping2[$fname]['SeriesNumber'])) {
		      $mapping2[$fname]['SeriesNumber'] = "unknown";
		    }

                    $path = $mapping2[$fname]['InstitutionName'].
		        "/".$mapping2[$fname]['PatientID'].
                        "/".$mapping2[$fname]['StudyDate'].
                        "_".$mapping2[$fname]['StudyTime'].
			($event == ""?"":"_".sanitizeFilename($event)).
                        "/".str_pad($mapping2[$fname]['SeriesNumber'], 4, '0', STR_PAD_LEFT).
                        //"_".str_replace("*", "all", str_replace(" ","_",$mapping2[$fname]['SeriesDescription'])).
			"_".$SeriesDescription.
                        "/".basename($relativePath);
		    $file_parts = pathinfo($path);
		    if ($file_parts["extension"] != "dcm") { // check if we have an extension dcm
		       $path = $path.".dcm"; // add if not
		    }
		    //$path = "\"".$path.replace("/\"/", "_")."\"";
                    $relativePath = $path;
                } else {
		  //syslog(LOG_EMERG, "Error: did not find variable: ".$fname." in mapping2.json: ".$dcmdir."/mapping2.json");
		}
            } else if ($exportType == "RAM-MS") {
                // if we are RAM-MS we don't want to have PS* or SR* files
                $fname = $file->getFilename();

                if (strpos($fname, "SR") === 0 || strpos($fname, "PS") === 0) {
                    // ignore this file, don't add
                    continue;
                }
            } else if ($exportType == "Spectroscopy") {
                $fname = $file->getFilename();

                if (isset($mapping2[$fname])) {
                    // lets look at the different variables
                    if ($mapping2[$fname]['SeriesNumber'] == "-1") {
                        $mapping2[$fname]['SeriesNumber'] = "unknown";
                    }

                    $path = $mapping2[$fname]['InstitutionName'].
		        "/".$mapping2[$fname]['PatientID'].
                        "/".$mapping2[$fname]['StudyDate'].
                        "_".$mapping2[$fname]['StudyTime'].
                        "/".$mapping2[$fname]['SeriesNumber'].
                        "_".str_replace(" ","_",$mapping2[$fname]['SeriesDescription']).
                        "/".basename($relativePath);
                    $relativePath = $path;
                }
	        // for Spectroscopy delete all files but the once that are of type
		// (0002,0002) UI [1.3.12.2.1107.5.9.1]                    #  20, 1 MediaStorageSOPClassUID

  	        $cmd = "/usr/bin/dcmdump +P SOPClassUID \"".$filePath."\" | cut -d'[' -f2 | cut -d']' -f1 | head -1 | tr -d '\n'";
		$SOPClassUID = shell_exec($cmd);
		//syslog(LOG_EMERG, "test for SOPCLASSUID as ".$SOPClassUID);
		if (strcmp($SOPClassUID, "1.3.12.2.1107.5.9.1") !== 0) {
		   // ignore this file
		   continue;
		}
	    }

  	    // Add current file to archive
            $ok = $zip->addFile($filePath, $relativePath);
	    if (!$ok) {
	       // syslog(LOG_EMERG, "Error: could not add relative path: ".$relativePath);
           storeLog("could not add relative path: ".$relativePath, "ERROR");
           //echo "Error: could not add relative path: ".$relativePath;
	    } else {
	       $counter = $counter + 1;
	    }
        }
    }
    // In rare cases we only had files that we removed. The zip file will be empty at this
    // point. Check and put a message in there.
    if ($counter == 0) {
       // no file?
       $zip->addFromString('warning.txt', 'Empty zip file was created. Check if there are real DICOM images in this study. Presentation state objects and structured reports might be filtered out based on your export type setting.');
    }

    //syslog(LOG_EMERG, "ADD A FILEs TO ".$fn_folder.$fn.". Added ".$counter." files.");

    // Zip archive will be created only after closing object
    // Problem here is that this might take a long time - so long that we get
    // killed by a timeout. Would be better if we can do this work in the background..
    $ret = $zip->close();
    // syslog(LOG_EMERG, "Zip close returned:".$ret);

    // Check if the job is "Prepare download(email)" so that archive is secured with password
    if (array_key_exists('password', $nextJob) && array_key_exists('email', $nextJob)) {
        if ($nextJob['password'] !== '' && $nextJob['email'] !== '') {
	    $email = $nextJob['email'];
	    $emailParts = explode('@', $email);
            $domain = array_pop($emailParts);

            if (!in_array($domain, ['helse-bergen.no', 'ihelse.net'])) {
                echo "Domain name of the email for secured download is not valid!\n";
            } else {
		$encryptedFilename = $fn_folder.$nextJob['password'].".zip";
                $internalArchive = $fn_folder.$fn;
		$encryptedArchive = $project."_".$patientid."_".$event."_".$studyinstanceuid."_".$accessionnumber."_".$exportType."_encrypted.7z";
		$archivePassword = base64_decode($nextJob['password']);
		$encryptedArchivePath = $fn_folder.$encryptedArchive;

		shell_exec("7z a $encryptedArchivePath $internalArchive -p$archivePassword -mhe=on");

		if (!file_exists($encryptedArchivePath)) {
            storeLog("Error ocured in the process of archiving with 7z. File not found!", "ERROR");
            //echo "Error ocured in the process of archiving with 7z. File not found!\n";
		   die();
		}

                $from = "no-reply@helse-bergen.no";
                $headers  = 'MIME-Version: 1.0' . "\r\n";
		$headers .= 'Content-type: text/html; charset=iso-8859-1' . "\r\n";

                // Create email headers
		$headers .= 'From: '.$from."\r\n".
		    'Reply-To: '.$from."\r\n" .
		    'X-Mailer: PHP/' . phpversion();

                // <email address of sender, who created the link>
		$senderEmail = $nextJob['sender_email'];
		$randomId = rand(100, 1000);

		$textFirst = "This email has been created by $senderEmail using FIONA, a regional system to support image-data transfers. <strong>Ignore this email if it has been errouneously forwarded to you.</strong><br><br>".
		             "FIONA link request: $randomId<br>".
			     "Project: $project<br>".
			     "Participant ID: $patientid<br>".
			     "Visit/Event: $event<br>".
			     'Link: <a href="https://fiona.ihelse.net/applications/Exports/process.php?link='.$encryptedArchive.'">Link to archive</a><br><br>'.
			     "This link will remain active for a limited number of days. Please download files immediately to ensure that<br>".
			     "you receive the image data forwarded to you. Contact <a href=\"mailto:\"".$senderEmail."\">".$senderEmail."</a> to get a new link.<br><br>".
			     "Notice: Data received by this service are pseudonymized but, may still contain patient identifying information and they<br>".
			     "do count as health data. Such data should only be stored in secure locations based on your institutional rules.";


                // Send second email with Secure number and password: 11 - secret
   	       	$textSecond = '<!DOCTYPE html><html><body style="font: monospace">'."$randomId<br>$archivePassword".'</body></html>';

                if (mail($email, "FIONA link to archive", $textFirst, $headers)) {
                    storeLog("First email has been sent to ".$email, "EMAIL");
                    //echo(date('Y-m-d H:i:s').": First email has been sent to ".$email."\n");
		    sleep(15);
		    if (mail($email, "no-reply", $textSecond, $headers)) {
                storeLog("Second email has been sent to ".$email, "INFO");
		        //echo(date('Y-m-d H:i:s').": INFO Second email has been sent to ".$email."\n");
		    } else {
                storeLog("second mail could not be sent to ".$email, "ERROR");
		        //echo(date('Y-m-d H:i:s').": Error: second mail could not be sent ".$email."\n");
	            }
                } else {
                    storeLog("first mail could not be sent ".$email, "ERROR");
                    //echo(date('Y-m-d H:i:s').": Error: first mail could not be sent ".$email."\n");
                }
            }

            //echo date('Y-m-d H:i:s').": Removing internal zip file.\n";
            storeLog("Removing internal zip file from ".$fn_folder.$fn, "INFO");
            // remove original zip
            unlink($fn_folder.$fn);
 	}
    }

} catch (Exception $e) {
    //syslog(LOG_EMERG, 'Caught exception: '.$e->getMessage()."\n");
    $zip->close();
}


// we need to delete the temp folder $dcmdir again, all work is done and we
// have the information we need in the zip file
function rrmdir($src) {
    $dir = opendir($src);
    while(false !== ( $file = readdir($dir)) ) {
        if (( $file != '.' ) && ( $file != '..' )) {
            $full = $src . '/' . $file;
            if ( is_dir($full) ) {
                rrmdir($full);
            }
            else {
                unlink($full);
            }
        }
    }
    closedir($dir);
    rmdir($src);
}

//if (is_dir($tempdir_name)) {
//    echo date("Y-m-d H:i:s")." INFO: delete temp folder: ".$tempdir_name.PHP_EOL;
//    rrmdir($tempdir_name);
//}

if (file_exists($tempdir_name)) {
    storeLog("deleting temp folder: ".$tempdir_name, "INFO");
    //echo(date("Y-m-d H:i:s")." INFO: deleting temp folder: ".$tempdir_name.PHP_EOL);

    $di = new RecursiveDirectoryIterator($tempdir_name, FilesystemIterator::SKIP_DOTS);
    $ri = new RecursiveIteratorIterator($di, RecursiveIteratorIterator::CHILD_FIRST);

    foreach ($ri as $file) {
        $file->isDir() ? $res = rmdir($file->getRealPath()) : unlink($file->getRealPath());
    }

    rmdir($tempdir_name);
}

// We should cache the file at this point, that would
// allow us to use the cache to speed up processing,
// if data exists in the cache we can also immediately
// return it instead of doing the pull again.
// But data could have changed so we need to be able to
// overwrite the cache use- or regenerate the cache even
// if a dataset is found. We have to store the anonymization
// type as well so we don't deliver the wrong data. We need
// to report the cache so we can update the button state
// on the website.
function uploadToTSD($fn_folder, $fn) {
    global $user_name, $project, $allowedTSD;
    // check if the user has permission to Export to TSD for this project
    // Permission would be something like TSD_EXPORT_<Project name>
    if (!$allowedTSD) {
        echo("{ \"message\": \"Error: Export to TSD is not allowed for the current user ".$user_name."!\" }");
        return;
    }

    // info about this export is in REDCap
    // look for project_tsd_group and project_tsd_id (in DataTransferProjects)
    $data = array(
        'token' => "921AD1F8B4ADA41EA7A05696888CC83D",
        'content' => 'record',
        'format' => 'json',
        'type' => 'flat',
        'fields' => array('project_tsd_group','project_tsd_id','project_tsd_user'),
        'rawOrLabel' => 'raw',
        'rawOrLabelHeaders' => 'raw',
        'exportCheckboxLabel' => 'false',
        'exportSurveyFields' => 'false',
        'exportDataAccessGroups' => 'false',
        'returnFormat' => 'json'
    );

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://fiona.ihelse.net:4444/api/');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_VERBOSE, 0);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_AUTOREFERER, true);
    curl_setopt($ch, CURLOPT_MAXREDIRS, 10);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data, '', '&'));
    $output = curl_exec($ch);
    $TSD_EXPORT_INFO = json_decode($output, TRUE);
    curl_close($ch);

    //syslog(LOG_EMERG, "TSD INFO: ".$output);
    $group = "";
    $id = "";
    $user = "";
    foreach($TSD_EXPORT_INFO as $t) {
        if (isset($t['project_tsd_group']) && $t['project_tsd_group'] != "") {
            $group = $t['project_tsd_group'];
        }

        if (isset($t['project_tsd_id']) && $t['project_tsd_id'] != "") {
            $id = $t['project_tsd_id'];
        }

        if (isset($t['project_tsd_user']) && $t['project_tsd_user'] != "") {
            $user = $t['project_tsd_user'];
        }
    }

    //syslog(LOG_EMERG, " group: ".$group." id: ".$id." user: ".$user);

    if ($group == "" || $id == "") {
        echo("{ \"message\": \"Error: Export to TSD not setup for this project.\" }");
        return;
    }

    // ok now we have all the information we need, we can upload to TSD using curl
    // curl -X POST -H "Content-Type: application/json" -d '{"id": "66558604-0232-4c28-a15b-4cda177d5e0e"}' https://data.tsd.usit.no/capability_token

    $ch = curl_init("https://data.tsd.usit.no/capability_token");
    $payload = json_encode(array( "id" => $id ));

    $header = array(
        'Content-Type: application/json',
        'Content-Length: '.strlen($payload)
    );

    curl_setopt_array($ch, array(
        CURLOPT_URL, 'https://data.tsd.usit.no/capability_token',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => false,
        CURLOPT_PROXY => 'http://proxy.ihelse.net:3128/',
        //CURLINFO_HEADER_OUT => true,
        CURLOPT_FOLLOWLOCATION => true,
        //CURLOPT_SSL_VERIFYPEER => false,
        //CURLOPT_SSL_VERIFYHOST => 0,
        //CURLOPT_ENCODING => "",
        //CURLOPT_USERAGENT => "spider",
        CURLOPT_CUSTOMREQUEST => 'POST',
        //CURLOPT_POST => 1,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => $header
    ));

    $output = curl_exec($ch);

    //$errmsg  = curl_error($ch);
    //syslog(LOG_EMERG, "error message: ".$errmsg);

    //syslog(LOG_EMERG, "sending: ".json_encode($data));
    //$ch = curl_init();
    //curl_setopt($ch, CURLOPT_URL, 'https://data.tsd.usit.no/capability_token');
    //curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    //curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    //curl_setopt($ch, CURLOPT_VERBOSE, 1);
    //curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    //curl_setopt($ch, CURLOPT_AUTOREFERER, true);
    //curl_setopt($ch, CURLOPT_MAXREDIRS, 10);
    //curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
    //curl_setopt($ch, CURLOPT_POST, true);
    //curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    //curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    //curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    //$output = curl_exec($ch);

    //syslog(LOG_EMERG, json_encode(curl_getinfo($ch))." ".$output);

    $JWT = json_decode($output, TRUE);
    curl_close($ch);

    $TSD_TOKEN = "";
    if (isset($JWT['token'])) {
        $TSD_TOKEN = $JWT['token'];
    } else {
        echo("{ \"message\": \"Error: TSD did not return a JWT token for us ".trim(json_encode($output),'"').".\" }");
        return;
    }

    // curl -d "@testfile.txt" -X PUT -H "Authorization: Bearer ${token}" https://data.tsd.usit.no/v1/p697/files/stream/p697-member-group/destination_filename
    //syslog(LOG_EMERG, "file: ".$fn_folder.$fn." ".$TSD_TOKEN);
    $cf = new CURLFile($fn_folder.$fn);
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://data.tsd.usit.no/v1/".$user."/files/stream/".$group."/".$fn);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_HEADER, false);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array("Authorization: Bearer ".$TSD_TOKEN));
    curl_setopt($ch, CURLOPT_PROXY, 'http://proxy.ihelse.net:3128/');
    curl_setopt($ch, CURLOPT_POSTFIELDS, ["upload" => $cf]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);

    echo("{ \"message\": \"TSD export might have been successful. Please check at the destination for ".$fn."\" }");

    curl_close($ch);

    return;
}


// We want to export to TSD if this is configured for the project
if ($destination == "tsd") {
    uploadToTSD($fn_folder, $fn);
}

// Removing already processed jobs (for which the archive is alrady saved on the disc)
$countAlreadyExists = count($zipAlreadyExists);
storeLog("removing already processed jobs ($countAlreadyExists) from the joblist...", "INFO");
//echo date('Y-m-d H:i:s').": INFO: removing already processed jobs ($countAlreadyExists) from the joblist...\n";
foreach ($zipAlreadyExists as $j) {
	$key = array_search($j, $downloadJobs);
	unset($downloadJobs[$key]);
}

// Remove line from `prepared_downloads_list.jobs`
$keyToRemove = array_search($nextJob, $downloadJobs);
unset($downloadJobs[$keyToRemove]);
setJobList($downloadJobs, $keyToRemove);

//file_put_contents("/var/www/html/applications/Exports/php/prepared_downloads_list.jobs", implode(PHP_EOL, $downloadJobs));

$execTime = microtime(true) - $timeStart;
writeAverageExecutionTime($project, $execTime);

audit('createZipFileCmd', $processUser['name'], 'SUCCESS');
// we hide here where the file is (will be in /export2/Export/files/)
storeLog("filename: ".$fn, "INFO");
//echo(date("Y-m-d H:i:s").": INFO: filename: $fn".PHP_EOL);
storeLog("execution time: ".$execTime, "INFO");
//echo(date("Y-m-d H:i:s").": INFO: execution time: $execTime".PHP_EOL);

$fn_md5=$fn_folder . DIRECTORY_SEPARATOR . pathinfo($fn, PATHINFO_FILENAME).".md5";
// TODO: Not all files get an MD5SUM file with this. Maybe the background job is not a good idea?
$cmd = "/usr/bin/md5sum -b \"".$fn_folder."/".$fn."\" 2>&1 > \"".$fn_md5."\"";
shell_exec($cmd);

?>
