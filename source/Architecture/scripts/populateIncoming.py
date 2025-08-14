#!/usr/bin/env python3
"""
populateIncoming.py
===================

Fills in the Study and Series information in the Incoming table in REDCap. If a CouplingList entry exists its also adding a TransferRequest so that anonymizeAndSend can do its job.

- user: processing
- depends-on:
  - REDCap Incoming project
  - REDCap project "Projects" routing rules table
  - REDCap CouplingList project
- log-file:
  - ${SERVERDIR}/logs/populateIncoming.log
- pid-file: ${SERVERDIR}/.pids/populateIncoming.pid
- start:
  */1 * * * *  /usr/bin/flock -n /home/processing/.pids/populateIncoming.pid /home/processing/bin/populateIncoming.py >> /home/processing/logs/populateIncoming.log 2>&1

Notes
-----

TODO: support a new CouplingList entry even if there is already a TransferRequest done.


"""

import pycurl, hashlib, io, re, datetime, argparse, os, time
from urllib.parse import urlencode

# we want to find all json files in our directory tree
import glob, json

parser = argparse.ArgumentParser(description='Populate the incoming REDCap project')
parser.add_argument("--importAll", type=str, default=None, help='generate transfer requests for a specific project (all routing rules that are active, transfer request should be missing)')
args = parser.parse_args()

# either we try to update all entries
# or we only update entries that are new (series that are new)
modeRewriteAll = False
modeRewriteProject = ""
if args.importAll != None:
    modeRewriteAll = True
    modeRewriteProject = args.importAll

start_time = datetime.datetime.now()
print("%s: [populateIncoming.py] populateIncoming start" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
   
def getAllCouplingLists():
    token = '03BAEA1CCCEF8E89A44E16775FEA0109'
    buf = io.BytesIO()
    
    data = {
        'token': token,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
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
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    # print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    data = []
    # only return active routing rules
    for q in qdata:
        if q['cl_projectname'] != '':
            data.append(q)
    return data


def getAllRoutingRules():
    token = 'BEE3E9F1346C64B08807E0BD505703B4'
    buf = io.BytesIO()
    
    data = {
        'token': token,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
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
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    # print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    data = []
    # only return active routing rules
    for q in qdata:
        #print("Check if this rules is active: %s" % (json.dumps(q)))
        if q['routing_active'] == '1':
            data.append(q)

    # We also need to replace the value for the dropdown routing_dest_project with the text
    # written on the dropdown - only the label can have spaces and we need those for some
    # projects.
    buf = io.BytesIO()
    
    data2 = {
        'token': token,
        'content': 'metadata',
        'format': 'json',
        'returnFormat': 'json',
        'fields[0]': 'routing_dest_project'
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data2))
    ch.setopt(ch.SSL_VERIFYPEER, 0)
    ch.setopt(ch.SSL_VERIFYHOST, 0)
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()

    try:
        q2data = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        q2data = []
    buf.close()
    # parse the option list
    # "select_choices_or_calculations":"PECTMRI, PECTMRI | PAIM, PAIM | ECTMRI-DEID, ECTMRI-DEID | BRAINGUT, BRAINGUT | OFAMS, OFAMS | PBICAM, PBICAM | NAKKE, NAKKE | DISC, DISC | CervicalCancer, CervicalCancer | EndometrialCancer, EndometrialCancer | BackToBasic, BackToBasic | NOR-TEST, NOR-TEST | JMETAST, JMETAST | 8DISC, 8DISC | BPRGung, BPRGung | LGG, LGG | RAM-MS, RAM-MS | QC-NHPhantom, QC - NH Phantom | GenKOLS, GenKOLS | SAS-GKRS-trial-01, SAS-GKRS-trial-01 | LIDC-IDRI, LIDC-IDRI"
    paired_list = q2data[0]['select_choices_or_calculations'].split("|")
    paired_dict = { paired_list[i].split(",")[0].strip(): paired_list[i].split(",")[1].strip() for i in range(0,len(paired_list), 1) }
    # replace the option with the label version
    for idx, q in enumerate(data):
        if ('routing_dest_project' in q) and (q['routing_dest_project'] in paired_dict):
            #print("FOUND REPLACEMENT FOR DEST_PROJECT: %s is now \"%s\"" % (q['routing_dest_project'], paired_dict[q['routing_dest_project']]))
            data[idx]['routing_dest_project'] = paired_dict[q['routing_dest_project']]
    #print("routing rules are now: %s" % (json.dumps(data)))
    
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
    print("%s: [populateIncoming.py] INFO received from REDCap: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
    buf.close()
    

# all transfers, are those too many?
# TODO: This takes quite some time for each participant.
#       Better to pull transfers once and lookup from there.
def getTransfers(StudyInstanceUID):
    if len(StudyInstanceUID) == 0:
        print("%s: [populateIncoming.py] Error: only allow transfer requests with a known StudyInstanceUID" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        return []
    buf = io.BytesIO()
    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'rawOrLabel': 'raw',
        'records[0]': StudyInstanceUID,
        'fields[0]': 'study_instance_uid',
        'forms[0]': 'transfers',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    # print('request is now: %s' % (json.dumps(data)))
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
        print("%s: [populateIncoming.py] ERROR could not get JSON from REDCap. Instead got: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),buf.getvalue()))
        qdata = []
    buf.close()
    # this should get us the redcap_repeat_instance as well
    return qdata


    
# create a new transfer request for that study - assume that the patient is used as patientID patientName
# this call is only made when we see a series in this study the first time. That means we can safely create
# a transfer request without checking first if one already exists. TODO: change this so it works with already
# existing transfer requests (add one if its a new project or update if it already exists).
def createNewTransferRequest( studyInstanceUID, target_project, patient, event):
    # query for all existing transfer requests for this studyInstanceUID
    ts = getTransfers(studyInstanceUID)
    # print("getTransfers returned: \"%s\"\nDONE\n" % (json.dumps(ts)))
    # skip if we have this transfer request already
    foundAlready = False
    for t in ts:
        # print("check if %s %s %s in %s" % (target_project, patient, event, json.dumps(t)))
        if t['transfer_project_name'] == target_project and t['transfer_name'] == patient and t['transfer_event_name'] == event:
            foundAlready = True
            break
    if foundAlready:
        # ignore this transfer request, do not create a new one
        # print("%s ignore this transfer request, it exists already" % (datetime.datetime.now()))
        return
    else:
        print("%s: [populateIncoming.py] new transfer request for %s %s %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), studyInstanceUID, target_project, patient, event))
    # Next we want to find out if our current request exists already (overwrite with new data in tranfers requests).
    # If the request is new, increase the redcap_repeat_instance and submit a new request (keeping the old transfer).
    last_repeat_instance = 0
    for t in ts:
        if t['redcap_repeat_instance'] != "" and t['redcap_repeat_instance'] > 0:
            if last_repeat_instance < t['redcap_repeat_instance']:
                last_repeat_instance = t['redcap_repeat_instance']

    # This does not work as expected because the overwrite mode is 'normal', if a request already exists it will not be
    # overwritten.
    dat = {
        'study_instance_uid': studyInstanceUID,
        'redcap_repeat_instance': last_repeat_instance+1,
        'redcap_repeat_instrument': 'transfers',
        'transfer_requested_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'transfer_project_name': target_project,
        'transfer_name': patient
    }
    if event != '':
        dat['transfer_event_name'] = event
    print("%s: [populateIncoming.py] update REDCap with: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), json.dumps(dat)))
    updateREDCap( [ dat ] )

    
def createNewStudyInstanceUID(vals):
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
    print("%s: [populateIncoming.py] received from REDCap: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
    buf.close()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    

# return a dictionary of studyInstanceUID related values
def getDataForStudyInstanceUIDs(ar):
    qdata = {}
    # query REDCap in chunks to speed up processing without inflicting pain
    for chunk in chunks(ar,50):    
        buf = io.BytesIO()
        data = {
            'token': '82A0E31C415BF2215EBC3DC968616CD5',
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }
        for s in range(len(chunk)):
            data["records[%d]" % s] = chunk[s];
        #print(json.dumps(data))
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
            q = json.loads(buf.getvalue())
            for s in q:
                if not('study_instance_uid' in s):
                    continue
                if not(s['study_instance_uid'] in qdata):
                    qdata[s['study_instance_uid']] = []
                qdata[s['study_instance_uid']].append(s)               
        except json.decoder.JSONDecodeError:
            pass
        buf.close()
        #print(qdata)
    return qdata

def getDataForStudyInstanceUID(StudyInstanceUID):
    buf = io.BytesIO()
    data = {
        'token': '82A0E31C415BF2215EBC3DC968616CD5',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'records[0]': StudyInstanceUID,
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
    #print(qdata)
    return qdata


routing = getAllRoutingRules()
print("%s: [populateIncoming.py] populateIncoming after getAllRoutingRules" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
coupling = getAllCouplingLists()
print("%s: [populateIncoming.py] populateIncoming after getAllCoupingLists" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
#print(routing)
files = glob.glob('/data/site/raw/*/*.json')

# sort series by study instance uid
db = {}
print("%s: [populateIncoming.py] process %d series..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(files)))
for file in files:
    # we need to be careful here, we don't want to touch a series too early, so if the json file is too new
    # in that case the data is still transferred and we should wait for the next iteration
    try:
        tstamp = os.path.getmtime(file)
    except OSError:
        print("%s: [populateIncoming.py] ERROR Path '%s' does not exist or is inaccessible" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),file))
        continue
    tnow = time.time()
    # don't use this file is its younger than 1 minute
    if (tnow - tstamp) < (1*60):
        print("%s: [populateIncoming.py] INFO wait a bit for '%s', file is still being changed (%ds)" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), file, (tnow - tstamp)))
        continue
    
    with open(file, 'r') as myfile:
        data = json.load(myfile)
    if not data['StudyInstanceUID'] in db.keys():
        db[data['StudyInstanceUID']] = list()
    db[data['StudyInstanceUID']].append(data)
    #print("%s candidate study %s" % (datetime.datetime.now(),data['StudyInstanceUID']))

print("%s: [populateIncoming.py] populateIncoming after building db" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

# ok, we have the database filled in, all series for all files
# for each study we now need to find out if the data is already in REDCap
# if its not in there, we can add them.
# pull the info for all studyInstanceUID keys at once
suiddata = getDataForStudyInstanceUIDs(list(db.keys()))
#print("got suiddata: %d" % (len(list(suiddata.keys()))))

print("%s: [populateIncoming.py] start processing %d study instance uids" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(db.keys())))
for studyInstanceUID in db.keys():
    # the data we want to send out
    data = db[studyInstanceUID]

    # Can we check for a new transfer request here? If we do this at the bottom
    # all image series that are already known are filtered out and we will not see
    # a second transfer request for another project (dual project data).
    # print("%s check %s for matching coupling list entries" % (datetime.datetime.now(), accession_number))
    try:
        accession_number = data[0]['AccessionNumber']
    except KeyError:
        accession_number = ""
    
    for coupling_entry in reversed(coupling):
        # check if the coupling list matches (use AccessionNumber or StudyInstanceUID)
        if (( len(coupling_entry['cl_accessionnumber'].strip()) > 0) and (accession_number == coupling_entry['cl_accessionnumber']) ) or ( (len(coupling_entry['cl_studyinstanceuid'].strip()) > 0) and (studyInstanceUID == coupling_entry['cl_studyinstanceuid'])):
            target_project = coupling_entry['cl_projectname']
            patient = coupling_entry['cl_subjectid']
            target_event_name = coupling_entry['cl_eventname']
            #print("coupling list entry matches with the following project: ", target_project, " Patientid:",
            #      patient, " event name: ", target_event_name)
            createNewTransferRequest( studyInstanceUID, target_project, patient, target_event_name )
    
    # the data that is already in REDCap
    # we need to combine different calls into one, this spams REDCap and will be slow and stop working if the number of calls per minute is larger than 800
    #if not(studyInstanceUID in suiddata):
    #    continue
    #qdata = getDataForStudyInstanceUID(studyInstanceUID)
    qdata = []
    if studyInstanceUID in suiddata:
        qdata = suiddata[studyInstanceUID]
    foundAlready = []
    # every series is in a repeating instrument, to add a new entry we have to know the last redcap_repeat_instance number
    maxRepeatInstance = 0
    for d in qdata:
        # we search for this series in data, if its there already we remove it, don't want to send this again
        # of course the series information could be different....
        # so we would like to send it again in some cases (to update all fields, maybe once a night?)
        # instead of deleting them we should keep them, but store the repeat instance to overwrite the information
        for q in data:
            if q['SeriesInstanceUID'] == d['series_instance_uid']:
                # we have a repeat instrument here for series, no transfer information
                
                # remember the repeat instance number for this series
                q['redcap_repeat_instance'] = d['redcap_repeat_instance']
                # remove this entry - if its not different
                foundAlready.append(q['SeriesInstanceUID'])
                if 'redcap_repeat_instance' in q:
                    if maxRepeatInstance < q['redcap_repeat_instance']:
                        maxRepeatInstance = q['redcap_repeat_instance']
                        #print("found new maxRepeatInstance: ", maxRepeatInstance)
    if not(modeRewriteAll) and len(foundAlready) > 0:
        #print("before filter %d" % (len(data)))
        #skipped_data = [d for d in data if d['SeriesInstanceUID'] in foundAlready]
        #print("Skipping these : %s" % (json.dumps([d['StudyInstanceUID'] for d in skipped_data])))
        data = [d for d in data if d['SeriesInstanceUID'] not in foundAlready]
        #print("after filter %d" % (len(data)))

    # now send new data to REDCap (create the studies first)
    if len(data) == 0:
        continue
    plurals = ""
    if len(data)!=1:
        plurals = "s"
    print("%s: [populateIncoming.py] process with %d record%s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(data), plurals))
    
    try:
        study_description = data[0]['StudyDescription']
    except KeyError:
        study_description = ""
    try:
        accession_number = data[0]['AccessionNumber']
    except KeyError:
        accession_number = ""
    try:
        study_date = data[0]['StudyDate']
    except KeyError:
        study_date = ""
    try:
        study_time = data[0]['StudyTime']
    except KeyError:
        study_time = ""
    try:
        study_institution_name = data[0]['InstitutionName']
    except KeyError:
        study_institution_name = ""
    try:
        study_accession_number = data[0]['AccessionNumber']
    except KeyError:
        study_accession_number = ""
    try:
        patient_id = data[0]['PatientID']
    except KeyError:
        patient_id = ""
    try:
        patient_name = data[0]['PatientName']
    except KeyError:
        patient_name = ""
    try:
        aetitle_sender = data[0]['IncomingConnection']['AETitleCaller'].strip(' \t\x00')
    except KeyError:
        aetitle_sender = ""
    try:
        aetitle_addressed = data[0]['IncomingConnection']['AETitleCalled'].strip()
    except KeyError:
        aetitle_addressed = ""
    dat = []
    dat.append({ 'study_instance_uid': studyInstanceUID,
                 'study_description': study_description,
                 'study_date': study_date,
                 'study_time': study_time,
                 'study_institution_name': study_institution_name,
                 'study_patient_name': hashlib.sha256(patient_name.encode('utf-8')).hexdigest()[0:64],
                 'study_patient_id': hashlib.sha256(patient_id.encode('utf-8')).hexdigest()[0:64],
                 'study_aetitle_sender': aetitle_sender,
                 'study_accession_number': study_accession_number,
                 'study_aetitle_addressed': aetitle_addressed,
                 'study_arrival_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'incoming_studies_complete': 2
    })
    #print(dat[len(dat)-1])
    # now for every image series we want to add create another entry
    for d in data:
        try:
            series_instance_uid = d['SeriesInstanceUID']
        except KeyError:
            continue
        try:
            series_description = d['SeriesDescription']
        except KeyError:
            series_description = ""
        try:
            series_date = d['SeriesDate']
        except KeyError:
            series_date = study_date
        try:
            series_time = d['SeriesTime']
        except KeyError:
            series_time = study_time
        try:
            series_num_files = d['NumFiles']
        except KeyError:
            series_num_files = ""
        try:
            series_sequence_name = d['SequenceName']
        except KeyError:
            series_sequence_name = ""
        try:
            series_classify_types = json.dumps(d['ClassifyType'])
        except KeyError:
            series_classify_types = ""
        # we have two modes, we want to rewrite all entries, or we only want to update new entries
        # either the redcap_repeat_instance is always empty ( only new entries)
        # or we have copied the existing redcap_repeat_instance entry into the data array further up
        try:
            redcap_repeat_instance = d['redcap_repeat_instance']
        except KeyError:
            redcap_repeat_instance = maxRepeatInstance + 1
            maxRepeatInstance = maxRepeatInstance + 1
        dati = { 'study_instance_uid': studyInstanceUID,
                 'series_instance_uid': series_instance_uid,
                 'series_description': series_description,
                 'series_date': series_date,
                 'series_time': series_time,
                 'series_sequence_name': series_sequence_name,
                 'redcap_repeat_instrument': 'series',
                 'redcap_repeat_instance': redcap_repeat_instance,
                 'series_num_files': series_num_files,
                 'series_classify_types': series_classify_types,
                 'series_complete': 2
        }
        dat.append(dati)
    createNewStudyInstanceUID(dat)
    # do any of the routing rules apply?
    # if yes, create a transfer request
    # should we create a transfer request for all the image series?
    # we want to forward the whole study - instead of forwarding the series in dati
    routingMatches = False
    for route in routing:
        # print(route)
        if modeRewriteAll:
            if modeRewriteProject != route['routing_dest_project']:
                continue
        
        # all our rules are active (see reading in function)
        #print("%s We have a route here which is: %s" % (datetime.datetime.now(), json.dumps(route)))
        incoming_aetitle = route['routing_incoming_aetitle'].strip()
        sender_aetitle = route['routing_sending_aetitle'].strip()
        allowed_patientid = route['routing_allowed_patientid']
        allowed_patientname = route['routing_allowed_patientname']
        target_project = route['routing_dest_project']
        target_event_name = route['routing_event_name']
        match1 = False
        match2 = False
        match3 = False
        match4 = False
        if incoming_aetitle == aetitle_addressed:
            match1 = True
        if sender_aetitle == aetitle_sender:
            match4 = True
        # what anonymized name should we be using? The one mentioned in the route,
        # if both id and name are matched, use the id
        patient = ""
        if allowed_patientname != '' and re.match(allowed_patientname, patient_name):
            match3 = True
            patient = patient_name
        if allowed_patientid != '' and re.match(allowed_patientid, patient_id):
            match2 = True
            patient = patient_id

        #if studyInstanceUID == '1.2.840.113654.2.3.1995.3.0.6.2013102813464700000':
        #print('FOUND IT rule: ', route, " results in match for incoming_aetitle ",
        #          match1, " match for sending AETitle: ", match4, " match for patientid: ", match2, " and match for patient name: ",
        #          match3, " with the following settings: ", aetitle_addressed, " patientid:",
        #          patient_id, " patientname:", patient_name, " Target: ", target_project, " sender_aetitle: \"", sender_aetitle, "\" aetitle_sender: \"", aetitle_sender, "\"", sep='')
            
            
        # debug information
        if ((match1 == True) or (match4 == True)) and ((match2 == True) or (match3 == True)):
            print("%s: [populateIncoming.py] routing for rule: " % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')), route, " results in match for incoming_aetitle ",
                  match1, " match for patientid: ", match2, " and match for patient name: ",
                  match3, " with the following settings: ", aetitle_addressed, " patientid:",
                  patient_id, " patientname:", patient_name, " Target: ", target_project)
            createNewTransferRequest( studyInstanceUID, target_project, patient, target_event_name )
    #print("%s check %s for matching coupling list entries now" % (datetime.datetime.now(), accession_number))
    for coupling_entry in reversed(coupling):
        # check if the coupling list matches (use AccessionNumber or StudyInstanceUID)
        if  (( len(coupling_entry['cl_accessionnumber'].strip()) > 0) and (accession_number == coupling_entry['cl_accessionnumber']) ) or ( (len(coupling_entry['cl_studyinstanceuid'].strip()) > 0) and (studyInstanceUID == coupling_entry['cl_studyinstanceuid'])):
            # we found an entry
            target_project = coupling_entry['cl_projectname']
            patient = coupling_entry['cl_subjectid']
            target_event_name = coupling_entry['cl_eventname']
            #print("coupling list entry matches with the following project: ", target_project, " Patientid:",
            #      patient, " event name: ", target_event_name)
            createNewTransferRequest( studyInstanceUID, target_project, patient, target_event_name )
            # only submit to the first entry, but we could have several projects to submit to... TODO
            break

elapsed_time = datetime.datetime.now()-start_time
print("%s: [populateIncoming.py] populateIncoming end (%dsec)" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), elapsed_time.total_seconds()))
