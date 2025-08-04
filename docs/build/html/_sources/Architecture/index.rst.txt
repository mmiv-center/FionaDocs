ARCHITECTURE
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 0
   

**FIONA System Architecture**

A detailed system architecture including all system components is presented below

.. mermaid::
   :caption: FIONA layered Architecture

   flowchart TD
        subgraph network [" <b>Network Layer</b> "]
            PACS[📡 Clinical PACS<br/>DICOM File Source]
            StoreSCP[📥 storescpFIONA<br/>DICOM SCP]
            Scanner[🏥 Scanner Integration<br/>moveFromScanner.sh]
            MPPS[📋 MPPS Service<br/>mppsctl.sh]
        end
        
        subgraph processing [" <b>Processing Layer</b> "]
            ProcessFile[🔄 processSingleFile3.py<br/>DICOM Processing]
            DetectStudy[🔍 detectStudyArrival.sh<br/>Study Detection]
            Classification[⚙️ Classification<br/>Rule Engine]
            ProcessTiff[🖼️ process_tiff.sh<br/>Pathology + Anonymization]
            PopulateIncoming[📊 populateIncoming.py<br/>REDCap Population]
            PopulateProjects[🗂️ populateProjects.py<br/>Project Distribution]
            PopulateAutoID[🔢 populateAutoID.py<br/>Auto ID Generation]
            RunJobs[⚙️ runOneJob.sh<br/>Workflow Execution]
            NamedPipe((Named Pipe))
        end
        
        subgraph storage [" <b>Storage Layer</b> "]
            FileSystem[💾 File System<br/>/data/site/]
            SymLinks[🔗 Symbolic Links<br/>Study/Series]
            Archive[📚 Archive Management<br/>clearOldFiles.sh]
            Inventory[📋 PACS Inventory<br/>whatIsInIDS7.py]
            ValidationCleanup[🧹 Data Validation<br/>whatIsNotInIDS7.py]
            GetPatients[👥 Patient Data<br/>getAllPatients2.sh]
            ParsePatients[📊 Parse Patient Data<br/>parseAllPatients.sh]
            StaleLinks[🔗 Link Cleanup<br/>clearStaleLinks.sh]
        end
        
        subgraph transfer [" <b>Transfer Layer</b> "]
            CreateRequests[📝 createTransferRequests.py<br/>Transfer Management]
            Anonymize[🔒 anonymizeAndSend.py<br/>Main Anonymization]
            CreateZip[📦 createZipFileCmd.php<br/>Export Anonymization]
            SendFiles[📤 sendFiles.sh<br/>SFTP Transfer]
            ResendProject[🔄 resendProject.py<br/>Retry Logic]
            ResPACS[🏥 Research PACS<br/>Destination]
            REDCap[(🗄️ REDCap<br/>Database)]
        end
        
        subgraph mgmt [" <b>Management Layer</b> "]
            Heartbeat[💓 heartbeat.sh<br/>Health Monitoring]
            CronSystem[⏰ cron.sh<br/>Event Automation]
            Setup[⚙️ setup.sh<br/>Configuration]
            ClearExports[🗑️ clearExports.sh<br/>Export Cleanup]
            S2M[🔄 s2m.sh<br/>Reprocessing Tool]
        end
        
        %% Main Data Flow
        PACS -->|DICOM| StoreSCP
        Scanner -->|C-MOVE| StoreSCP
        StoreSCP -->|DICOM Files| ProcessFile
        ProcessFile -->|metadata| NamedPipe
        NamedPipe -->|trigger| DetectStudy
        DetectStudy -->|study info| Classification
        ProcessFile -->|pathology images| ProcessTiff
        ProcessTiff -->|anonymized DICOM| FileSystem
        Classification -->|routing| PopulateIncoming
        PopulateIncoming -->|data| REDCap
        PopulateProjects -->|project data| REDCap
        PopulateAutoID -->|auto IDs| REDCap
        
        %% Storage Operations
        ProcessFile -->|files| FileSystem
        FileSystem -->|organization| SymLinks
        GetPatients -->|patient data| ParsePatients
        ParsePatients -->|parsed data| Inventory
        Inventory -->|validation| ValidationCleanup
        ValidationCleanup -->|cleanup| FileSystem
        Archive -->|cleanup| StaleLinks
        StaleLinks -->|clean links| SymLinks
        
        %% Transfer Operations
        REDCap -->|transfer rules| CreateRequests
        CreateRequests -->|requests| Anonymize
        SymLinks -->|study data| Anonymize
        Anonymize -->|anonymized DICOM| ResPACS
        CreateZip -->|export archives| SendFiles
        SendFiles -->|SFTP| ResPACS
        ResendProject -->|retry| Anonymize
        
        %% Management Operations
        Heartbeat -.->|monitor| StoreSCP
        Heartbeat -.->|monitor| ProcessFile
        CronSystem -.->|automate| PopulateIncoming
        CronSystem -.->|automate| CreateRequests
        Archive -.->|cleanup| FileSystem
        ClearExports -.->|cleanup| SendFiles
        Setup -.->|configure| FileSystem
        Setup -.->|configure| StoreSCP
        S2M -->|reprocess| ProcessFile
        
        %% Workflow Integration
        RunJobs -->|analysis results| ResPACS
        
        %% Styling
        classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
        classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
        classDef storage fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
        classDef transfer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
        classDef mgmt fill:#ffebee,stroke:#d32f2f,stroke-width:2px
        classDef pipe fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
        
        class PACS,StoreSCP,Scanner,MPPS network
        class ProcessFile,DetectStudy,Classification,ProcessTiff,PopulateIncoming,PopulateProjects,PopulateAutoID,RunJobs process
        class FileSystem,SymLinks,Archive,Inventory,ValidationCleanup,GetPatients,ParsePatients,StaleLinks storage
        class CreateRequests,Anonymize,CreateZip,SendFiles,ResendProject,ResPACS,REDCap transfer
        class Heartbeat,CronSystem,Setup,ClearExports,S2M mgmt
        class NamedPipe pipe



:download:`Dowlnoad image as PDF <../_static/fiona-layers.pdf>`


Setup
-------

To setup the system some mandatory information must be set set in ``/data/config/conf.json`` file. Fill values appropriate to your serwer as shown in example json file.


.. literalinclude:: config-example.json
   :language: json
   :linenos:
   :emphasize-lines: 3,5
   :caption: System configuration example settings
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

#. :doc:`scripts/anonymizeAndSend` - Processes imaging studies, performs anonymization, and sends them to research PACS
#. :doc:`scripts/clearExports` - Removes old export files when storage reaches capacity thresholds
#. :doc:`scripts/clearOldFiles` - Removes old studies from ``/data/site/archive`` when disk usage exceeds 80%
#. :doc:`scripts/clearStaleLinks` - Removes broken symbolic links and empty directories from data structures
#. :doc:`scripts/createTransferRequests` - Generates transfer requests for studies that need anonymization and forwarding to research projects
#. :doc:`scripts/createTransferRequestsForProcessed` - Handles transfer requests for processed/derived imaging data from workstations back to research PACS
#. :doc:`scripts/createZipFileCmd` -  Creates anonymized ZIP archives for research data distribution
#. :doc:`scripts/cron` - Processes trigger-action pairs from JSON configuration files for event-driven automation
#. :doc:`scripts/detectStudyArrival` - Triggers processing workflows when imaging studies are fully received
#. :doc:`scripts/getAllPatients2` - Retrieves patient and study information from research PACS using findscu
#. :doc:`scripts/heartbeat` - Checks DICOM service responsiveness and restarts failed components
#. :doc:`scripts/moveFromScanner` - Pulls imaging data from clinical scanners using DICOM C-MOVE operations
#. :doc:`scripts/mppsctl` - Controls DICOM Modality Performed Procedure Step (MPPS) service for tracking scan progress
#. :doc:`scripts/parseAllPatients` - Parses patient data retrieved by getAllPatients2.sh and extracts study-level metadata for REDCap import
#. :doc:`scripts/populateAutoID` -  Generates automatic participant IDs for projects using pseudonymized identifiers
#. :doc:`scripts/populateIncoming` - Processes incoming DICOM studies and creates metadata records in REDCap
#. :doc:`scripts/populateProjects` - Populates individual research project databases with distributed data
#. :doc:`scripts/processSingleFile3` - Extracts metadata from DICOM files and creates directory structures
#. :doc:`scripts/process_tiff` - Converts whole slide imaging (WSI) files to DICOM format for pathology processing
#. :doc:`scripts/removeOldEntries` - Removes old entries from incoming data tracking files
#. :doc:`scripts/resendProject` - Handles re-transmission of studies when initial transfers fail or new data arrives
#. :doc:`scripts/runOneJob` - Processes containerized analysis jobs from job queue
#. :doc:`scripts/s2m` - Re-sends DICOM directories through the processing pipeline for re-classification
#. :doc:`scripts/sendFiles` - Uploads anonymized data to external research repositories via secure file transfer
#. :doc:`scripts/storectl` - Manages the main DICOM C-STORE receiver daemon
#. :doc:`scripts/whatIsInIDS7`- Catalogs all studies present in the research imaging database
#. :doc:`scripts/whatIsNotInIDS7`- Identifies and removes database entries for studies no longer in PACS

System setup pipeline
------------------------

.. mermaid::

   flowchart TD
       Start([System Boot]) -->  CoreServices[Core Services]
          
       subgraph CoreServices [Core Services]
           StoreCTL[storectl.sh<br/>DICOM Receiver]
           MPPS[mppsctl.sh<br/>MPPS Service]
           Process[processSingleFile3.py<br/>Processing Daemon]
       end
       
       CoreServices --> CronJobs[Cron Jobs]
       
       subgraph CronJobs [Automatic Tasks]
           Detect[detectStudyArrival.sh<br/>15 seconds]
           Heartbeat[heartbeat.sh<br/>1 minute]
           Populate[populateIncoming.py<br/>5 minutes]
           Transfer[createTransferRequests.py<br/>10 minutes]
           Anonymize[anonymizeAndSend.py<br/>continuous]
           Jobs[runOneJob.sh<br/>job queue]
       end
       
       CronJobs --> Maintenance[Daily/Hourly Tasks]
       
       subgraph Maintenance [Maintenance Tasks]
           Projects[populateProjects.py<br/>hourly]
           AutoID[populateAutoID.py<br/>30 minutes]
           SendFiles[sendFiles.sh<br/>30 minutes]
           Cleanup[clearOldFiles.sh<br/>daily]
           ClearExports[clearExports.sh<br/>daily]
           StaleLinks[clearStaleLinks.sh<br/>daily]
           RemoveOld[removeOldEntries.sh<br/>daily]
       end
       
       Maintenance --> SystemReady[System Ready]
       
       SystemReady --> EventSystem[cron.sh<br/>Event Automation]
       
       %% Styling
       classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
       classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
       classDef storage fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
       classDef transfer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
       classDef mgmt fill:#ffebee,stroke:#d32f2f,stroke-width:2px
       classDef system fill:#f0f0f0,stroke:#424242,stroke-width:2px
       
       class StoreCTL,MPPS network
       class Process,Detect,Populate,Jobs process
       class Cleanup,StaleLinks storage
       class Transfer,Anonymize,SendFiles transfer
       class Setup,Heartbeat,Projects,AutoID,ClearExports,RemoveOld,EventSystem mgmt
       class Start,SystemReady system

:download:`Dowlnoad image as PDF <../_static/fiona-sequence.pdf>`

Data flow
--------------

Data flow scheme through the FIONA system, from initial DICOM reception to final transfer to research PACS, is presented below.

.. mermaid::

   flowchart TD
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

 



