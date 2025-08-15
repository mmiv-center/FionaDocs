#!/usr/bin/env python3
"""
populateProjects.py
===================

Each study that has been forwarded to PACS should appear in its own REDCap project. Get a list of all transferred studies from REDCaps Incoming project (Transfers table). Get a token for the project and add the entry - if it does not exist yet. For information to appear in the Imaging instrument set it up as a repeating instrument for "Event 1" (not a repeating event).


- user: processing
- depends-on:

  - InstitutionName specific REDCap project (repeating instrument Imaging for "Event 1")
  - REDCap Projects table of projects with API key

- log-file:

  - ``${SERVERDIR}/logs/populateProjects.log``

- pid-file: ``${SERVERDIR}/.pids/populateProjects.pid``
- start:

    .. code-block:: bash

       */1 * * * *  /usr/bin/flock -n /home/processing/.pids/populateProjects.pid /home/processing/bin/populateProjects.py >> /home/processing/logs/populateProjects.log 2>&1

Notes
------

TODO: Without calling for specific projects does not work anymore. We need to get a list of all imaging projects and run them project by project.


"""



import pycurl, hashlib, io, datetime, sys, argparse
from urllib.parse import urlencode
from pathlib import Path

# we want to get all entries from REDCap
import glob, json

print("%s: [populateProjects.py] start" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
sys.stdout.flush()

parser = argparse.ArgumentParser(description='Populate a projects Imaging instrument')
parser.add_argument("--project", type=str, default=None, help='---')
args = parser.parse_args()

limitToProject = None
if args.project != None:
    print("%s: [populateProjects.py] Limit processing to project \"%s\"" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), args.project))
    limitToProject = args.project


def sendToREDCap(token, vals, site):
    # TODO: remove duplicates from the vals based on record id and event name
    cache_tmp = []
    good_data = []
    for d in vals:
        key = "%s-%s" % (d['record_id'], d['redcap_event_name'])
        if not(key in cache_tmp):
            cache_tmp.append(key)
            good_data.append(d)

    buf = io.BytesIO()

    data = {
        'token': token,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': json.dumps(good_data),
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
    if 'error' in str(buf.getvalue()):
        print("Data producing the error: %s" % (json.dumps(vals)))
    print("%s: [populateProjects.py] SITE %s: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), site, buf.getvalue()))
    buf.close()


# return a list of all existing field names in the Imaging instrument
def validImagingFields(token):
    buf = io.BytesIO()
    data = {
        'token': token,
        'content': 'metadata',
        'format': 'json',
        'returnFormat': 'json',
        'forms[0]': 'imaging'
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
    data = json.loads(buf.getvalue())
    buf.close()
    ret = []
    for d in data:
        ret.append(d["field_name"])
    return ret

def chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

# test if study entry exists already in that project
def updateStudyInProject(token, data2, site):
    list_of_existing_fields = validImagingFields(token)

    # query all existing studies for the participants
    participantList = {}
    for d in data2:
        participantList[d['record_id']] = 1
    participantList = list(participantList.keys())
    # print("participant LIST: %s" % (json.dumps(participantList)))
    # TODO, if there are too many studies in a project we should chunk this
    # for about 20 of each

    buf = io.BytesIO()
    data = {
        'token': token,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'events[0]': 'event_1_arm_1',
        'field[0]': 'img_study_instance_uid',
        'field[1]': 'img_event_name',
        'field[2]': 'img_study_date',
        'field[3]': 'record_id',
        'field[4]': 'img_study_description',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    if "img_incoming_accession_number" in list_of_existing_fields:
        data['field[5]'] = "img_incoming_accession_number"

    # add the records we need data from
    for idx, participant in enumerate(participantList):
        # print("   ADD entry %d as %s" % (idx, participant))
        data["record[%d]" % idx] = participant
    # print("request: %s" % json.dumps(data))
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
        print("%s: [populateProjects.py] Error: updateStudyInProject could not get data from REDCap, JSONDecodeError, %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str(buf.getvalue())))
    buf.close()
    #print("got: %s" % (json.dumps(qdata)))
    # print("we got the following info for BBSC: %s" % json.dumps(qdata))
    # we need to filter by the record_id, the above call does not return for record_id only
    newInstancesPerRecord = {}
    results = []
    #print("data2: %s" % (json.dumps(data2)))
    for dat in data2:
        # we handle the current participant and study_instance_uid
        studyExists = False
        studyInstanceUID = dat['img_study_instance_uid']
        #studyDescription = dat['img_study_description']
        participant = dat['record_id']
        redcap_repeat_instances = []
        for dat2 in qdata:
            if not('record_id' in dat2):
                print("%s: [populateProjects.py] Error: expected record_id in dat2" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
                continue

            if participant != dat2['record_id']: # ignore this entry
                continue

            if isinstance(dat2['redcap_repeat_instance'], int):
                redcap_repeat_instances.append(dat2['redcap_repeat_instance'])
            # see if we have that study instance uid already
            if dat2['img_study_instance_uid'] == studyInstanceUID:
                # print("This study exists already in the imaging instrument")
                studyExists = True

        if not(studyExists):
            # this is a new study, we should add
            # print(" We found a new study, needs to be added as a new repeat instance")
            result = {}
            result['record_id'] = participant
            result['redcap_event_name'] = dat['redcap_event_name']
            result['redcap_repeat_instrument'] = "imaging"
            repeat_instance = 1
            if len(redcap_repeat_instances) > 0:
                repeat_instance = max(redcap_repeat_instances)+1
            if not(participant in newInstancesPerRecord):
                newInstancesPerRecord[participant] = -1
            newInstancesPerRecord[participant] = newInstancesPerRecord[participant] + 1
            result['redcap_repeat_instance'] = repeat_instance + newInstancesPerRecord[participant]
            result['img_study_instance_uid'] = studyInstanceUID
            result['img_event_name'] = dat['img_event_name']
            # TODO: dat2 does not exist here anymore
            if 'img_study_description' in dat:
                result['img_study_description'] = dat['img_study_description']
            if 'img_incoming_accession_number' in dat:
                result['img_incoming_accession_number'] = dat['img_incoming_accession_number']
            #result['img_study_description'] = studyDescription
            results.append(result)
            #print(" appending to results: %s" % (json.dumps(result)))
            #print("   data: %s" % (json.dumps(result)))
    # if we have to add more than one study we need to update the repeat instance number
    # to create a new one for each
    print("%s: [populateProjects.py] Project %s imaging new entries: %d" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), site, len(results)))
    if len(results) > 0:
        # chunk the send operation here
        ll = chunks(results,200)
        for chunk in ll:
            sendToREDCap(token, chunk, site)


def addStudyLevelInfo(transfer, token):
    valid_fields = validImagingFields(token)
    if 'study_instance_uid' in valid_fields and 'study_description' in valid_fields and 'img_incoming_accession_number' in valid_fields:
        # we can do something now
        pass
    else:
        # do nothing for this project
        return transfer


    # lookup all study_instance_uids in Incoming and extract the study description and the original accession number from there
    # update those fields in each of the transfers
    studyInstanceUIDs = []
    for t in transfer:
        if "study_instance_uid" in t:
            studyInstanceUIDs.append(t["study_instance_uid"])
    # get the unique keys
    studyInstanceUIDs = list(set(studyInstanceUIDs))

    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'field[0]': 'study_instance_uid',
        'field[1]': 'study_description',
        'field[2]': 'img_incoming_accession_number',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    for chunk in chunks(studyInstanceUIDs, 100):
        buf = io.BytesIO()
        data_tmp = data.copy()
        counter = 0
        for c in chunk:
            data_tmp["record[%d]" % counter] = c
            counter = counter + 1

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
        qdata = json.loads(buf.getvalue())
        buf.close()

        # now add qdata to the transfers
        for q in qdata:
            # find the correct transfer request
            for t in transfer:
                if t['study_instance_uid'] == q['study_instance_uid']:
                    if 'study_description' in t and 'study_description' in q:
                        t['study_description'] = q['study_description']
                    if 'img_incoming_accession_number' in t and 'img_incoming_accession_number' in q:
                        t['img_incoming_accession_number'] = q['img_incoming_accession_number']

    return transfer



# get sufficient information to identify what has been transferred and to where
# TODO: These transfers do not contain the study level information like study_description and Accession number of the incoming study.
def getAllTransfers(specific_project=None):
    buf = io.BytesIO()
    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'field[0]': 'study_instance_uid',
        'field[1]': 'transfer_request_date',
        'field[2]': 'transfer_date',
        'field[3]': 'transfer_error',
        'field[4]': 'transfer_project_name',
        'field[5]': 'transfer_name',
        'field[6]': 'transfer_mapped_uid',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    if specific_project != None:
        data['filterLogic'] = "[transfer_project_name]=\"%s\"" % (specific_project)
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
        print("%s: [populateProjects.py] Error: getAllTransfers could not get data from REDCap, JSONDecodeError %s called %s, return value: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str(buf.getvalue()), json.dumps(data), str(buf.getvalue())))
    buf.close()
    #print(qdata)
    return qdata

# get a list of active projects and their tokens
def getProjects():
    buf = io.BytesIO()
    data = { # get info from the DataTransferProjects project
        'token': '921AD1F8B4ADA41EA7A05696888CC83D',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'field[0]': 'record_id',
        'field[1]': 'project_name',
        'field[2]': 'project_token',
        'field[3]': 'project_active',
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
    qdata = json.loads(buf.getvalue())
    buf.close()
    data = []
    for d in qdata:
        if d['project_active'] == '1' and d['project_name'] != '' and d['project_token'] != '':
            data.append(d)
    return data


print("%s: [populateProjects.py] get projects and transfers..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
sys.stdout.flush()
projects = getProjects()
# if we do not have a limitToProject we should call this a couple of times with the different project names
transfers = []
if limitToProject == None:
    for project in projects:
        print("%s: [populateProjects.py] pull for project \"%s\"..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), project['project_name']))
        t = getAllTransfers(project['project_name'])
        transfers.extend(t)
else:
    transfers = getAllTransfers(limitToProject)

print("%s: [populateProjects.py] get projects and transfers done, %d entries" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(transfers)))
sys.stdout.flush()

imagingProjects = { "projects": [] };
# TODO: lookup in DataTransferProjects the variable project_annotation_type
imaging_projects_path = "/home/processing/bin/imagingProjects.json"
p = Path(imaging_projects_path)
if p.is_file():
    with open(imaging_projects_path, 'r') as datafile:
        imagingProjects = json.load(datafile)

if limitToProject != None:
    imagingProjects = { "projects": [ limitToProject ] }
    # filter out all transfers that are not in that project
    t_tmp = []
    for transfer in transfers:
        if transfer['transfer_project_name'] == limitToProject:
            t_tmp.append(transfer)
    transfers = t_tmp

if len(imagingProjects['projects']) == 0:
    print("%s: [populateProjects.py] Error: could not find imagingProjects.json" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

# sort transfers by project and event
transferPerSite = {}
for transfer in transfers:
    if transfer['transfer_project_name'] == '':
        continue
    # create a key that is unique for the project and the event name
    kk = "%s_%s" % (transfer['transfer_project_name'], transfer['transfer_event_name'])
    transfer['site'] = transfer['transfer_project_name']
    if kk not in transferPerSite:
        transferPerSite[kk] = []
    transferPerSite[kk].append(transfer)

print("%s: [populateProjects.py] for each site..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
sys.stdout.flush()

# now for each project we can use one token to query redcap
for siteKey in transferPerSite.keys():
    # the site is always the same, but we can have different events
    #print("SITEKEY: %s" % (siteKey))
    site = transferPerSite[siteKey][0]['site']
    # get all the data for this token
    token = ''
    for u in projects:
        if u['project_name'] == site:
            token = u['project_token']
    if token == '':
        # skip because we did not find the project
        print("%s: [populateProjects.py] skip project %s, we did not find a token." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), site))
        continue
    else:
        # Plot the event name as well
        print("%s: [populateProjects.py] Work on project %s (%s)" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), site, siteKey))

    sys.stdout.flush()
    # add this participant to that tokens project
    data = []
    data2 = []
    ids = {}

    # add missing fields from the study level instrument in incoming
    for transfer in addStudyLevelInfo(transferPerSite[siteKey], token):

        redcap_event_name = 'event_1_arm_1'
        if ('transfer_event_name' in transfer) and (transfer['transfer_event_name'] != ''):
            redcap_event_name = "%s_arm_1" % ((transfer['transfer_event_name']).lower())
        # we add the correct keys to data and submit to that project
        d = { 'record_id' : transfer['transfer_name'],
              'redcap_event_name': redcap_event_name,
              'first_name': transfer['transfer_name'],
              'last_name': transfer['transfer_name'] }
        # we only want to append if this is a new entry
        if transfer['transfer_mapped_uid'] not in ids:
            data.append(d)
            ids[transfer['transfer_mapped_uid']] = 1
            # create a record for the study instance uid in IDS7
            data2.append( {
                'record_id': transfer['transfer_name'],
                'redcap_event_name': 'event_1_arm_1',
                'img_study_instance_uid': transfer['transfer_mapped_uid'],
                'img_event_name': redcap_event_name,
                'img_study_description': transfer['study_description']
            } )
    # send to redcap
    #if site == "XPHYSTEST":
    #    print("Data for REDCap is: %s" % (json.dumps(data2)))
    sendToREDCap(token, data, site)
    # We also want to fill in information to the 'imaging' spreadsheet
    # but only if that exists. That can have many studies for each participant
    # name and event name.
    #
    # Write: img_study_instance_uid
    #        img_event_name
    #        for event_name "event_1_arm_1"
    if site in imagingProjects["projects"]:
        #print("   data2 submitted to project %s is: %s" % (site, json.dumps(data2)))
        updateStudyInProject(token, data2, site)
    else:
        print("%s: [populateProjects.py] ERROR Site \"%s\" ignored, not in imagingProjects %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), site, imaging_projects_path))

print("%s: [populateProjects.py] end" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
