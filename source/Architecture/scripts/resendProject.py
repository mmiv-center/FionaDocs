#!/usr/bin/env python3
"""
resendProject.py
================

Check all transfer requests (request date and transfer date). Generate transfer requests if the request date is newer than the transfer date.

- user: processing
- depends-on:
  - /home/processing/transfer_requests/,
- log-file:
  - ${SERVERDIR}/logs/resendProject.log,
- pid-file: 
- start:
  1 * * * * /home/processing/bin/utils/resendProject.py >> /home/processing/logs/resendProject.log 2>&1


Notes
-----

If run from the command line with the --importAll InstitutionName (project name) all transfer requests of this project will get a
new /home/processing/transfer_requests/ entry regardless of transfer date.

"""


import pycurl, hashlib, io, re, datetime, argparse
from urllib.parse import urlencode

import glob, json

parser = argparse.ArgumentParser(description='Create outstanding transfer request documents based on timing of previous send dates')
parser.add_argument("--importAll", type=str, default=None, help='generate transfer requests for a specific project (all routing rules that are active, transfer request should be missing)')
args = parser.parse_args()

# either we try to update all entries
# or we only update entries that are new (series that are new)
modeRewriteProject = ""
if args.importAll != None:
    modeRewriteProject = args.importAll

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
    print("%s: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), buf.getvalue()))
    buf.close()

def getAllTransferRequests( target_project ):
    token = '82A0E31C415BF2215EBC3DC968616CD5'
    buf = io.BytesIO()
    
    data = {
        'token': token,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'forms[0]': 'transfers',
        'forms[1]': 'incoming_studies',
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
    # print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except json.decoder.JSONDecodeError:
        qdata = []
    buf.close()
    data = []
    # only return transfer requests that have been send before and dates that are newer
    for q in qdata:
        if (target_project != '') and (q['transfer_project_name'] != target_project):
            continue
        if (q['transfer_date'] != '') and (q['transfer_requested_date'] != ''):
            # check the dates
            date1 = datetime.datetime.strptime(q['transfer_date'], '%Y-%m-%d %H:%M')
            date2 = datetime.datetime.strptime(q['transfer_requested_date'], '%Y-%m-%d %H:%M')
            if date1 > date2:
                continue
            data.append(q)
    return data

request_dir = '/home/processing/transfer_requests/'
transfers = getAllTransferRequests( modeRewriteProject )

print("%s: [resendProject.py] We have %d transfer requests" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(transfers)))
count = 0
for t in transfers:
    if t['transfer_project_name'] == "":
        continue
    if t['transfer_name'] == "":
        continue
    # only if we have all the information we attempt to transfer the study
    # lets create a filename that is unique for this transfer
    fname="%s/%s_%s_%s_%d.json" % (request_dir,t['study_instance_uid'],t['transfer_project_name'],t['transfer_name'],t['redcap_repeat_instance'])
    # print(fname)
    with open(fname, 'w') as outfile:
            json.dump(t, outfile, indent=2, sort_keys=True)
    count = count + 1
print("%s: [resendProject.py] Created %s transfer requests done." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), count))
