#!/usr/bin/env python3
"""
createTransferRequests.py
=========================

Create a transfer request json in ``/home/processing/transfer_requests`` based on all existing records in REDCap's Incoming project. If there is no transfer date yet for an Incoming study or, if the transfer date is before the newest series date (JSON modification date in ``/data/site/raw``) a new transfer request is created for anonymizeAndSend.py.

- user: processing
- depends-on:

  - anonymizeAndSend.py (processes files created in ``/home/processing/transfer_requests``)
  - REDCap https://localhost:4444/ (project Incoming, table TransferRequests)
  - Series level JSON files in: ``/data/site/raw/*/*/*.json``

- log-file:

  - ``${SERVERDIR}/logs/createTransferRequests.log``
- pid-file: ${SERVERDIR}/.pids/createTransferRequests.pid
- start:

.. code-block:: bash

   */1 * * * *  /usr/bin/flock -n /home/processing/.pids/createTransferRequests.pid /home/processing/bin/createTransferRequests.py >> /home/processing/logs/createTransferRequests.log 2>&1


"""


import pycurl, io, hashlib, datetime, os, glob
from urllib.parse import urlencode

# create request json files, each request should be fulfilled and marked as such in REDCap
import json

print("%s: [createTransferRequests.py] start processing" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

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
        'fields[1]': 'transfer_project_name',
        'fields[2]': 'transfer_name',
        'fields[3]': 'transfer_date',
        'fields[4]': 'transfer_requested_date',
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
    ch.perform()
    ch.close()
    #print(buf.getvalue())
    try:
        qdata = json.loads(buf.getvalue())
    except:
        print("%s: [createTransferRequests.py] ERROR could not get JSON from REDCap. Instead got: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), buf.getvalue()))
        qdata = []
    buf.close()
    # this should get us the redcap_repeat_instance as well
    return qdata


from pathlib import Path
import os

request_dir = '/home/processing/transfer_requests/'
transfers = getTransfers()
for t in transfers:
    #print(t)
    if t['transfer_date'] != "":
        # ok there is one special case here, if the date is not empty we are probably ok
        # but it could be that a new image series arrived after our current send date
        # in that case we want to send everything again (don't care if we send too much)
        # we will know if that is the case if we compare the transfer_date with the newest
        # date of *.json files in the raw folder for this study
        if os.path.exists("/data/site/raw/%s/" %  (t['study_instance_uid'])):
            oldest_time = 0
            for u in glob.iglob("/data/site/raw/%s/*.json" % (t['study_instance_uid'])):
                ti = os.path.getmtime(u)
                if oldest_time == 0:
                    oldest_time = ti
                else:
                    if ti > oldest_time:
                        oldest_time = ti
            last_send = datetime.datetime.strptime(t['transfer_date'], '%Y-%m-%d %H:%M')
            # TODO: In a special case that the transfer is still ongoing we could start sending again
            # too early. If the transfer of new images is still ongoing we should wait for 16 seconds
            # (trigger for finished study receive) before sending.
            if datetime.datetime.timestamp(last_send) < oldest_time:
                # send again
                print("%s: [createTransferRequests.py] New image series, send study %s again, newest series json: %s is after last transfer: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), t['study_instance_uid'], datetime.datetime.fromtimestamp(oldest_time), datetime.datetime.fromtimestamp( datetime.datetime.timestamp(last_send))) )
                #continue
            else:
                continue
        else:
            # ignore this entry, the transfer has already been done
            continue
    if t['transfer_project_name'] == "":
        continue
    if t['transfer_name'] == "":
        continue
    # only if we have all the information we attempt to transfer the study
    # lets create a filename that is unique for this transfer
    fname="%s/%s_%s_%s_%d.json" % (request_dir,t['study_instance_uid'],t['transfer_project_name'],t['transfer_name'],t['redcap_repeat_instance'])
    if not os.path.isfile(fname):
        with open(fname, 'w') as outfile:
            json.dump(t, outfile, indent=2, sort_keys=True)
        print("%s: [createTransferRequests.py] Wrote transfer request: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), json.dumps(t)))

print("%s: [createTransferRequests.py] end processing" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))

