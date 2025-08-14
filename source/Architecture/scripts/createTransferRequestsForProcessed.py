#!/usr/bin/env python3
"""
createTransferRequestsForProcessed.py
=====================================

Detect if we have image series forwarded to FIONA
that belong to a study that already exists on the research PACS.
This happens if data is forwarded from the research PACS to a
workstation. The workstation procudes new image series and forwards
those to FIONA. There is no transfer request for them so they are not
automatically forwarded and Assign is not displaying them because
they have a study instance uid without a dot.

We want to forward them by first finding them (no dot in raw and dot
in series). Change their StudyInstanceUID to the incoming
one that has a transfer request. Send them to fiona so they will
show up in the correct folder, be detected as new incoming series for
existing study and auto forward using createTransferRequests.py.

- user: processing
- depends-on:

  - REDCap Incoming project

- log-file:

  - ``${SERVERDIR}/logs/createTransferRequestsForProcessed.log``

- pid-file: ``${SERVERDIR}/.pids/createTransferRequestsForProcessed.pid``
- start:

.. code-block:: bash

   */30 * * * * /usr/bin/flock -n /home/processing/.pids/createTransferRequestsForProcessed.pid /home/processing/bin/createTransferRequestsForProcessed.py >> /home/processing/logs/createTransferRequestsForProcessed.log 2>&1


Notes
-----

This script will create a SeriesInstanceUID compatible with FIONA's anonymizer and use it to mark the new image series. If this identifier is changed the script needs to be updated.

.. code-block:: python

  def hashID( SeriesInstanceUID ):
      # do the same operation that would be done by the anonymizer
      # get a safe string
      s = SeriesInstanceUID.encode("utf-8")
      org_root = "1.3.6.1.4.1.45037"
      h = "%s.%s" % (org_root, hashlib.sha256(s).hexdigest());
      return h[0:63]


"""



import pycurl, io, hashlib, datetime, os, glob, shutil, tempfile, time
from urllib.parse import urlencode
import hashlib

# create request json files, each request should be fulfilled and marked as such in REDCap
import json

#

# TODO: Seems to be slow to finish

#
# Detect what series need this special treatment
#

# all transfers, are those too many?
def getTransfers():
    buf = io.BytesIO()
    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'rawOrLabel': 'raw',
        'fields[0]': 'study_instance_uid',
        'fields[1]': 'transfer_mapped_uid',
        'fields[2]': 'study_date',
        'fields[3]': 'study_accession_number',
        'fields[4]': 'transfer_project_name',
        'fields[5]': 'transfer_event_name',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    ch.setopt(ch.POST, 1)
    ch.setopt(ch.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    try:
        ch.perform()
    except pycurl.error:
        print("%s: [createTransferRequestsForProcessed.py] Error, could not reach REDCap" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        buf.close()
        return []
    ch.close()
    #print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except:
        print("%s: [createTransferRequestsForProcessed.py] could not get JSON from REDCap. Instead got: " % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
        qdata = []
    buf.close()
    # this should get us the redcap_repeat_instance as well
    return qdata


def hashID( SeriesInstanceUID ):
    # do the same operation that would be done by the anonymizer
    # get a safe string
    s = SeriesInstanceUID.encode("utf-8")
    org_root = "1.3.6.1.4.1.45037"
    h = "%s.%s" % (org_root, hashlib.sha256(s).hexdigest());
    return h[0:63]

# get all SeriesInstanceUID for all Studies from Incoming
def getSeriesInstanceUIDs():
    buf = io.BytesIO()
    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'rawOrLabel': 'raw',
        'fields[0]': 'study_instance_uid',
        'fields[1]': 'series_instance_uid',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    ch.setopt(ch.POST, 1)
    ch.setopt(ch.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    #print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except:
        print("%s: [createTransferRequestsForProcessed.py] [ERROR] could not get JSON from REDCap. Instead got: " % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
        qdata = []
    buf.close()
    # create a structure for each studyinstanceuid that has a hash of the hashed value and the real seriesinstanceuid
    erg = {}
    for entry in qdata:
        StudyInstanceUID = ""
        SeriesInstanceUID = ""
        if "study_instance_uid" in entry:
            StudyInstanceUID = entry['study_instance_uid']
        if "series_instance_uid" in entry:
            SeriesInstanceUID = entry['series_instance_uid']
        if StudyInstanceUID != "" and SeriesInstanceUID != "":
            if not(StudyInstanceUID in erg):
                erg[StudyInstanceUID] = []
            # hash the SeriesInstanceUID
            hashedSeriesInstanceUID = hashID(SeriesInstanceUID)
            erg[StudyInstanceUID].append(hashedSeriesInstanceUID)

    # this should get us the redcap_repeat_instance as well
    return erg


print("%s: [createTransferRequestsForProcessed.py] Start processing" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

# get all the transfer requests, will contain the new studyInstanceUID in research PACS
transfers = getTransfers()
print("%s: [createTransferRequestsForProcessed.py] getTransfers done" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
listOfSeriesInstanceUIDs = getSeriesInstanceUIDs()
print("%s: [createTransferRequestsForProcessed.py] getSeriesInstanceUIDs done with %d entries" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(listOfSeriesInstanceUIDs)))

studies = glob.glob('/data/site/raw/*/')
for study in studies:
    # No dot in folder (folder==StudyInstanceUIC,SeriesInstanceUID), but dot in study (old style UID).
    # If there is no dot we have anonymized this series already. We would not want to do this again so
    # skip that series.
    org_root = "1.3.6.1.4.1.45037"
    str_without_root = study.replace(org_root, "")

    # IF we screen out studies we will not catch series that are newly calculated on an already anonymized
    # study. But we would like to rewrite those studies StudyInstaceUID - to the original and send them
    # to FIONA. They would show up as new series for the old StudyInstanceUIDs and therefore trigger a
    # resend. - so we can not test this here.

    ##if str_without_root.find(".") != -1:
    ##    print("Skip a study because there was a dot in the study instance uid \"%s\"" % study)
    ##    continue

    studyInstanceUID = study.replace("/data/site/raw/", "")
    studyInstanceUID = studyInstanceUID.replace("/","")
    org_root = "1.3.6.1.4.1.45037"
    newStyleStudyInstanceUID = org_root + "." + studyInstanceUID
    newStyleStudyInstanceUID = newStyleStudyInstanceUID[0:63]

    #print("Found a study : %s" % (study))
    series = glob.glob(study + "/*.json")
    for serie in series:
        # We might have a series here that comes already from the research PACS like
        # a presentation state object. Those are created on the research PACS and
        # they also have series instance uids with dots. We can check the IncomingConnection
        # to filter those out. IncomingConnection.CallerIP != "vir-app5274".
        with open(serie, 'r') as myfile:
            data = json.load(myfile)
        if data['IncomingConnection']['CallerIP'] == "vir-app5274":
            print("%s: [createTransferRequestsForProcessed.py] INFO skip series because the CallerIP was vir-app5274 \"%s\"" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), series))
            continue
        #print("%s: [createTransferRequestsForProcessed.py] INFO Series from %s: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), data['IncomingConnection']['CallerIP'], serie))
        # we want to ignore the StudyDate for this series - that will be either generated by the external application or its already shifted
        PatientID = ""
        if ('PatientID' in data) and (data['PatientID'] != ""):
            PatientID = data['PatientID']
        SeriesNumber = ""
        if ('SeriesNumber' in data) and (data['SeriesNumber'] != ""):
            SeriesNumber = data['SeriesNumber']

        realSeriesInstanceUID = os.path.basename(serie).replace(".json","")
        seriesInstanceUID = os.path.basename(serie).replace(".json", "")
        org_root = "1.3.6.1.4.1.45037"
        seriesInstanceUID_without_root = seriesInstanceUID.replace("%s." % (org_root), "")
        # if we have a dot (old style for not yet anonymized) and we don't start with the org root
        if seriesInstanceUID_without_root.find(".") != -1:
            #print("%s: [createTransferRequestsForProcessed.py] INFO do something for this series \"%s\", it does contain a dot so its new, even if we remove the org_root" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), seriesInstanceUID))
            # what is the real StudyInstanceUID?
            realStudyInstanceUID = ""
            StudyDate = ""
            StudyAccessionNumber = ""
            ProjectName = ""
            EventName = ""
            for transfer in transfers:
                # which one is the right id?
                # our study_instance_uid could be one with the new root as well
                if (transfer['transfer_mapped_uid'] == studyInstanceUID) or (transfer['transfer_mapped_uid'] == newStyleStudyInstanceUID):
                    if ('study_instance_uid' in transfer) and (transfer['study_instance_uid'] != ""):
                        realStudyInstanceUID = transfer['study_instance_uid']
                        ProjectName = transfer['transfer_project_name']
                        EventName = transfer['transfer_event_name']
                        break

            if realStudyInstanceUID != "":

                #print("Here is a series that does have a dot: %s %s" % (studyInstanceUID, serie))
                #print("%s: [createTransferRequestsForProcessed.py] INFO found real studyInstanceUID is: %s (series: %s)" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realStudyInstanceUID, realSeriesInstanceUID))
                # find the correct StudyDate for this (we have to do this again because one transfer will
                # have the transfer_mapped_uid and the other has the StudyDate
                for transfer in transfers:
                    # we use the StudyDate on file for the original study
                    if transfer['study_instance_uid'] == realStudyInstanceUID:
                        # print("  our transfer is: %s" % (json.dumps(transfer)))
                        if ('study_accession_number' in transfer) and (transfer['study_accession_number'] != ""):
                            StudyAccessionNumber = transfer['study_accession_number']
                        if ('study_date' in transfer) and (transfer['study_date'] != ""):
                            StudyDate = transfer['study_date']
                            break

                # Now the question is if that series is new?
                # If its new we want to do something, if its old we don't. We need to see if the
                # series under that studyInstanceUID is not there -> send or if the
                # is there if its newer.

                # We can check if the folder exists for this realSeriesInstanceUID
                newSeries = False
                rawPath = "/data/site/raw/%s/%s/" % (realStudyInstanceUID,realSeriesInstanceUID)
                if not os.path.exists(rawPath):
                    print("%s: [createTransferRequestsForProcessed.py] INFO folder %s does not exist in /data/site/raw/. Seems to be a new series..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), rawPath))
                    newSeries = True
                else:
                    #print("%s: [createTransferRequestsForProcessed.py] INFO folder %s does exist in /data/site/raw/. Seems to be an old series." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), rawPath))
                    # but it can also be new if its there already just newer date
                    # Here the rawPath is not good enough. It conly contains symbolic links that are created once.
                    # Instead we need to check the date of a file pointed to by a symbolic link inside the rawPath folder.
                    filesInSeries = glob.glob("%s*" % (rawPath))
                    filesInSeries.sort(key=os.path.getmtime)
                    tstamp_destination = os.path.getmtime(filesInSeries[0])
                    # tstamp_destination = os.path.getmtime(rawPath)
                    tstamp_input = os.path.getmtime(serie)
                    tstamp_destination_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstamp_destination))
                    tstamp_input_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstamp_input))
                    if tstamp_destination < tstamp_input:
                        newSeries = True
                        print("%s: [createTransferRequestsForProcessed.py] INFO folder exists in /data/site/raw but our input is newer. Seems to be a new series... %s < %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), tstamp_destination_time_str, tstamp_input_time_str))
                    else:
                        #print("%s: [createTransferRequestsForProcessed.py] INFO folder exists in /data/site/raw and our input is older. Ignore this series (%s, %s, %s)... %s >= %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), PatientID, StudyDate, SeriesNumber, tstamp_destination_time_str, tstamp_input_time_str))
                        pass
                    #print("     %s < %s" % (rawPath, serie))

                # IF this is a new series, but just because it came back from research PACS with an anonymized SeriesInstanceUID
                # then ignore this series (set back to newSeries = False).
                if newSeries:
                    # check if this seriesInstanceUID is in the list of hashed seriesinstanceuids from Incoming in REDCap
                    # check if our current realSeriesInstanceUID is in the listOfSeriesInstanceUIDs (should be a hash)
                    if realStudyInstanceUID in listOfSeriesInstanceUIDs:
                        print("%s: [createTransferRequestsForProcessed.py] INFO Found realStudyInstanceUID %s as key (key values: %s)" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realStudyInstanceUID, ",".join(listOfSeriesInstanceUIDs[realStudyInstanceUID])))
                        if realSeriesInstanceUID in listOfSeriesInstanceUIDs[realStudyInstanceUID]:
                            print("%s: [createTransferRequestsForProcessed.py] INFO SeriesInstanceUID hash (%s) matches an existing series in Incoming. Not a new series." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realSeriesInstanceUID))
                            newSeries = False
                        else:
                            print("%s: [createTransferRequestsForProcessed.py] INFO DID NOT FIND %s in %s, still a new series" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realSeriesInstanceUID, ",".join(listOfSeriesInstanceUIDs[realStudyInstanceUID])))
                    else:
                        print("%s: [createTransferRequestsForProcessed.py] INFO did not find realStudyInstanceUID %s in Incoming" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realStudyInstanceUID))


                if newSeries:
                    # we might reference here some image series, those referenced UID's need to be replaced as well
                    # as an example we might have a structured report that is relative to an existing series
                    # so we need to collect those, find them in REDCap and replace them below, most likely there is only
                    # a single one...
                    # Build a lookup table for all uids for this study and add their hash codes for a reverse lookup
                    # all this work... maybe we should just forward the images directly? At least do this for some
                    # projects?
                    #if ProjectName == "TransparaBergen" or ProjectName == "TransparaStavanger":
                    #    # shortcut - just submit the series data as is, don't add again to archive
                    #    print("  Forward this series directly to research PACS.")
                    #    seriesFolder = serie.replace(".json","")
                    #    if os.path.exists(seriesFolder):
                    #        print("  Send now data in \"%s\"" % (seriesFolder))

                    # TODO: secondary capture image series require the InstitutionName entry to be visible in research PACS.
                    # For Transpara that tag is not written so reports are only visible to users with full access. Check and
                    # add the InstitutionName tag to such image series.

                    print("%s: [createTransferRequestsForProcessed.py] INFO process series by changing the StudyInstanceUID (\"%s\") and sending it again to fiona - will trigger forward." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realStudyInstanceUID))
                    with tempfile.TemporaryDirectory() as tmpdir_KK:
                        # copy the data to a temp folder
                        seriesFolder = serie.replace(".json","")
                        if os.path.exists(seriesFolder):
                            print("%s: [createTransferRequestsForProcessed.py] INFO make temp copy of %s into %s/input" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), seriesFolder, tmpdir_KK))
                            shutil.copytree(seriesFolder, "%s/input" % (tmpdir_KK), ignore_dangling_symlinks = True)

                            # copy directly if we are in the right projects
                            if ProjectName == "TransparaBergen" or ProjectName == "TransparaStavanger" or ProjectName == "TransparaVEST" or ProjectName == "TransparaVEST2020-2022" or ProjectName == "TransparaVEST22" or ProjectName == "TransparaForde" or ProjectName == "TransparaReview" or ProjectName == "BADDI" or ProjectName == "TOBE2L":
                                # TODO: add InstitutionName to each image

                                print("%s: [createTransferRequestsForProcessed.py] INFO start sending to DICOM_STORAGE" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
                                os.system("/usr/bin/docker run --rm -i -v %s/input:/send dcmtk /usr/bin/storescu -xf /etc/dcmtk/storescu.cfg Default -nh -aec DICOM_STORAGE -aet FIONA +sd +r -v vir-app5274.ihelse.net 7810 /send" % (tmpdir_KK))
                                print("%s: [createTransferRequestsForProcessed.py] INFO this is a %s case. Forward to research PACS as original done." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ProjectName))
                                # We should also convert the report to PDF embedded DICOM to allow for viewing on IDS7
                                #if ProjectName == "TransparaStavanger":
                                #    os.system("/home/processing/bin/extractDataFromTransparaSR.sh %s/input >> /home/processing/logs/extractDataFromTransparaSR.log" % (tmpdir_KK))
                                #    print("  Store structured report scores TransparaStavanger in REDCap for %s..." % (seriesFolder))
                                if ProjectName == "TransparaBergen" or ProjectName == "TransparaStavanger" or ProjectName == "TransparaVEST" or ProjectName == "TransparaVEST2020-2022" or ProjectName == "TransparaVEST22" or ProjectName == "TransparaForde" or ProjectName == "TransparaReview" or ProjectName == "BADDI" or ProjectName == "TOBE2L":
                                    print("%s: [createTransferRequestsForProcessed.py] INFO start Store structured report scores %s in REDCap for %s..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ProjectName, seriesFolder))
                                    os.system("/home/processing/bin/extractDataFromTransparaSR.sh %s/input >> /home/processing/logs/extractDataFromTransparaSR.log" % (tmpdir_KK))
                                    print("%s: [createTransferRequestsForProcessed.py] INFO end Store structured report scores TransparaBergen in REDCap for %s..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), seriesFolder))
                                # we have to do something here because we get the same images every time, so we need to add them properly
                            else:
                                #print("  copied files as %s" % glob.glob("%s/input/*" % (tmpdir_KK)))
                                # this will only work for small number of images (limit by the command line length)
                                # os.system("/usr/bin/dcmodify -ie -nb -ma \"StudyInstanceUID=%s\" -i \"InstitutionName=external\" -m \"StudyDate=%s\" \"%s/input\"/*" % (realStudyInstanceUID, StudyDate, tmpdir))
                                # this call should work with any number of images coming in
                                #print(" create a modified version for: %s" % (tmpdir_KK))
                                os.system("/usr/bin/find \"%s/input\" -type f -print | /usr/bin/xargs -I'{}' /usr/bin/dcmodify -ie -nb -ma \"StudyInstanceUID=%s\" -i \"InstitutionName=external\" -i \"AccessionNumber=%s\" -m \"StudyDate=%s\" {}" % (tmpdir_KK, realStudyInstanceUID, StudyAccessionNumber, StudyDate))
                                print("%s: [createTransferRequestsForProcessed.py] INFO created a modified version with StudyInstanceUID %s now (date: %s, patientid: %s, SeriesNumber: %s)." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), realStudyInstanceUID,StudyDate, PatientID, SeriesNumber))
                                # now send that folder using s2m.sh (the output folder will disappear if we don't wait here)
                                os.system("/var/www/html/server/utils/s2m.sh \"%s/input/\"" % (tmpdir_KK))

                                if ProjectName == "NOPARK":
                                    # extract the numeric values for REDCap as well
                                    os.system("/home/processing/bin/extractDataFromDaTQUANT.sh \"%s/input\" \"%s_arm_1\" >> /home/processing/logs/extractDataFromDaTQUANT.log" % (tmpdir_KK, EventName))
                                    print("%s: [createTransferRequestsForProcessed.py] INFO Stored report scores for DaTQUANT in REDCap for \"%s\", data in %s/input with event: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), seriesFolder, tmpdir_KK, EventName))
                                    print("%s: [createTransferRequestsForProcessed.py] INFO This is a %s case [%s]. Forward to research PACS as original done." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ProjectName, PatientID))
                                # here the temp folder is deleted again so nothing remains

            #else:
            #    print("Error: We do nothing because real study instance uid could not be found")
        #else:
        #    # this means that we always need a "." in a series that should be added again (minux the org_root)
        #    print("Info: We do nothing for this series \"%s\", it does not contain a dot so we assume its already anonymized" % seriesInstanceUID)


print("%s: [createTransferRequestsForProcessed.py] End processing" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
