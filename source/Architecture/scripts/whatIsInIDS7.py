#!/usr/bin/env python3
"""
whatIsInIDS7.py
===============

Populate the WhatIsInIDS7 table in REDCap for a specific project using findscu. This script is part of a sequence of scripts: getAllPatients2.sh - parseAllPatients.sh - whatIsInIDS7.py.

- user: processing
- depends-on:
  - /tmp/parseAllPatients{projname}/
  - /tmp/pullStudies{projname}/
- log-file:
  - ${SERVERDIR}/logs/whatIsInIDS7{projname}.log,
- pid-file: ${SERVERDIR}/.pids/whatIsInIDS7{projname}.pid
- start: 
  */48 * * * * /usr/bin/flock -n /home/processing/.pids/getAllPatients2{projname}.pid /bin/bash -c "/home/processing/bin/utils/getAllPatients2.sh 10000 "{proejct}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1 \
  && /home/processing/bin/utils/parseAllPatients.sh "{projname}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1 \
  && /home/processing/bin/utils/whatIsInIDS7.py "{projname}" >> /home/processing/logs/whatIsInIDS7/whatIsInIDS7{projname}.log 2>&1"


Notes
-----

TODO: check if the number of study related series is correct (looks too large in Export app), seems to depend on --repeat findscu.


"""



import pycurl, glob, json, io, subprocess, datetime, hashlib, sys
from urllib.parse import urlencode


# depends on a previous run of getAllPatients and parseAllPatients 

# D7EEAFD0C83FA9BA81A5D427534A071E

def updateREDCap(vals):
    buf = io.BytesIO()
    
    data = {
        'token': 'D7EEAFD0C83FA9BA81A5D427534A071E',
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'overwrite',
        'forceAutoNumber': 'false',
        'data': json.dumps(vals),
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    ch = pycurl.Curl()
    #ch.setopt(ch.URL, 'https://10.94.209.30:4444/api/')
    ch.setopt(ch.URL, 'https://localhost:4444/api/')
    ch.setopt(ch.SSL_VERIFYHOST, False)
    #ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(pycurl.POST, 1)
    ch.setopt(pycurl.POSTFIELDS, urlencode(data))
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    print("%s: [whatIsInIDS7.py] send piece, got %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), buf.getvalue()))
    buf.close()

def getValue(entry, key):
    if not(key in entry):
        return ""
    entry = entry[key]
    a = ""
    if "Value" in entry:
        c = 0
        if len(entry["Value"]) > 0:
            a = ""
            for e in entry["Value"]:
                aa = ""
                if (type(e) is dict) and ("Alphabetic" in e):
                    aa = e["Alphabetic"]
                else:
                    aa = str(e)
                if c > 0:
                    a = a + "," + aa
                else:
                    a = a + aa
                c = c + 1
        else:
            a = entry["Value"]
    if (type(a) is dict) and ("Alphabetic" in a):
        a = a["Alphabetic"]
    return a
    
# if we have an argument for a project, only process data from that project
InstitutionName=""
if len(sys.argv) == 2:
    InstitutionName=sys.argv[1]

# parse all the studies
print("%s: [whatIsInIDS7.py] parse /tmp/pullStudies%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), InstitutionName))
files=glob.glob("/tmp/pullStudies%s/*/*" % (InstitutionName))
print("%s: [whatIsInIDS7.py] we found %d %s files..." % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), len(files), InstitutionName))
vals = []
datestamp=datetime.datetime.now().isoformat()
records = {}
usedStudyInstanceUIDs = {}
for file in files:
    # This is too slow.. need to make this faster to be able to read in all cases stored in research PACS.
    # So instead of calling dcmdump so many times calling dcm2json once might be an option.
    dicom_meta_tmp=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcm2json \"" + file + "\"", shell=True).strip()
    dicom_meta=json.loads(dicom_meta_tmp)
    StudyInstanceUID=getValue(dicom_meta, "0020000D")    
    PatientID=getValue(dicom_meta,"00100020")
    PatientName=getValue(dicom_meta,"00100010")
    StudyDescription=getValue(dicom_meta,"00081030")
    NumberOfStudyRelatedInstances=getValue(dicom_meta,"00201208")
    NumberOfStudyRelatedSeries=getValue(dicom_meta,"00201206")
    InstitutionName=getValue(dicom_meta,"00080080")
    ReferringPhysicianName=getValue(dicom_meta,"00080090")
    StudyDate=getValue(dicom_meta,"00080020")
    StudyTime=getValue(dicom_meta,"00080030")
    StudyID=getValue(dicom_meta,"00200010")
    ModalitiesInStudy=getValue(dicom_meta,"00080061")
    AccessionNumber=getValue(dicom_meta,"00080050")
    
    # check_output
    ##StudyInstanceUID=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"StudyInstanceUID\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    # check_output
    ##PatientID=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"PatientID\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##PatientName=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"PatientName\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##StudyDescription=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"StudyDescription\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##NumberOfStudyRelatedSeries=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"0020,1206\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##NumberOfStudyRelatedInstances=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"0020,1208\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##InstitutionName=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"0008,0080\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##ReferringPhysicianName=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"0008,0090\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##StudyDate=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"StudyDate\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##StudyTime=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"StudyTime\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    ##ModalitiesInStudy=subprocess.check_output("DCMDICTPATH=/usr/share/dcmtk/dicom.dic dcmdump +P \"ModalitiesInStudy\" " + file + " | cut -d'[' -f2 | cut -d']' -f1", shell=True).strip()
    # sanitize the outputs - in case there is no value
    #if b'no value available' in StudyDescription:
    #    StudyDescription=b''
    #if b'no value available' in PatientID:
    #    PatientID=b''
    #if b'no value available' in PatientName:
    #    PatientName=b''
    #if b'no value available' in StudyInstanceUID:
    #    StudyInstanceUID=b''
    #if b'no value available' in InstitutionName:
    #    InstitutionName=b''
    #if b'no value available' in StudyDate:
    #    StudyDate=b''
    #if b'no value available' in StudyTime:
    #    StudyTime=b''
    #if b'no value available' in ModalitiesInStudy:
    #    ModalitiesInStudy=b''
    #if StudyInstanceUID.decode("utf-8", "ignore") in records:
    #    continue
    #else:
    #    records[StudyInstanceUID.decode("utf-8", "ignore")] = 1
    #if b'no value available' in ReferringPhysicianName:
    #    ReferringPhysicianName=b''
    # store this entry, we can only store a single entry per studyinstanceuid.. why do we get more than one?

    a = { 'record_id': StudyInstanceUID,
          'ids7_patient_name': PatientName,
          'ids7_patient_id': PatientID,
          'ids7_study_description': StudyDescription,
          'ids7_number_of_series': int(NumberOfStudyRelatedSeries),
          'ids7_number_of_instances': int(NumberOfStudyRelatedInstances),
          'ids7_institution_name': InstitutionName,
          'ids7_referring_physician': ReferringPhysicianName,
          'ids7_study_time': StudyTime,
          'ids7_study_date': StudyDate,
          'ids7_study_id': StudyID,
          'ids7_accession_number': AccessionNumber,
          'ids7_modalities': ModalitiesInStudy,
          'ids7_date_stamp': datestamp }
    if StudyInstanceUID in usedStudyInstanceUIDs:
        #print(" DUPLICATION: %s\n%s" % (json.dumps(a), json.dumps(usedStudyInstanceUIDs[StudyInstanceUID])))
        # we should merge the two structures
        if usedStudyInstanceUIDs[StudyInstanceUID]["ids7_study_description"] == "":
            # if we have a missing study description, replace with one of the other ones
            usedStudyInstanceUIDs[StudyInstanceUID]["ids7_study_description"] = a["ids7_study_description"]
        usedStudyInstanceUIDs[StudyInstanceUID]["ids7_number_of_series"] += a["ids7_number_of_series"]
        usedStudyInstanceUIDs[StudyInstanceUID]["ids7_number_of_instances"] += a["ids7_number_of_instances"]
        # we could have a list of AccessionNumbers
        if usedStudyInstanceUIDs[StudyInstanceUID]["ids7_accession_number"] != "":
            san = [x.strip(' ') for x in usedStudyInstanceUIDs[StudyInstanceUID]["ids7_accession_number"].split(",")]
            if AccessionNumber.strip(' ') not in san:
                san.append(AccessionNumber)
                usedStudyInstanceUIDs[StudyInstanceUID]["ids7_accession_number"] = ",".join(san)
        continue # skip duplicates

    usedStudyInstanceUIDs[StudyInstanceUID] = a
    #print(a)
    #vals.append(a)
    if (len(usedStudyInstanceUIDs) % 200) == 0:
        print("%s: [whatIsInIDS7.py] progress %d of %d cases parsed" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), len(usedStudyInstanceUIDs), len(files)))
print("%s: [whatIsInIDS7.py] progress %d of %d cases parsed" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), len(usedStudyInstanceUIDs), len(files)))

# We might have records that appear more than once, we should remove any duplicates.
vals = list(usedStudyInstanceUIDs.values())

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
                        
# now store those values in REDCap
print("%s: [whatIsInIDS7.py] send %d %s entries to REDCap..." %  (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), len(vals), InstitutionName))
#print(json.dumps(vals))
for chunk in chunks(vals, 100):
    #print("%s: " % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), json.dumps(chunk)))
    updateREDCap(chunk)
