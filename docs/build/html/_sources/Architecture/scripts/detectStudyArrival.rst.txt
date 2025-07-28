``detectStudyArrival.sh`` monitors and processes incoming DICOM study arrivals in a medical imaging pipeline. The script checks for new study jobs created by receiveSingleFile.sh, processes them after a configurable delay, and triggers various quality control and compliance checks.

**The Main Dependences:**

| - **user:** none
| - **depends-on:**
|	- receiveSingleFile.sh
|	- anonymize.sh
|	- /data/config/config.json
|	- /tmp/.processSingleFilePipe
|	- /var/www/html/applications/Assign/incoming.txt
| - **log-file:**
|	- ${SERVERDIR}/logs/detectStudyArrival.log
|	- SERVERDIR/logs/detectStudyArrival{SERVERDIR}/logs/detectStudyArrival
|	- SERVERDIR/logs/detectStudyArrival{projname}.log
| - **pid-file:**
|	- SERVERDIR/.pids/detectStudyArrival{SERVERDIR}/.pids/detectStudyArrival
|	- SERVERDIR/.pids/detectStudyArrival{projname}.lock
| - **start:**
|	- ./detectStudyArrival.sh
|	- ./detectStudyArrival.sh [PROJECT_NAME]
| - **license:** TBE


**cron Configuration**

The script is designed to run via cron every 15 seconds to detect new arrivals and process studies for both ABCD and PCGC projects.
Add these lines to crontab -e for 15-second monitoring intervals:

.. code-block:: none

   */1 * * * * /data/code/bin/detectStudyArrival.sh
   */1 * * * * sleep 15; /data/code/bin/detectStudyArrival.sh
   */1 * * * * sleep 30; /data/code/bin/detectStudyArrival.sh
   */1 * * * * sleep 45; /data/code/bin/detectStudyArrival.sh

For PCGC project:

.. code-block:: none

   */1 * * * * /data/code/bin/detectStudyArrival.sh PCGC
   */1 * * * * sleep 15; /data/code/bin/detectStudyArrival.sh PCGC
   */1 * * * * sleep 30; /data/code/bin/detectStudyArrival.sh PCGC
   */1 * * * * sleep 45; /data/code/bin/detectStudyArrival.sh PCGC
   
   
** Input/Output File Dependencies Diagram**

.. mermaid::

   flowchart LR
   A["/data/config/config.json"] -->|"reads config"| B["detectStudyArrival.sh"]
   C["/data/site/.arrived/*"] -->|"monitors job files"| B
   D["receiveSingleFile.sh"] -->|"creates job files"| C
   B -->|"calls"| E["anonymize.sh"]
   B -->|"writes to"| F["/tmp/.processSingleFilePipe"]
   B -->|"updates"| G["/var/www/html/applications/Assign/incoming.txt"]
   B -->|"creates"| H["logs/detectStudyArrival.log"]
   B -->|"creates lock"| I["pids/detectStudyArrival.lock"]
   B -->|"creates archives"| J["quarantine/*.tgz"]
   B -->|"creates checksums"| K["quarantine/*.md5sum"]

   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef outputFile fill:#f3e5f5
   classDef mainScript fill:#fff3e0

   class A,C,D inputFile
   class F,G,H,I,J,K outputFile
   class B,E mainScript
   
   
**File Descriptions:**
| 1. Input Files:

| - ``/data/config/config.json`` - Main configuration file with project settings
| - ``/data/site/.arrived/*`` - Job files containing study arrival information
| - ``receiveSingleFile.sh`` - Script creating study arrival job files

| 2. Output Files:

| - ``/tmp/.processSingleFilePipe`` - Named pipe for queuing files to process
| - ``/var/www/html/applications/Assign/incoming.txt`` - Web interface assignment list for studies
| - ``logs/detectStudyArrival.log`` - Log file recording processing activities
| - ``pids/detectStudyArrival.lock`` - Lock file preventing concurrent execution
| - ``quarantine/*.tgz`` - Compressed archive files of processed data
| - ``quarantine/*.md5sum`` - Checksum files for data integrity verification

| 3. Scripts:

| - ``detectStudyArrival.sh`` - Main script monitoring DICOM study arrivals
| - ``anonymize.sh`` - Script for anonymizing DICOM files



**Data Flow Dependencies**

.. mermaid::

   flowchart LR
   A["site/raw/SDIR/SSERIESDIR/<br/>Directory containing raw DICOM files"] -->|"reads DICOM files"| B["detectStudyArrival.sh<br/>Main script processing data flow"]
   C["site/raw/SDIR/SSERIESDIR.json<br/>Metadata file with series information"] -->|"reads metadata"| B
   B -->|"processes to"| D["site/archive/SDIR/<br/>Archive directory for processed studies"]
   B -->|"outputs to"| E["site/output/SDIR/<br/>Output directory for QC reports"]
   B -->|"quarantines to"| F["quarantine/<br/>Directory for quarantined data"]
   B -->|"manages containers"| G["Docker: ABCDPhantomQC<br/>Container for phantom quality control"]
   B -->|"manages containers"| H["Docker: compliance_check<br/>Container for protocol compliance"]
   I["PFILEDIR/<br/>Directory for packed files storage"] -->|"packed files storage"| B
   B -->|"stores to"| I

   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef outputFile fill:#f3e5f5
   classDef mainScript fill:#fff3e0

   class A,C,I inputFile
   class D,E,F outputFile
   class B mainScript
   class G,H inputFile
   
   
**Data Flow File Descriptions:**

| 1. Input Files:

| - ``site/raw/SDIR/SSERIESDIR/`` - Directory containing raw DICOM files
| - ``site/raw/SDIR/SSERIESDIR.json`` - Metadata file with series information
| - ``PFILEDIR/`` - Directory for packed files storage

| 2. Output Files:

| - ``site/archive/SDIR/`` - Archive directory for processed studies
| - ``site/output/SDIR/`` - Output directory for QC reports
| - ``quarantine/`` - Directory for quarantined data

| 3. Scripts:

| - ``detectStudyArrival.sh`` - Main script processing data flow

| 4. Docker Containers:

| - Docker: ``ABCDPhantomQC`` - Container for phantom quality control
| - Docker: ``compliance_check`` - Container for protocol compliance


**Directories:**

| - ``/data/site/.arrived/`` - Job arrival directory (ABCD)
| - ``/data[PROJECT]/site/.arrived/`` - Project-specific arrival directories
| - ``${DATADIR}/site/raw/`` - Raw DICOM storage
| - ``${DATADIR}/site/archive/`` - Archived studies
| - ``${DATADIR}/site/output/`` - Processing results
| - ``${DATADIR}/quarantine/`` - Quarantine storage
| - ``${PFILEDIR}/`` - Packed file directory
| - ``${SERVERDIR}/logs/`` - Log file location
| - ``${SERVERDIR}/.pids/`` - Lock file directory




.. include:: detectStudyArrival.sh
   :start-after: : ' 
   :end-before: ' #end-doc
