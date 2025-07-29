ARCHITECTURE 
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 0
   
  
   
Architecture Overview
============================

The architecture of Fiona sysetem can be included included into a few layers: network layer, processing layer, storage layer, transfer layer and management layer

.. mermaid::    
    
    flowchart LR
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
===============

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


Data flow diagram (ver.2 - more general)

.. mermaid::

  graph TB
      PACS[Clinical PACS]
      FIONA_Input[FIONA Input Layer]
      FIONA_Process[FIONA Processing]
      FIONA_Storage[FIONA Storage]
      FIONA_Transfer[FIONA Transfer]
      Research[Research PACS]
      REDCap[REDCap Database]
      
      PACS --> FIONA_Input
      FIONA_Input --> FIONA_Process
      FIONA_Process --> FIONA_Storage
      FIONA_Storage --> FIONA_Transfer
      FIONA_Transfer --> Research
      
      REDCap --> FIONA_Transfer
      FIONA_Process --> REDCap




Data Flow Overview
------------------

.. mermaid::

  graph TB
      A[Clinical Systems]
      B[DICOM Reception]
      C[File Processing]
      D[Classification]
      E[Study Organization]
      F[Anonymization]
      G[Transfer Prep]
      H[Research PACS]
      
      A --> B
      B --> C
      C --> D
      D --> E
      E --> F
      F --> G
      G --> H




The FIONA system processes medical image data through several distinct phases:

1. **Data Reception** - DICOM files arrive from clinical systems
2. **Initial Processing** - Files are processed and classified
3. **Study Organization** - Data is organized into study/series structure
4. **Anonymization** - Data is anonymized for research use
5. **Transfer Preparation** - Data is prepared for transfer
6. **Export** - Data is transferred to research PACS

Detailed Data Flow
------------------

Phase 1: Data Reception
~~~~~~~~~~~~~~~~~~~~~~~

**Input:** DICOM files from clinical PACS
**Components:** storescpFIONA, storectl.sh
**Output:** Raw DICOM files in temporary storage

.. code-block:: text

    Clinical PACS → storescpFIONA → /data/site/.arrived/
                                    ↓
                              Named Pipe (/tmp/.processSingleFilePipe)

**Process:**
1. Clinical PACS sends DICOM files via DICOM protocol
2. storescpFIONA receives files and stores in `/data/site/.arrived/`
3. File arrival notification sent via named pipe
4. Files moved to `/data/site/archive/` for processing

Phase 2: Initial Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Input:** Raw DICOM files
**Components:** processSingleFile3.py, receiveSingleFile.sh
**Output:** Processed DICOM files with metadata

.. code-block:: text

    /data/site/archive/ → processSingleFile3.py → /data/site/raw/
                           ↓
                    Classification Rules (classifyRules.json)
                           ↓
                    Study/Series Organization

**Process:**
1. processSingleFile3.py daemon receives file notifications
2. DICOM headers are parsed and metadata extracted
3. Files are classified using rule-based system
4. Study and series information is organized
5. Symbolic links are created for easy access

Phase 3: Study Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Input:** Processed DICOM files
**Components:** detectStudyArrival.sh
**Output:** Organized study structure

.. code-block:: text

    /data/site/raw/ → detectStudyArrival.sh → Study Job Directory
                       ↓
                Study Completion Detection
                       ↓
                Workflow Trigger

**Process:**
1. detectStudyArrival.sh monitors for completed studies
2. Study completion is detected when all series arrive
3. Study job directory is created
4. Workflow processes are triggered

Phase 4: Anonymization
~~~~~~~~~~~~~~~~~~~~~~

**Input:** Organized study data
**Components:** anonymizeAndSend.py, anonymize.sh
**Output:** Anonymized DICOM files

.. code-block:: text

    Study Data → anonymizeAndSend.py → Anonymized Data
                   ↓
            REDCap Configuration
                   ↓
            Project-specific Rules

**Process:**
1. Transfer requests are read from REDCap
2. Project-specific anonymization rules are applied
3. DICOM tags are modified according to requirements
4. Anonymized files are prepared for transfer

Phase 5: Transfer Preparation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Input:** Anonymized study data
**Components:** createTransferRequest.py, createZipFileCmd.php
**Output:** Transfer-ready data packages

.. code-block:: text

    Anonymized Data → createTransferRequest.py → Transfer Package
                         ↓
                  ZIP File Creation
                         ↓
                  MD5 Checksum Generation

**Process:**
1. Transfer requests are processed
2. Data is packaged into ZIP files
3. MD5 checksums are generated for integrity
4. Transfer packages are prepared

Phase 6: Export
~~~~~~~~~~~~~~~

**Input:** Transfer packages
**Components:** sendFiles.sh
**Output:** Data transferred to research PACS

.. code-block:: text

    Transfer Package → sendFiles.sh → Research PACS
                          ↓
                   SFTP Transfer
                          ↓
                   Transfer Confirmation

**Process:**
1. SFTP connection established to research PACS
2. Files are transferred with integrity checking
3. Transfer status is logged
4. Success/failure notifications are sent

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

Communication Mechanisms
------------------------

**Named Pipes:**
- `/tmp/.processSingleFilePipe` - File processing notifications
- Project-specific pipes: `/tmp/.processSingleFilePipe{PROJECT}`

**Configuration Files:**
- `/data/config/config.json` - Main system configuration
- `classifyRules.json` - Classification rules
- REDCap integration for transfer management

**Log Files:**
- System logs in `/var/www/html/server/logs/`
- Processing logs in `/data/logs/`

Error Handling and Recovery
---------------------------

**File Processing Errors:**
- Failed files are logged and can be reprocessed
- Corrupted DICOM files are quarantined
- Processing retries are implemented

**Transfer Errors:**
- Failed transfers are retried automatically
- MD5 checksum verification ensures data integrity
- Transfer status is tracked in REDCap

**System Recovery:**
- Daemon processes can be restarted automatically
- File system consistency is maintained
- Backup and recovery procedures are in place

Monitoring and Logging
----------------------

**System Monitoring:**
- heartbeat.sh - System health monitoring
- cron.sh - Scheduled task management
- Log rotation and management

**Data Flow Monitoring:**
- File arrival detection
- Processing status tracking
- Transfer completion monitoring

This data flow ensures reliable, automated processing of medical image data while maintaining data integrity and compliance with research requirements. 


System components
=================

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



