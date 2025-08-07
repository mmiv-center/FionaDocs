detectStudyArrival.sh
~~~~~~~~~~~~~~~~~~~~~~

``detectStudyArrival.sh`` is a DICOM processing daemon that monitors for newly arrived medical imaging studies and series. The script runs continuously via cron jobs (every 15 seconds) to detect completed file transfers, performs quality control checks using Docker containers, and manages the archival workflow for both ABCD and PCGC projects. It handles anonymization, phantom QA processing, series compliance validation, and prepares studies for transmission to data centers.


**Related Files**

.. mermaid::

   flowchart TD
    B["receiveSingleFile.sh<br>(Creates job directories)"] --> A["detectStudyArrival.sh<br>(Main Script)"]
    E["/data/config/config.json<br>(Configuration file)"] --> A
    A --> C["anonymize.sh<br>(Anonymizes DICOM data)"]
    A --> D["sendFiles.sh<br>(Sends processed data)"]
    A --> F["Docker: ABCDPhantomQC<br>(Phantom quality control)"]
    A --> G["Docker: compliance_check<br>(Series compliance validation)"]
    A --> H["/tmp/.processSingleFilePipe<br>(Processing queue)"]
    A --> I["/var/www/html/applications/<br>Assign/incoming.txt<br>(Web interface queue)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,E inputFile
    class C,D,F,G,H,I outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/data/site/.arrived/<br>(Job trigger files)"] --> B["detectStudyArrival.sh<br>(Main Processing)"]
    C["/data/site/raw/<br>(Raw DICOM data)"] --> B
    D["/data/config/config.json<br>(Configuration)"] --> B
    
    B --> E["/data/site/archive/<br>(Archived studies)"]
    B --> F["/data/site/output/<br>(Processing results)"]
    B --> G["/data/quarantine/<br>(Quarantine area)"]
    B --> H["/data/PFILEDIR/<br>(Processed files)"]
    B --> I["Log files<br>(Processing logs)"]
    B --> J["/var/www/html/applications/<br>Assign/incoming.txt<br>(Web interface)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B mainScript
    class E,F,G,H,I,J outputFile



Data paths

- Input Directories:

   * ``/data/site/.arrived/`` - Job trigger files created by receiveSingleFile.sh
   * ``/data/site/raw/`` - Raw DICOM data from scanners
   * ``/data/config/config.json`` - System configuration file
   * ``/data/site/archive/``- Archived study data for processing

- Output Directories:

   * ``/data/site/output/`` - Processing results and QC reports
   * ``/data/quarantine/`` - Temporary storage for processed series
   * ``/data/PFILEDIR/`` - Final processed files ready for transmission
   * ``/var/www/html/applications/Assign/incoming.txt`` - Web interface study queue
   * ``${SERVERDIR}/logs/`` - Processing and error logs

- Project-specific paths (for non-ABCD projects like PCGC):

   * ``/data{PROJNAME}/site/.arrived/`` - Project-specific job triggers Project-specific DATADIR and PFILEDIR from config.json


----

.. include:: detectStudyArrival.sh
   :start-after: : ' 
   :end-before: ' #end-doc
