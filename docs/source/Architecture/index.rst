ARCHITECTURE
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 0
   


Here is the complete data flow through the FIONA system, from initial DICOM reception to final transfer to research PACS.


.. mermaid::

   flowchart TB
   PACS["Clinical PACS - DICOM Source"]
   StoreSCP["storescpFIONA - DICOM SCP"]
   NamedPipe[("Named Pipe")]
   Arrived["Job Directory"]
   
   ProcessDaemon["processSingleFile3.py"]
   ClassifyRules["/data/config/classifyRules.json"]
   RawData["/data/site/raw/"]
   SymLinks["Symbolic Links"]
 
   DetectStudy["detectStudyArrival.sh"]
   StudyJob["Study Job Directory"]
   Anonymize["anonymize.sh"]
   Archive["/data/site/archive/"]
   
   AnonSend["anonymizeAndSend.py"]
   REDCap["REDCap API"]
   TransferReq["Transfer Requests"]
   
   SendFiles["sendFiles.sh"]
   Outbox["/data/outbox/"]
   ResPACS["Research PACS"]
   DAIC["/data/DAIC/"]
   
   PACS --> StoreSCP
   StoreSCP --> NamedPipe
   StoreSCP --> Arrived
   NamedPipe --> ProcessDaemon
   ProcessDaemon --> ClassifyRules
   ProcessDaemon --> RawData
   RawData --> SymLinks
   
   Arrived --> DetectStudy
   DetectStudy --> StudyJob
   SymLinks --> StudyJob
   StudyJob --> Anonymize
   Anonymize --> Archive
   
   Archive --> AnonSend
   REDCap --> AnonSend
   AnonSend -->TransferReq
   TransferReq --> SendFiles
   
   SendFiles --> Outbox
   Outbox --> ResPACS
   ResPACS --> DAIC
   %% Styling
   classDef externalSystem fill:#e1f5fe
   classDef configFile fill:#e1f5fe
   classDef dataDirectory fill:#f3e5f5
   classDef processScript fill:#fff3e0
   classDef tempData fill:#e8f5e8
   
   class PACS,REDCap,ResPACS externalSystem
   class ClassifyRules configFile
   class RawData,Archive,Outbox,DAIC dataDirectory
   class StoreSCP,ProcessDaemon,DetectStudy,Anonymize,AnonSend,SendFiles processScript
   class NamedPipe,Arrived,SymLinks,StudyJob,TransferReq tempData

Legend:

.. raw:: html

 <div style="display:flex;gap:20px;flex-wrap:wrap;">
  <span><span style="display:inline-block;width:32px;height:32px;background:#e1f5fe;border:1px solid #ccc;margin-right:5px;"></span>External Systems</span>
  <span><span style="display:inline-block;width:32px;height:32px;background:#f3e5f5;border:1px solid #ccc;margin-right:5px;"></span>Data Directories</span>
  <span><span style="display:inline-block;width:32px;height:32px;background:#fff3e0;border:1px solid #ccc;margin-right:5px;"></span>Scripts & Processes</span>
  <span><span style="display:inline-block;width:32px;height:32px;background:#e8f5e8;border:1px solid #ccc;margin-right:5px;"></span>Temporary Data</span>
  </div>
    <br><br>


Setup
-------

.. literalinclude:: config-example.json
   :language: json
   :linenos:
   :emphasize-lines: 3,5
   :caption: System configuration settings
   :name: config.json



Folder and File structure
--------------------------

.. raw:: html

   <pre>
   /home/processing/
   |          └── bin/
   │               ├── <a href="scripts/anonymizeAndSend.html">anonymizeAndSend.py</a>
   │               ├── <a href="scripts/clearExports.html">clearExports.sh</a>
   │               ├── <a href="scripts/clearOldFiles.html">clearOldFiles.sh</a>
   │               ├── <a href="scripts/clearStaleLinks.html">clearStaleLinks.sh</a>
   │               ├── <a href="scripts/createTransferRequestsForProcessed.html">createTransferRequestsForProcessed.py</a>
   │               ├── <a href="scripts/createTransferRequests.html">createTransferRequests.py</a>
   │               ├── <a href="scripts/populateAutoID.html">populateAutoID.py</a>
   │               ├── <a href="scripts/populateIncoming.html">populateIncoming.py</a>
   │               ├── <a href="scripts/populateProjects.html">populateProjects.py</a>
   │               └── utils/
   │                      ├── <a href="scripts/getAllPatients2.html">getAllPatients2.sh</a>
   │                      ├── <a href="scripts/parseAllPatients.html">parseAllPatients.sh</a>
   │                      ├── <a href="scripts/resendProject.html">resendProject.py</a>
   │                      ├── <a href="scripts/whatIsInIDS7.html">whatIsInIDS7.py</a>
   │                      └── <a href="scripts/whatIsNotInIDS7.html">whatIsNotInIDS7.py</a>
   │
   /var/
     └── www/
          └── html/
                ├── applications/
                │          ├── Assign/
                │          │     └── php
                |          |          └──<a href="scripts/removeOldEntries.html">removeOldEntries.sh</a>
                │          ├── Attach/
                │          │     └── <a href="scripts/process_tiff.html">process_tiff.sh</a>
                │          ├── Exports/
                │          │     └── php
                |          |          └──<a href="scripts/createZipFileCmd.html">createZipFileCmd.php</a>
                │          ├── User/
                │          │     └── asttt/
                │          │            └── code/
                │          │                  └── <a href="scripts/cron.html">cron.sh</a>
                │          └── Workflows/
                │                 └──php
                |                    └── <a href="scripts/runOneJob.html">runOneJob.sh</a>
                │
                └── server/
                       ├── bin/
                       |    ├── <a href="scripts/detectStudyArrival.html">detectStudyArrival.sh</a>
                       |    ├── <a href="scripts/heartbeat.html">heartbeat.sh</a>
                       |    ├── <a href="scripts/moveFromScanner.html">moveFromScanner.sh</a>
                       |    ├── <a href="scripts/mppsctl.html">mppsctl.sh</a>
                       |    ├── <a href="scripts/processSingleFile3.html">processSingleFile3.py</a>
                       |    ├── <a href="scripts/sendFiles.html">sendFiles.sh</a>
                       |    └── <a href="scripts/storectl.html">storectl.sh</a>
                       |
                       └── utils/
                             └── <a href="scripts/s2m.html">s2m.sh</a>
   
   </pre>



Components
-----------------------------

* :doc:`scripts/clearExports`
* :doc:`scripts/anonymizeAndSend`
* :doc:`scripts/clearOldFiles`
* :doc:`scripts/clearStaleLinks`
* :doc:`scripts/createTransferRequestsForProcessed`
* :doc:`scripts/createTransferRequests`
* :doc:`scripts/createZipFileCmd`
* :doc:`scripts/cron`
* :doc:`scripts/detectStudyArrival`
* :doc:`scripts/getAllPatients2`
* :doc:`scripts/heartbeat`
* :doc:`scripts/moveFromScanner`
* :doc:`scripts/mppsctl`
* :doc:`scripts/parseAllPatients`
* :doc:`scripts/populateAutoID`
* :doc:`scripts/populateIncoming`
* :doc:`scripts/populateProjects`
* :doc:`scripts/processSingleFile3`
* :doc:`scripts/process_tiff`
* :doc:`scripts/removeOldEntries`
* :doc:`scripts/resendProject`
* :doc:`scripts/runOneJob`
* :doc:`scripts/s2m`
* :doc:`scripts/sendFiles`
* :doc:`scripts/storectl`
* :doc:`scripts/whatIsInIDS7`
* :doc:`scripts/whatIsNotInIDS7`


Data Storage Structure
----------------------

The FIONA system uses a hierarchical storage structure:

.. code-block:: text

    /data/
    ├── site/
    │   ├── .arrived/         # Initial file reception
    │   ├── archive/          # Raw DICOM storage
    │   ├── raw/              # Processed DICOM files
    │   └── output/           # Processing results
    ├── config/               # Configuration files
    └── logs/                 # System logs

Project-specific directories follow the pattern:
/data{PROJECT}/site/...

 



