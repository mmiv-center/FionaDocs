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
