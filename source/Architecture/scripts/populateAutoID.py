#!/usr/bin/env python3
"""
populateAutoID.py
=================

Check all auto-id projects and create new transfer requests for each. This functionality will remove the need to use Assign simply based on patient naming convention. Regular safety and quality control phantom scans might use this process to automate the forward of such cases to research PACS.

- user: processing
- depends-on:
  - REDCap AutoID marked projects
- log-file:
  - ${SERVERDIR}/logs/populateAutoID.log
- pid-file: ${SERVERDIR}/.pids/populateAutoID.pid
- start: 
  */1 * * * *  /usr/bin/flock -n /home/processing/.pids/populateAutoID.pid /home/processing/bin/populateAutoID.py >> /home/processing/logs/populateAutoID.log 2>&1

Notes
-----

If used projects that are the target of automatic transfers should be regularly screened. Data forwarded on error to such projects should be deleted from research PACS.

"""


import pycurl, hashlib, io, re, datetime, argparse, os, time, sys
import tempfile, shlex, shutil, subprocess
from urllib.parse import urlencode

# we want to find all json files in our directory tree
import glob, json

parser = argparse.ArgumentParser(description='Create transfer requests based on auto-id')
parser.add_argument("--importAll", type=str, default=None, help='---')
args = parser.parse_args()

# either we try to update all entries
# or we only update entries that are new (series that are new)
modeRewriteAll = False
modeRewriteProject = ""
if args.importAll != None:
    modeRewriteAll = True
    modeRewriteProject = args.importAll

print("%s: [populateAutoID.py] start" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))


def getAutoIDEnabled():
    # get the list of projects that have auto-id enabled
    token = '921AD1F8B4ADA41EA7A05696888CC83D'
    buf = io.BytesIO()
    data = {
            'token': token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'fields[0]': 'project_use_autoid',
            'fields[1]': 'record_id',
            'fields[2]': 'project_autoid_aetitle',
            'fields[3]': 'project_name',
            'fields[4]': 'project_patient_naming',
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
    ch.perform()
    ch.close()
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    data = []
    for q in qdata:
        if (q['project_use_autoid'] == '1') and (q['project_autoid_aetitle'] != ''):
            data.append(q)
    return data
    

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
    print("%s: [populateAutoID.py] INFO %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),buf.getvalue()))
    buf.close()
    

def getIncomingData( autoid_projects ):
    # only get the latest incoming data, we need to know if a transfer request has already been created
    # to speed up the request lets try to use a dateRangeBegin of 2017-01-01 00:00:00
    buf = io.BytesIO()
    # use a date 14 days in the past (to limit the amount of data requested from REDCap)
    today = datetime.datetime.now()
    inpast = today - datetime.timedelta(days=14)
    
    data = {
            'token': '82A0E31C415BF2215EBC3DC968616CD5',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'fields[0]': 'study_aetitle_addressed',
            'fields[1]': 'study_instance_uid',
            'fields[2]': 'transfer_project_name',
            'fields[3]': 'study_patient_id',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json',
            'dateRangeBegin': inpast.strftime("%Y-%m-%d %H:%M:%S")
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
    qdata = []
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    # ok, we get a mess back here, basically the study instance uids repeat once for each instrument
    # we therefore need to sort through this first
    studyInstanceUIDs = {}
    for q in qdata:
        studyInstanceUIDs[q['study_instance_uid']] = 1
    studyInstanceUIDs = studyInstanceUIDs.keys()
    data = []
    for s in studyInstanceUIDs:
        study_aetitle_addressed = ''
        study_instance_uid = s
        transfer_project_name = ''
        study_patient_id = ''
        for q in qdata:
            if q['study_instance_uid'] == study_instance_uid:
                if ('study_aetitle_addressed' in q) and (q['study_aetitle_addressed'] != ''):
                    study_aetitle_addressed = q['study_aetitle_addressed']
                if ('transfer_project_name' in q) and (q['transfer_project_name'] != ''):
                    transfer_project_name = q['transfer_project_name']
                if ('study_patient_id' in q) and (q['study_patient_id'] != ''):
                    study_patient_id = q['study_patient_id']
        if transfer_project_name == '':
            if study_aetitle_addressed in autoid_projects:
               data.append({
                   'study_instance_uid': study_instance_uid,
                   'transfer_project_name': transfer_project_name,
                   'study_aetitle_addressed': study_aetitle_addressed,
                   'study_patient_id': study_patient_id
               })
    return data


# create a new transfer request for that study - assume that the patient is used as patientID patientName
# this call is only be made when we see a series in this study the first time. That means we can safely create
# a transfer request without checking first if one already exists.
def createNewTransferRequest( studyInstanceUID, target_project, patient, event):
    try:
        studyInstanceUID = studyInstanceUID.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass
    try:
        target_project = target_project.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass
    try:
        patient = patient.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass
    try:
        event = event.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass
    
    dat = {
        'study_instance_uid': studyInstanceUID,
        'redcap_repeat_instance': 1,
        'redcap_repeat_instrument': 'transfers',
        'transfer_requested_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'transfer_project_name': target_project,
        'transfer_name': patient
    }
    if event != '':
        dat['transfer_event_name'] = event
    print("%s: [populateAutoID.py] INFO %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),dat))
    updateREDCap( [ dat ] )


def getExistingAutoIDs( project_name ):
    # from REDCap get a list of all previously generated auto ids
    print("%s: [populateAutoID.py] INFO REQUEST IDS for %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), project_name))
    buf = io.BytesIO()
    data = {
            'token': 'CCBD47E1698254A9C9231D5F36C37627',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'forms[0]': 'autoid',
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
    ch.perform()
    ch.close()
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    data = []
    for q in qdata:
        #print("check for %s and %s in get" % (q['autoid_project_name'], project_name))
        if q['autoid_project_name'] == project_name:
            data.append(q)
    return data
    
def addToAutoIDTable( data_add ):
    # generate a new record_id in the autoid table and store the data
    buf = io.BytesIO()
    data = {
            'token': 'CCBD47E1698254A9C9231D5F36C37627',
            'content': 'generateNextRecordName'
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
    new_record_id = int(buf.getvalue())
    buf.close()
    # add the new id to the data_add
    data_add['record_id'] = new_record_id
    print("%s: [populateAutoID.py] Info: new record id %d for autoid table %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), new_record_id, json.dumps(data_add)))
    buf = io.BytesIO()
    data = {
            'token': 'CCBD47E1698254A9C9231D5F36C37627',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'data': json.dumps([data_add]),
            'overwriteBehavior': 'normal',
            'forceAutoNumber': 'false',
            'returnContent': 'count',
            'returnFormat': 'json',
            'record_id': hashlib.sha1().hexdigest()[:16]
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    print("%s: [populateAutoID.py] INFO %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
    buf.close()


autoid_projects_data = getAutoIDEnabled()
autoid_projects = [x['project_autoid_aetitle'] for x in autoid_projects_data]
incomingData = getIncomingData( autoid_projects )
# with the information from Incoming we don't need to look at the raw json files anymore
print("%s: [populateAutoID.py] INFO Incoming data: %d" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(incomingData)))
print("%s: [populateAutoID.py] INFO %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), autoid_projects_data))

# for each project we have in incomingData we need to create an ids file and call gen-id
project_names = {}
for kq in range(0,len(incomingData)):
    q = incomingData[kq]
    n = q['study_aetitle_addressed']
    found = False
    for u in autoid_projects_data:
        if u['project_autoid_aetitle'] == n:
            found = True
            project_names[n] = 1
            incomingData[kq]['project_name'] = n
            break

project_names = list(project_names.keys())

# now we want to fill in the key ... into incomingData, either the ID exists already for this participant or we create a new one
for project_name in project_names:
    #print(project_name)
    # the pattern that should be used for this project
    project_patient_naming = ''
    project_real_name = ''
    for q in autoid_projects_data:
        if q['project_autoid_aetitle'] == project_name:
            project_patient_naming = str(q['project_patient_naming'])
            project_real_name = str(q['project_name'])
    print("%s: [populateAutoID.py] INFO the rule for this project (%s) naming is \"%s\" from autoid_projects_data %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), project_name, project_patient_naming, json.dumps(autoid_projects_data)))
    
    existingIDs = getExistingAutoIDs(project_real_name)
    for kq in range(0,len(incomingData)):
       q = incomingData[kq]
       if q['project_name'] != project_name:
           continue
       hash = hashlib.sha512(q['study_patient_id'].encode('utf-8')).hexdigest()
       #print("CHECK EXISTING IDS for %s in %s" % (hash, json.dumps(existingIDs)))
       for qq in existingIDs:
           #print("check if hash exists already with %s and %s" % (hash, qq['autoid_hash']))
           if hash == qq['autoid_hash']:
               # found an existing entry for this hash, store in incomingData
               incomingData[kq]['suggested_transfer_id'] = qq['autoid_value']
               incomingData[kq]['suggested_transfer_hash'] = hash
               print("%s: [populateAutoID.py] INFO this id %s does already exist as %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), q['study_patient_id'], qq['autoid_value']))
               break
    # we still need to create new ids for new patients, we can check for the suggested_transfer_id now
    #print(json.dumps(incomingData))
    # lets dump those known IDs into a temporay file for gen-id
    with tempfile.NamedTemporaryFile() as fp:
        #print('write into temporary file named %s' % (fp.name))
        for q in existingIDs:
            fp.write(str(q['autoid_value'] + "\n").encode('utf-8'))
        for kq in range(0,len(incomingData)):
            q = incomingData[kq]
            if q['project_name'] != project_name:
                continue
            if 'suggested_transfer_id' in q:
                print("%s: [populateAutoID.py] INFO ignore this entry, there is already a suggested transfer id" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
                continue
            # request a name for this unknown entry
            hash = hashlib.sha512(q['study_patient_id'].encode('utf-8')).hexdigest()
            print("%s: [populateAutoID.py] INFO request name for %s using hash %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), q['study_patient_id'], hash))
            cmd = "/bin/bash -c \"/home/processing/bin/gen-id/gen-id.py -r '%s' -e %s -a\"" % (project_patient_naming, fp.name)
            cmd = shlex.split(cmd)
            #print(cmd)
            new_id = ''
            try:
                new_id = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print("%s: [populateAutoID.py] ERROR Error running gen-id, did not got a new id. %d, %s, %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e.returncode, e.output, cmd))
                new_id = ''
                continue
            # because the ID is genreated on the output line we need to trim it
            new_id = new_id.rstrip()
            # as a sanity check the generated I Dneeds to fit the pattern
            if not re.match(str(project_patient_naming).encode('utf-8'), new_id):
                print("%s: [populateAutoID.py] ERROR ID is BAD, %s does not match with %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), new_id, project_patient_naming))
                continue
            incomingData[kq]['suggested_transfer_id'] = new_id
            incomingData[kq]['suggested_transfer_hash'] = hash
            incomingData[kq]['suggested_transfer_id_exists'] = 0

    # now we have everything together in incomingData
    for kq in range(0,len(incomingData)):
        q = incomingData[kq]
        if q['project_name'] != project_name:
            continue
        if (not 'suggested_transfer_id' in q) or (q['suggested_transfer_id'] == ''):
            print("%s: [populateAutoID.py] ignore this entry , there is already a suggested transfer id" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
            continue
        # mark the name in the autoid table if it does not exist yet
        if ('suggested_transfer_id_exists' in q) and (q['suggested_transfer_id_exists'] == 0):
            data = {
                'autoid_project_name': str(project_real_name),
                'autoid_hash': str(q['suggested_transfer_hash']),
                'autoid_value': q['suggested_transfer_id'].decode('utf-8'),
                'autoid_method': 1
            }
            print("%s: [populateAutoID.py] Add to autoID table: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),json.dumps(data)))
            addToAutoIDTable( data )
        print("%s: [populateAutoID.py] INFO create a transfer request for %s %s %s %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), q['study_instance_uid'], q['project_name'], project_real_name, q['suggested_transfer_id'], q['suggested_transfer_hash']))
        createNewTransferRequest( q['study_instance_uid'], project_real_name, q['suggested_transfer_id'], '' )

        
print("%s: [populateAutoID.py] end" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
