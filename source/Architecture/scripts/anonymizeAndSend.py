#!/usr/bin/env python3
"""
anonymizeAndSend.py
====================

For each transfer request created by createTransferRequests.py this script will anonymized all DICOM files before forwarding them to research PACS storage. Successful storage is marked in REDCap's TransferRequest table (project Incoming). If errors are found during anonymization or during sending to research PACS errors are added to the TransferRequest REDCap table. Such errors are indicated by Assign as orange highlights.

- user: processing
- depends-on:

  - createTransferRequests.py (``/home/processing/transfer_requests``)
  - REDCap https://localhost:4444/ (project Incoming, table TransferRequests)
  - Series level JSON files in: ``/data/site/raw/*/*/*.json``

- log-file:

  - ``${SERVERDIR}/logs/anonymizeAndSend.log``,

- pid-file: ``${SERVERDIR}/.pids/anonymizeAndSend.pid``
- start:

.. code-block:: bash

   */1 * * * *  /usr/bin/flock -n /home/processing/.pids/anonymizeAndSend.pid /home/processing/bin/anonymizeAndSend.py >> /home/processing/logs/anonymizeAndSend.log 2>&1

Notes
-----

During anonymization every study is marked with a StudyInstanceUID that identifies them as already anonymized. Currently the check performed will look for a specific root UID ("1.3.6.1.4.1.45037") followed by a dot and a numeric sequence (without further dots).


"""



import pycurl, io, hashlib, glob, os, tempfile, shlex, datetime, time, shutil
import pydicom, re
from pydicom.filereader import InvalidDicomError
from urllib.parse import urlencode
import sys

# read the request json files, each request should be fulfilled and marked as such in REDCap
import json

# read requests from this directory
request_dir = '/home/processing/transfer_requests/'

start_time = time.time()
print("%s: [anonymizeAndSend.py] start processing" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

# we store to /home/processing/transfers_done/ and /home/processing/transfers_fail/

def updateREDCap(vals):
    buf = io.BytesIO()

    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': json.dumps(vals),
        'returnContent': 'count',
        'returnFormat': 'json',
        'record_id': hashlib.sha1().hexdigest()[:16]
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    print("%s: [anonymizeAndSend.py] update %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
    buf.close()


# get all the exclusions per project for series that should not be rewrite pixel data
def getRewritePixelExclusions():
    buf = io.BytesIO()
    data = {
            'token': '921AD1F8B4ADA41EA7A05696888CC83D',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'fields[0]': 'record_id',
            'fields[1]': 'rewrite_ex_tag',
            'fields[2]': 'rewrite_ex_reg',
            'fields[3]': 'project_features',
            'rawOrLabel': 'label',
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
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    #print buf.getvalue()
    data = []
    try:
        data = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        data = []
    buf.close()
    val = {}
    project_features = {} # 'project_features___0': "0" }
    # ignore all other projects that don't have a first rule
    for q in data:
        if 'rewrite_ex_reg' in q and q['rewrite_ex_reg'] != '':
            if not q['record_id'] in val:
                val[q['record_id']] = []
            val[q['record_id']].append([q['rewrite_ex_tag'], q['rewrite_ex_reg']])
        # check for removal of PR objects during transfer
        #print("project_features test: %s" % (json.dumps(q)))
        if 'project_features___0' in q and q['project_features___0'] == "Checked":
            if not q['record_id'] in project_features:
                project_features[q['record_id']] = { 'project_features___0': "1" }
            project_features[q['record_id']]['project_features___0'] = "1"
        # never remove burned-in image information for this project
        if 'project_features___1' in q and q['project_features___1'] == "Checked":
            if not q['record_id'] in project_features:
                project_features[q['record_id']] = { 'project_features___1': "1" }
            project_features[q['record_id']]['project_features___1'] = "1"
        # remove all secondary objects during transfer
        if 'project_features___2' in q and q['project_features___2'] == "Checked":
            if not q['record_id'] in project_features:
                project_features[q['record_id']] = { 'project_features___2': "1" }
            project_features[q['record_id']]['project_features___2'] = "1"

    #print(json.dumps(val))
    return { 'rewritePixelExclusions': val, 'project_features': project_features }


# if we do some transfers we can have special settings for each in the DataTransferProject project, pull those and return as dictionary
def getProjectTransferRules():
    buf = io.BytesIO()
    data = {
            'token': '921AD1F8B4ADA41EA7A05696888CC83D',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'forms[0]': 'projects',
            'rawOrLabel': 'raw',
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
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.setopt(pycurl.FOLLOWLOCATION, 1)
    ch.perform()
    ch.close()
    #print buf.getvalue()
    data = []
    try:
        data = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        data = []
    buf.close()
    val = {}
    # ignore all other projects that don't have a first rule
    for q in data:
        if 'project_import_rule_1_tag' in q and q['project_import_rule_1_tag'] != '':
            val[q['project_name']] = [q['project_import_rule_1_tag'], q['project_import_rule_1_regexp']]
    #print(json.dumps(val))
    return val


# all transfers, are those too many?
def getTransfers():
    files = glob.glob(request_dir + "*.json")
    # send oldest files first
    files.sort(key=os.path.getmtime, reverse=True)
    transfers = []
    for file in files:
        with open(file, 'r') as infile:
            try:
                data = json.load(infile)
            except json.decoder.JSONDecodeError:
                print("%s: [anonymizeAndSend.py] Error, could not read in %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), file))
                pass
            data['filename'] = file
            transfers.append( data )
    return transfers

from pathlib import Path
import subprocess

rules = getProjectTransferRules()
ret = getRewritePixelExclusions()
rewritePixelExclusions = ret['rewritePixelExclusions']
project_features = ret['project_features']
#print("PROJECT FEATURES IS: %s" % (json.dumps(project_features)))

transfers = getTransfers()
for idx, t in enumerate(transfers):
    print("%s: [anonymizeAndSend.py] transfer %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), t))
    start_time_processing = datetime.datetime.now()
    # we should verify that the file is ok - need a project name and a target patient name
    event_name = ''
    if ('transfer_event_name' in t) and (t['transfer_event_name'] != ''):
        event_name = " --eventname \"%s\" --tagchange \"0040,2001=EventName:%s\" --tagchange \"0040,1002=EventName:%s\" --tagchange \"0008,0090=EventName:%s\" " % (t['transfer_event_name'], t['transfer_event_name'], t['transfer_event_name'], t['transfer_event_name'])
        #event_name = " --tagchange \"0040,2001=EventName:%s\" --tagchange \"0040,1002=EventName:%s\" --tagchange \"0008,0090=EventName:%s\" " % (t['transfer_event_name'], t['transfer_event_name'], t['transfer_event_name'])

    # we can have regular expressions specified in redcap for this project, change your behavior if that is the case
    # --regtagchange '0032,4000=\[[^ ]+ ([^ ]+ [AMP]+).*\](.*)'
    special_tag_changes = ''
    if ('transfer_project_name' in t) and (t['transfer_project_name'] in rules):
        special_tag_changes = " --regtagchange \"%s=%s\" " % (rules[t['transfer_project_name']][0], rules[t['transfer_project_name']][1])

    if not os.path.isdir('/data/site/raw/' + t['study_instance_uid'] + '/'):
        print("%s: [anonymizeAndSend.py] Error, the path %s does not exist [idx: %d]. Resend from PACS!" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), '/data/site/raw/' + t['study_instance_uid'] + '/', idx))
        # TODO: here we store the request that contains fields like tranfer_error___1, something we later compute again, fix by putting only real request fields in here
        errorMessages = { "request": t, "error": "Study has been deleted from Fiona. Resend from PACS!" }
        # we should ignore this send request - move it to failed now
        nfn = '/home/processing/transfers_fail/%s_fail.log' % (os.path.basename(t['filename']))
        os.rename(t['filename'], nfn)
        nfn = '/home/processing/transfers_fail/%s_fail_messages.log' % (os.path.basename(t['filename']))
        with open(nfn,'w') as json_file:
            json.dump(errorMessages, json_file, indent=2, default=str)

        continue

    # we should process this one file and tell REDCap about it later
    # problem is that this could fail... we don't want to send an update if we encounter errors
    # we could store in REDCap if we run into a problem!
    # we need some temporary space to send anonymize and send
    with tempfile.TemporaryDirectory() as tmpfn:
        # store data to anonymize into the input directory here
        inputanon = os.path.join(tmpfn, "input")
        if not os.path.exists(inputanon):
            os.mkdir(inputanon)
        outputanon = os.path.join(tmpfn, "output")
        if not os.path.exists(outputanon):
            os.mkdir(outputanon)

        did_masking = 0
        errorMessages = { "request": t }
        # lets start with the data in raw and check if we have to run image anonymization, or just tag anonymization
        with os.scandir('/data/site/raw/' + t['study_instance_uid'] + '/') as it:
            for entry in it:
                # only count the directories - they contain the links to the raw images in archive
                if entry.is_file():
                    continue
                # each directory corresponds to an image series and should have a json with the same name, inside that json we have the classification
                series_instance_uid = entry.name
                jsonfilename = "%s.json" % (entry.path)
                doimageanon = False
                siemens_no_image = False
                found_pr_image = False
                found_secondary_capture = False
                if os.path.isfile(jsonfilename):
                    print("%s: [anonymizeAndSend.py] found json for series %s..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), series_instance_uid))
                    with open(jsonfilename, 'r') as infile:
                        try:
                            content = json.load(infile)
                        except json.decoder.JSONDecodeError:
                            print("%s: [anonymizeAndSend.py] Error: could not parse json file %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), jsonfilename))
                            content = {}
                            pass
                        if 'ClassifyType' in content:
                            if 'CHECKBURNEDINFO' in content['ClassifyType']:
                                if ('SeriesDescription' in content) and content['SeriesDescription'].startswith("(shadow) "):
                                    pass
                                else:
                                    print("%s: [anonymizeAndSend.py] found burned in info (potentially), anonymize dicom image data %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), jsonfilename, json.dumps(content['ClassifyType'])) )
                                    doimageanon = True
                                    found_secondary_capture = True
                            else:
                                print("%s: [anonymizeAndSend.py] no burned in image information in %s " % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), jsonfilename) )
                            if 'ABCD-Physio' in content['ClassifyType']:
                                siemens_no_image = True
                        if 'Modality' in content:
                            if 'PR' in content['Modality']:
                                found_pr_image = True
                else:
                    print("%s: [anonymizeAndSend.py] we did not find a json for this series %s, copy series without image anonymization" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), entry.path))

                # check for features, remove presentation state files?
                if found_pr_image:
                    if t['transfer_project_name'] in project_features:
                        # do we have the flag set for removal of PR?
                        if 'project_features___0' in project_features[t['transfer_project_name']]:
                            if project_features[t['transfer_project_name']]['project_features___0'] == "1":
                                # ok we have both, a PR image series and also a request to remove those during transfer
                                # can we just ignore the series here?
                                print("%s: [anonymizeAndSend.py] Feature: [%s] found PR modality and \"Remove presentation state (PR) objects during import\" flag. Skip import of this series [%s]." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), t['transfer_project_name'], jsonfilename))
                                continue
                                pass

                if found_secondary_capture:
                    if t['transfer_project_name'] in project_features:
                        # do we have the flag set for removal of PR?
                        if 'project_features___2' in project_features[t['transfer_project_name']]:
                            if project_features[t['transfer_project_name']]['project_features___2'] == "1":
                                # skip because this is a secondary capture image and we don't like those in this project
                                print("%s: [anonymizeAndSend.py] Feature: [%s] found secondary image and \"Remove secondary capture objects during import\" flag is set. Skip import of this series [%s]." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), t['transfer_project_name'], jsonfilename))
                                continue
                                pass

                # if we have a siemens NO-IMAGE file we cannot see it in PACS, add a new placeholder image for the same series
                # Note: We need to make sure that images are added only once. Assume that there is a single file per series for NON-IMAGE.
                if siemens_no_image:
                    cmd = '/home/processing/bin/addNoImageImage "%s" "%s"' % (t['study_instance_uid'], series_instance_uid)
                    print("%s: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cmd))
                    cmd = shlex.split(cmd)
                    try:
                        o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                        #print(o)
                    except subprocess.CalledProcessError as e:
                        print("%s: [anonymizeAndSend.py] Error running addNoImageImage. Return code was not 0 but %d, there was an error: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e.returncode, e.output))

                # if we have "Never anonymized burned-in image data" enabled for a project do not do it
                #print("  check if project %s is in project_features %s" % (t['transfer_project_name'], json.dumps(project_features)))
                if t['transfer_project_name'] in project_features:
                    #print("project_features is: %s" % (project_features))
                    if 'project_features___1' in project_features[t['transfer_project_name']]:
                        if project_features[t['transfer_project_name']]['project_features___1'] == "1":
                            #print("project features: doimageanon set to False now for project %s" % (t['transfer_project_name']))
                            doimageanon = False

                # we could have an exclusion for rewritepixel in rewritepixelexclusions for this project
                if doimageanon:
                    if t['transfer_project_name'] in rewritePixelExclusions:
                        # we need to check one of the files
                        fname = os.listdir(os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid))[0]
                        dcmFile = os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid, fname)
                        dataset = 0
                        try:
                            dataset = pydicom.read_file(dcmFile)
                        except OSError:
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ": [anonymizeAndSend.py] Error, could not access file: " + dcmFile + " " + os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid))
                            dataset = 0
                        except IOError:
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ": [anonymizeAndSend.py] Error, could not access file: " + dcmFile + " " + os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid))
                            dataset = 0
                        except InvalidDicomError:
                            print("%s: [anonymizeAndSend.py] Error: Could not read DICOM file: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), dcmFile))
                            dataset = 0
                        if dataset != 0:
                            #print("found DICOM data, check pixel exclusions %s" % (json.dumps(rewritePixelExclusions[t['transfer_project_name']])))
                            for exrule in rewritePixelExclusions[t['transfer_project_name']]:
                                print("%s: [anonymizeAndSend.py] Check for exclusion rule: %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), exrule[0], exrule[1]))
                                tag_str = exrule[0].split(" ")[0]
                                tag1, tag2 = tag_str.split(":")
                                if ( int(tag1,0), int(tag2,0) ) in dataset:
                                    # now we can check if the value is ok
                                    v = dataset[int(tag1,0), int(tag2,0)].value
                                    pattern = re.compile(exrule[1])
                                    if re.match(exrule[1], v):
                                        print("%s: [anonymizeAndSend.py] Found a rewrite exclusion rule match for %s and %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), exrule[1], v))
                                        doimageanon = False
                    else:
                        print("%s: [anonymizeAndSend.py] no exclusions for this project: %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), t['transfer_project_name'], json.dumps(rewritePixelExclusions)))

                if doimageanon:
                    # copy and anon
                    # shutil.copy(os.path.join('/data/site/raw', t['study_instance_uid']), inputanon, follow_symlinks = True)
                    inputanon_subdir = os.path.join(inputanon, series_instance_uid)
                    if not os.path.exists(inputanon_subdir):
                        os.mkdir(inputanon_subdir)
                    # rewrite does not work on symbolic links, lets copy the data to a temp directory before calling rewrite
                    with tempfile.TemporaryDirectory() as rewritetemp:
                        #rewritetemp = '/tmp/bla'
                        shutil.copytree(os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid), os.path.join(rewritetemp, series_instance_uid), symlinks=False, ignore_dangling_symlinks = True)
                        print("%s: [anonymizeAndSend.py] copy files from %s to %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid), os.path.join(rewritetemp, series_instance_uid)))
                        cmd = 'docker run --rm -v %s:/input -v %s:/output rewritepixel --input /input --output /output -c 20' % (os.path.join(rewritetemp, series_instance_uid), inputanon_subdir)
                        print("%s: [anonymizeAndSend.py] %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cmd))
                        did_masking = 1
                        if not "rewritepixel_command" in errorMessages:
                            errorMessages["rewritepixel_command"] = []
                        errorMessages["rewritepixel_command"].append(cmd)
                        cmd = shlex.split(cmd)
                        try:
                            o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                            #print(o)
                        except subprocess.CalledProcessError as e:
                            print("%s: [anonymizeAndSend.py] Error running check_call, return code was not 0 but %d, there was an error: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e.returncode, e.output))
                else:
                    # only copy
                    print("%s: [anonymizeAndSend.py] copytree %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid), os.path.join(inputanon, series_instance_uid)))
                    shutil.copytree(os.path.join('/data/site/raw', t['study_instance_uid'], series_instance_uid), os.path.join(inputanon, series_instance_uid), symlinks=False, ignore_dangling_symlinks = True)


        # anonymize all files in this directory and send from there - hopefully there is enough space here
        #cmd = '/home/processing/bin/anonymize --input \"/data/site/archive/scp_%s\" --output \"%s\" -j \"%s\" --tagchange \"0008,0080=PROJECTNAME\" %s --patientid \"%s\" -b -m --numthreads 2' % (t['study_instance_uid'], tmpfn, t['transfer_project_name'],event_name,t['transfer_name'])
        # make a copy for debugging
        #shutil.copytree(tmpfn, "/tmp/bla")
        #print("Copied anonymize directory to /tmp/bla")

        # TODO:
        # import all the current projects from REDCap to save in the array in order to anonymize with old-style UIDs
        oldStyleProjects = ["8DISC", "0014-IPF", "0023-PFILD", "A4D", "ABANDIA", "ABBA.GP", "ACT", "PAIM", "AML-PET", "BABYPEP", "BACIO", "BackToBasic", "BBSC", "BC-TEST1", "BCBP-WP2", "BER_KP", "BICAM", "BIOPSY", "BMX-BAR", "BORTEM-17-I", "BORTEM-17-II", "BPRGung", "BRAINGUT", "BrainHeart", "BROCASTIM", "BURNOUT", "CAS-STUDIE", "CCTA-COEST", "CervicalCancer", "COVID-19", "COVID-19-IMAGING", "COVID-19-SUS", "CT-PERF", "CT_COPILOT", "D3CME", "DELIRIUM", "DISC", "DoseDense", "DYSFASING", "EC-PDX", "PECTMRI", "ECTMRI-DEID", "ENDO-SHARE", "EndometrialCancer", "EPENDYMOMA", "ERAN-TEST", "FABRY_DAT", "FATCOR_FOL", "FUNDECT", "GEN-ECT-IC", "GenKOLS", "GRASP-CLIN", "GRASP-CPT", "GRASPCPT02", "HealthyVolunteers-FONNA", "HealthyVolunteers-FORDE", "HealthyVolunteers-HUS", "HealthyVolunteers-SUS", "Hjerte3T", "HOF-RSA", "Hofte89", "HVAI21-CT", "HYPERBAR_A", "IMMUN-MS", "ISOCC", "JMETAST", "KALK", "KFPVTEST1", "KNE-NAV", "KNE-PROT", "LAR-BARN", "LAR-MRI", "LGG", "LIDC-IDRI", "LIFEHABPIL", "LungCTBergen", "M4Autism_B", "MALIGN", "MD21", "METIMMOX", "METIMMOX-2", "MIBLOCK", "MOBA_BRAIN", "MR_PROSTATA", "N-DOSE", "N-DOSE_AD", "NADPARK", "NAKKE", "NEVR_COVID", "NO-ALS", "NOPARK", "NOR-TEST", "NOR-TEST-2", "NORCOAST", "NorDCap", "NORDSTAR", "NorPEPS", "NoS\u00e5r", "NRS", "NUKOA", "OFAMS", "ORTHO", "OVERLORD-MS", "P535", "PANCANCER", "PARENT-ASD", "PATELLA", "PATOTEST_1", "PATOTEST_2", "PBICAM", "PEP11EPT", "PeTreMac", "PHACT", "PHOENIX-ACT", "PRADA-II", "PRO-GLIO", "PRO-LBD", "QC-FRARIE", "QC-MISC", "QC - NH Phantom", "R-LINK", "RAAO-REG", "RAM-MS", "REACT-MCI", "REBECCA", "REG-ECT", "RESTATE", "RHINESSA", "Sarkom", "SAS-GKRS-trial-01", "SE-PED", "SECTRA Laboratories", "SIROLIMUS", "SMART-MS", "StatEpiCon", "STRAT-PARK", "THORA", "THORAPET", "TMJ-DE", "TNT-RECORD", "Tool-Making", "TP53", "Transpara", "Transpara150", "TransparaBergen", "TransparaStavanger", "TransparaVEST", "TransparaVEST22", "TREATM_DAT", "V-REX", "VeRaVest", "VFO_TEST", "VNVWM", "WA42293_PR", "WorkflowWIMLTestProject", "XPHYSTEST"]

        oldStyleFlag_str = ""
        if t['transfer_project_name'] in oldStyleProjects:
            oldStyleFlag_str = "-u"

        cmd = '/home/processing/bin/anonymize --input \"%s\" --output \"%s\" -j \"%s\" --tagchange \"0008,0080=PROJECTNAME\" %s --patientid \"%s\" -b %s -m --numthreads 2 %s' % (inputanon, outputanon, t['transfer_project_name'],event_name,t['transfer_name'], oldStyleFlag_str, special_tag_changes)


        # lets make sure the command line is kosher
        cmd = shlex.split(cmd)
        print("%s: [anonymizeAndSend.py] %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cmd))
        errorAnonymize = ""
        errorStoreSCU = ""
        o = ""
        try:
            # this might fail if the disk is full (writes to /tmp/)
            o = subprocess.check_output(cmd,stderr=subprocess.STDOUT)
            #print(o)
            # if we have an OutOfResources error, is that an error?
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print("%s: [anonymizeAndSend.py] Error running check_call, return code was not 0 but %d, there was an error: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e.returncode, e.output))
            errorMessages["anonymize_return_code"] = e.returncode
            errorMessages["anonymize_command"] = cmd
            errorMessages["anonymize_output"] = e.output
            #errorAnonymize = e.output if e.output is not None else "no message"
            errorAnonymize = "call to anonymize failed with error code %d" % (e.returncode)

        # we should have a mapping file now at the output location with the new study instance uid
        # strange, I get an error that the file exists, but it cannot be read - its empty
        # this looks like a timing issue with the external program above, maybe its not finished
        # writing the content to the disk? As a test, lets wait a bit
        time.sleep(1)
        mapped_uids = ""
        if os.path.isfile(outputanon + '/mapping.json'):
            with open(outputanon + "/mapping.json", 'r') as json_file:
                try:
                    content = json.load(json_file)
                    if "StudyInstanceUID" in content:
                        content = content["StudyInstanceUID"]
                except:
                    print("%s: [anonymizeAndSend.py] Error reading %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), outputanon + "/mapping.json"))
                    #print("\"", json_file.read(), "\"")
                    content = {}
                mapped_uids = ",".join(map(str, list(content.values())))

        print("%s: [anonymizeAndSend.py] storescu now the folder %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), outputanon))
        # can we send using docker, that might speed up this process due to network issues
        cmd = '/usr/bin/docker run --rm -v %s:/send dcmtk /usr/bin/storescu -xf /etc/dcmtk/storescu.cfg Default -nh -aec DICOM_STORAGE -aet FIONA +sd +r -v vir-app5274.ihelse.net 7810 \"/send\"' % (outputanon)
        cmd = shlex.split(cmd)
        print("%s: [anonymizeAndSend.py] %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cmd))
        o = ""
        try:
            o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            #print(o)
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print("%s: [anonymizeAndSend.py] %s, return code was not 0 but %d, there was an error: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), "Error running storescu", e.returncode, e.output))
            errorMessages["storescu_return_code"] = e.returncode
            errorMessages["storescu_command"] = cmd
            errorMessages["storescu_output"] = e.output
            errorStoreSCU = e.output if e.output is not None else "no message"
        else:
            # if we don't have an error but we found OutOfResources
            if "Refused: OutOfResources" in o.decode('utf8'):
                print("%s: [anonymizeAndSend.py] Error running storescu, OutOfResources message during send, %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), o.decode('utf8')))
                #print("%s" % (o.decode('utf8')))
                #shutil.copytree(outputanon, "/tmp/anons")
                errorMessages["storescu_return_code"] = -1
                errorMessages["storescu_command"] = cmd
                errorMessages["storescu_output"] = "OutOfResources in research PACS during send"
                errorStoreSCU = errorMessages["storescu_output"] if errorMessages["storescu_output"] is not None else "no message"

        # now send info back to REDCap about success (or not)
        anon_error = 0
        if len(errorAnonymize) > 0:
            anon_error = 1
        store_error = 0
        if  len(errorStoreSCU) > 0:
            store_error = 1
        any_error = 0
        if anon_error == 1 or store_error == 1:
            any_error = 1
        total_processing_time = 0
        try:
            total_processing_time = (datetime.datetime.now() - start_time_processing).seconds
        except Expection as e:
            print("%s: [anonymizeAndSend.py] Warning: error computing total processing time, ignored" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        dat = {
            'study_instance_uid': t['study_instance_uid'],
            'redcap_repeat_instance': t['redcap_repeat_instance'],
            'redcap_repeat_instrument': t['redcap_repeat_instrument'],
            'transfer_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'transfer_mapped_uid': mapped_uids,
            'transfer_error___1': anon_error,
            'transfer_error___2': store_error,
            'transfer_error___3': did_masking,
            'transfer_active_proc_time': total_processing_time,
            'transfer_error_message': json.dumps(errorMessages,indent=2,default=str) if any_error == 1 else "",
            'transfers_complete': 2 if any_error == 0 else 1
        }
        updateREDCap( [ dat ] )
        # if we did not see an error - lets move the request to done
        if any_error == 0:
            nfn = '/home/processing/transfers_done/%s_ok_%s' % (os.path.basename(t['filename']), datetime.datetime.now().strftime('%Y-%m-%d_%H:%M.log'))
            os.rename(t['filename'], nfn)
        else:
            # TODO: check if the saved information is containing the correct check box entries
            nfn = '/home/processing/transfers_fail/%s_fail.log' % (os.path.basename(t['filename']))
            os.rename(t['filename'], nfn)
            nfn = '/home/processing/transfers_fail/%s_fail_messages.log' % (os.path.basename(t['filename']))
            # For now lets not copy more failed messages, this wills our disk too fast
            with open(nfn,'w') as json_file:
                json.dump(errorMessages, json_file, indent=2, default=str)

end_time = time.time()
print("%s: [anonymizeAndSend.py] end processing [%s secs]" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), (end_time - start_time)))
