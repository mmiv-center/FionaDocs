ARCHITECTURE 
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 0
   
  
   
Overview
--------

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



System Purpose
--------------

FIONA serves as an intermediary system that:

* Receives medical image data from clinical PACS systems
* Processes and classifies incoming DICOM studies
* Anonymizes data according to research requirements
* Manages data transfer back to research PACS systems
* Provides project-specific data organization



Data Flow
----------

This document describes the complete data flow through the FIONA system, from initial DICOM reception to final transfer to research PACS.

Data flow overwie (ver.1 - detailed)

.. mermaid::

   graph TB
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






Data Storage Structure
----------------------

The FIONA system uses a hierarchical storage structure:

.. code-block:: text

    /data/
    ├── site/
    │   ├── .arrived/          # Initial file reception
    │   ├── archive/           # Raw DICOM storage
    │   ├── raw/              # Processed DICOM files
    │   └── output/           # Processing results
    ├── config/               # Configuration files
    └── logs/                 # System logs

Project-specific directories follow the pattern:
/data{PROJECT}/site/...


System components
------------------

.. toctree::
   :maxdepth: 1
   
   scripts/storectl
   scripts/processSingleFile3
   scripts/detectStudyArrival   
   scripts/anonymizeAndSend   
   scripts/sendFiles   
   scripts/mppsctl
   scripts/parseAllPatients
   scripts/process_tiff
   scripts/removeOldEntries
   scripts/runOneJob
   scripts/getAllPatients2
   scripts/heartbeat
   scripts/moveFromScanner
   scripts/clearExports
   scripts/clearOldFiles
   scripts/clearStaleLinks
   scripts/cron
   scripts/whatIsInIDS7
   scripts/whatIsNotInIDS7
   scripts/createTransferRequestForProcessed
   scripts/populateAutoID
   scripts/populateIncoming
   scripts/populateProjects
   scripts/resendProject
   scripts/createTransferRequest
   scripts/createZipFileCmd



