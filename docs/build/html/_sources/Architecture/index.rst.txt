ARCHITECTURE 
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 0
   



Setup
----------

Here is the complete data flow through the FIONA system, from initial DICOM reception to final transfer to research PACS.

.. mermaid::

   flowchart TB
       PACS[Clinical PACS - DICOM Source]
       StoreSCP[storescpFIONA - DICOM SCP]
       NamedPipe((Named Pipe))
       Arrived[Job Directory]
       
       ProcessDaemon[processSingleFile3.py]
       ClassifyRules[classifyRules.json]
       RawData[/data/site/raw/]
       SymLinks[Symbolic Links]
       
       DetectStudy[detectStudyArrival.sh]
       StudyJob[Study Job Directory]
       Anonymize[anonymize.sh]
       Archive[/data/site/archive/]
       
       AnonSend[anonymizeAndSend.py]
       REDCap[REDCap API]
       TransferReq[Transfer Requests]
       
       SendFiles[sendFiles.sh]
       Outbox[/data/outbox/]
       ResPACS[Research PACS]
       DAIC[/data/DAIC/]
       
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
       AnonSend --> TransferReq
       TransferReq --> SendFiles
       
       SendFiles --> Outbox
       Outbox --> ResPACS
       ResPACS --> DAIC


Folder and File structure
--------------------------

.. raw:: html

   <pre>
   /home/processing/
   |          ├── bin/
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
                │          │     └── <a href="scripts/removeOldEntries.html">removeOldEntries.sh</a>
                │          ├── Attach/
                │          │     └── <a href="scripts/process_tiff.html">process_tiff.sh</a>
                │          ├── Exports/
                │          │     └── <a href="scripts/createZipFileCmd.html">createZipFileCmd.php</a>
                │          ├── User/
                │          │     └── asttt/
                │          │            └── code/
                │          │                  └── <a href="scripts/cron.html">cron.sh</a>
                │          └── Workflows/
                │                 └── <a href="scripts/runOneJob.html">runOneJob.sh</a>
                │
                └── server/
                       └── bin/
                           ├── <a href="scripts/detectStudyArrival.html">detectStudyArrival.sh</a>
                           ├── <a href="scripts/heartbeat.html">heartbeat.sh</a>
                           ├── <a href="scripts/moveFromScanner.html">moveFromScanner.sh</a>
                           ├── <a href="scripts/mppsctl.html">mppsctl.sh</a>
                           ├── <a href="scripts/processSingleFile3.html">processSingleFile3.py</a>
                           ├── <a href="scripts/sendFiles.html">sendFiles.sh</a>
                           └── <a href="scripts/storectl.html">storectl.sh</a>
   </pre>


Files Listed Alphabetically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
.. toctree::
   :maxdepth: 0
     
   scripts/anonymizeAndSend.rst
   scripts/clearExports.rst
   scripts/clearOldFiles.rst
   scripts/clearStaleLinks.rst
   scripts/createTransferRequestsForProcessed.rst
   scripts/createTransferRequests.rst
   scripts/createZipFileCmd.rst
   scripts/cron.rst
   scripts/detectStudyArrival.rst
   scripts/getAllPatients2.rst
   scripts/heartbeat.rst
   scripts/moveFromScanner.rst
   scripts/mppsctl.rst
   scripts/parseAllPatients.rst
   scripts/populateAutoID.rst
   scripts/populateIncoming.rst
   scripts/populateProjects.rst
   scripts/processSingleFile3.rst
   scripts/process_tiff.rst
   scripts/removeOldEntries.rst
   scripts/resendProject.rst
   scripts/runOneJob.rst
   scripts/sendFiles.rst
   scripts/storectl.rst
   scripts/whatIsInIDS7.rst
   scripts/whatIsNotInIDS7.rst


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

Fiona Layers
-------------

The architecture of Fiona sysetem can be included included into a few layers: network layer, processing layer, storage layer, transfer layer and management layer

.. mermaid::    
    
    flowchart TD
        subgraph network [" Network Layer "]
            PACS[📡 Clinical PACS<br/>DICOM Source]
            StoreSCP[📥 storescpFIONA<br/>DICOM SCP]
        end
        
        subgraph processing [" Processing Layer "]
            ProcessFile[🔄 processSingleFile3.py<br/>DICOM Processing]
            DetectStudy[🔍 detectStudyArrival.sh<br/>Study Detection]
            Classification[⚙️ Classification<br/>Rule Engine]
            NamedPipe((Named Pipe))
        end
        
        subgraph storage [" Storage Layer "]
            FileSystem[💾 File System<br/>/data/site/]
            SymLinks[🔗 Symbolic Links<br/>Study/Series]
        end
        
        subgraph transfer [" Transfer Layer "]
            Anonymize[🔒 anonymizeAndSend.py<br/>Anonymization]
            SendFiles[📤 sendFiles.sh<br/>SFTP Transfer]
            ResPACS[🏥 Research PACS<br/>Destination]
            REDCap[(🗄️ REDCap)]
        end
        
        subgraph mgmt [" Management Layer "]
            Management[⚙️ System Management<br/>heartbeat.sh, cron.sh, monitoring]
        end
        
        %% Data Flow
        PACS -->|DICOM| StoreSCP
        StoreSCP -->|DICOM Files| ProcessFile
        ProcessFile -->|metadata| NamedPipe
        NamedPipe -->|trigger| DetectStudy
        DetectStudy -->|study info| Classification
        Classification -->|classification| SymLinks
        FileSystem -->|files| SymLinks
        SymLinks -->|study data| Anonymize
        Anonymize -->|anonymized| SendFiles
        SendFiles -->|SFTP| ResPACS
        REDCap -->|consent| Anonymize
        
        %% Management connections
        Management -.->|monitor| StoreSCP
        Management -.->|monitor| ProcessFile
        Management -.->|monitor| FileSystem
        
        %% Styling
        classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
        classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
        classDef storage fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
        classDef transfer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
        classDef mgmt fill:#ffebee,stroke:#d32f2f,stroke-width:2px
        classDef pipe fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
        
        class PACS,StoreSCP network
        class ProcessFile,DetectStudy,Classification process
        class FileSystem,SymLinks storage
        class Anonymize,SendFiles,ResPACS,REDCap transfer
        class Management mgmt
        class NamedPipe pipe
  



