#!/usr/bin/env python3
"""
whatIsNotInIDS7.py
==================

There is no docstring.

"""



import pycurl, glob, json, io, subprocess, datetime, hashlib, sys, requests, shlex
import time, argparse
from urllib.parse import urlencode

# We just check from the REDCap project WhatIsInIDS7 and delete
# any entries in there that do not exist anymore in the research
# PACS (using findscu).


parser = argparse.ArgumentParser(description='Remove all records from whatIsInIDS7 that do not exist in research PACS anymore')
parser.add_argument("-f", "--force", action='store_true', help='really remove and not just show what would be removed')
args = parser.parse_args()

force = False
if args.force:
    force = True

datestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
print("%s: [whatIsNotInIDS7.py] start" % (datestamp))
    
# def updateREDCap(vals):
#     buf = io.BytesIO()
    
#     data = {
#         'token': 'D7EEAFD0C83FA9BA81A5D427534A071E',
#         'content': 'record',
#         'format': 'json',
#         'type': 'flat',
#         'overwriteBehavior': 'normal',
#         'forceAutoNumber': 'false',
#         'data': json.dumps(vals),
#         'returnContent': 'count',
#         'returnFormat': 'json',
#         'record_id': hashlib.sha1().hexdigest()[:16]
#     }
#     ch = pycurl.Curl()
#     #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
#     ch.setopt(ch.URL, 'https://localhost:4444/api/')
#     ch.setopt(ch.SSL_VERIFYHOST, False)
#     #ch.setopt(ch.HTTPPOST, data.items())
#     ch.setopt(pycurl.POST, 1)
#     ch.setopt(pycurl.POSTFIELDS, urlencode(data))
#     ch.setopt(ch.WRITEFUNCTION, buf.write)
#     ch.perform()
#     ch.close()
#     print(buf.getvalue())
#     buf.close()

# pull all data from REDCap
# buf = io.BytesIO()

data = {
    'token': 'D7EEAFD0C83FA9BA81A5D427534A071E',
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'fields[0]': 'record_id',
    'fields[1]': 'ids7_patient_name',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}

# ch = pycurl.Curl()
# ch.setopt(ch.URL, 'https://localhost:4444/api/')
# ch.setopt(ch.SSL_VERIFYHOST, False)
# ch.setopt(pycurl.POST, 1)
# ch.setopt(pycurl.POSTFIELDS, urlencode(data))
# ch.setopt(ch.WRITEFUNCTION, buf.write)
# ch.perform()
# ch.close()
# data=json.loads(buf.getvalue())
# buf.close()

r = requests.post('https://10.94.209.30:4444/api/', data=data, verify=False)
data = r.json()
print("%s: [whatIsNotInIDS7.py] got: %d entries from whatIsInIDS7" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(data)))

todelete = {}
counter = 0
for dat in data:
    cmd = "/usr/bin/findscu -aet FIONA -aec DICOM_QR_SCP --study -k 0008,0052=SERIES -k \"(0020,000d)=%s\" -k \"(0020,000e)\"  vir-app5274.ihelse.net 7840" % (dat['record_id'])
    cmd = shlex.split(cmd)

    try:
        o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("%s: [whatIsNotInIDS7.py] An error occured during findscu call. Continuing with the next entry..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        o = e.output
        print(o)
        print(dat['record_id'])
        time.sleep(5)
        if "Refused: OutOfResources" in o.decode('utf-8'):
            print("%s: [whatIsNotInIDS7.py] ERROR the Research PACS is not responding - OutOfResources!. Ignore and continue to the next one" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        continue


    if "Refused: OutOfResources" in o.decode('utf-8'):
        print("%s: [whatIsNotInIDS7.py] the Research PACS is not responding - OutOfResources!. Ignore and continue to the next one" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        continue
    
    #studyExists=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic /usr/bin/findscu -aet FIONA -aec DICOM_QR_SCP --study -k 0008,0052=SERIES -k \"(0020,000d)=%s\" -k \"(0020,000e)\"  vir-app5274.ihelse.net 7840 2>&1 | grep \"SeriesInstanceUID\" | cut -d'[' -f2 | cut -d']' -f1 | sort | uniq | wc -l" % (dat['record_id']), shell=True).strip()
    #studyExists=subprocess.check_output(["grep \"SeriesInstanceUID\" | cut -d'[' -f2 | cut -d']' -f1 | sort | uniq | wc -l"], input=o.decode('utf-8'), text=True).strip()

    nu = o.decode('utf-8').count("SeriesInstanceUID")
    print('%s: [whatIsNotInIDS7.py] Got response from the Research PACS, counted %02d occurances of SeriesInstanceUID substring' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), nu))

    if nu == 0:
        #print("%s %s" % (dat['record_id'], dat['ids7_patient_name']))
        todelete[dat['record_id']] = 0
        # print("we have something: %s" % (json.dumps(todelete)))
    if counter % 100 == 0:
        print(".", end='', flush=True)
    counter = counter + 1
    time.sleep(0.05)

print("%s: [whatIsNotInIDS7.py] got %d entries to delete" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), len(list(todelete.keys()))))

if force:
    # chunk and remove 200 at a time
    todel = list(todelete.keys())

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]    
    
    for dat in chunks(todel, 200):
        # buf = io.BytesIO()
        
        data = {
            'token': 'D7EEAFD0C83FA9BA81A5D427534A071E',
            'action': 'delete',
            'content': 'record',
            'returnFormat': 'json'
        }
        counter = 0
        for d in dat:
            data["records[%d]" % (counter)] = d
            counter = counter + 1

        print("%s: [whatIsNotInIDS7.py] %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), json.dumps(data)))
        # and send out

        # ch = pycurl.Curl()
        # ch.setopt(ch.URL, 'https://localhost:4444/api/')
        # ch.setopt(ch.SSL_VERIFYHOST, False)
        # ch.setopt(pycurl.POST, 1)
        # ch.setopt(pycurl.POSTFIELDS, urlencode(data))
        # ch.setopt(ch.WRITEFUNCTION, buf.write)
        # ch.perform()
        # ch.close()
        # print(buf.getvalue())
        # buf.close()
        r = requests.post('https://fiona.ihelse.net:4444/api/',data=data, verify=False)
        print("%s: [whatIsNotInIDS7.py] HTTP Status: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str(r.status_code)))
        print("%s: [whatIsNotInIDS7.py] %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), r.text))
        time.sleep(1)
        
else:
    print("%s: [whatIsNotInIDS7.py] Do nothing for: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), json.dumps(list(dict.keys(todelete)))))

datestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
print("%s: [whatIsNotInIDS7.py] done" % (datestamp))
