processSingleFile3.py
----------------------

``processSingleFile3.py`` is a Python daemon process that monitors DICOM files, extracts header information, and creates Study/Series symbolic link structures. The script implements a generic daemon class and a specialized DICOM processing class that listens for incoming messages via named pipes, processes DICOM files, and organizes them into a structured directory hierarchy.

**The Main Dependences**

| - **user:** 
| - **depends-on:** 
| - **log-file:** /../logs/processSingleFile[projname].log 
| - **pid-file:**
|	-	 /../.pids/processSingleFile[projname].pid 
|	-	/tmp/processSingleFile[projname].pid
| - **start:** python processSingleFile3.py start [projname]
| - **license:** Tbe


**The processing workflow:**

| - Receives file paths via named pipe
| - Reads DICOM files and extracts metadata
| - Parses Siemens CSA headers for additional information
| - Applies classification rules from classifyRules.json
| - Creates organized directory structure with symbolic links
| - Generates JSON metadata files for each series


**Input/Output File Dependencies Diagram**

.. mermaid::

   flowchart LR
   %% Input Files
   CONFIG["config.json"]
   RULES["classifyRules.json"]
   PIPE["named pipe"]
   DICOM["DICOM files"]

   %% Main Script
   MAIN["processSingleFile3.py"]

   %% Output Files
   PID["*.pid"]
   LOG["*.log"]
   JSON["*.json metadata"]
   LINKS["symbolic links"]
   DIRS["organized directories"]

   %% Dependencies
   CONFIG --> MAIN
   RULES --> MAIN
   PIPE --> MAIN
   DICOM --> MAIN
		
   %% Outputs
   MAIN --> PID
   MAIN --> LOG
   MAIN --> JSON
   MAIN --> LINKS
   MAIN --> DIRS

   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef outputFile fill:#f3e5f5
   classDef mainScript fill:#fff3e0

   class CONFIG,RULES,PIPE,DICOM inputFile
   class PID,LOG,JSON,LINKS,DIRS outputFile
   class MAIN mainScript


**File Description:**

| 1. Input Files:

| - ``config.json`` - project configuration and directory paths
| - ``classifyRules.json`` - DICOM series classification rules
| - ``named pipe`` - daemon communication, receives file paths
| - ``DICOM files`` - medical imaging files to be processed

| 2. Output Files:

| - ``*.pid`` - daemon process ID
| - ``*.log`` - operation and error logs
| - ``*.json metadata`` - series metadata in JSON format
| - ``symbolic links`` - links to original DICOM files
| - ``organized directories`` - directory structure organized by patients/studies


**Data Flow Dependencies**

.. mermaid::

   flowchart LR
   %% Input Data
   CONFIG["config.json"]
   RULES["classifyRules.json"]
   PIPE["named pipe"]
   DICOM["DICOM files"]
    
   %% Main Process
   DAEMON["processSingleFile3.py"]
    
   %% Output Data
   PID["*.pid"]
   LOG["*.log"]
   JSON["*.json"]
   LINKS["symbolic links"]
   DIRS["organized directories"]
    
   %% Data Flow
   CONFIG --> DAEMON
   RULES --> DAEMON
   PIPE --> DAEMON
   DICOM --> DAEMON
    
   DAEMON --> PID
   DAEMON --> LOG
   DAEMON --> JSON
   DAEMON --> LINKS
   DAEMON --> DIRS
    
   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef process fill:#fff3e0
   classDef outputFile fill:#f3e5f5
    
   class CONFIG,RULES,PIPE,DICOM inputFile
   class DAEMON process
   class PID,LOG,JSON,LINKS,DIRS outputFile
   
**Data Flow components:**



| 1. Input Files:

| - ``config.json`` - system configuration file containing project settings and directory paths
| - ``classifyRules.json`` - rule definitions for automatic DICOM series classification
| - ``named pipe`` - inter-process communication channel receiving file processing commands
| - ``DICOM files`` - medical imaging files in DICOM format containing patient data

| 2. Main Process:

| - ``processSingleFile3.py`` - daemon process that orchestrates DICOM file processing and organization

| 3. Output Files:

| - ``*.pid`` - process identifier files for daemon management and monitoring
| - ``*.log`` - log files containing operational messages and error reports
| - ``*.json`` - metadata files with extracted DICOM header information
| - ``symbolic links`` - file system links organizing DICOM files by study structure
| - ``organized directories`` - hierarchical directory structure arranged by patients and studies


**Directories:**

| - ``/data`` - Default data directory
| - ``/data/site/.arrived`` - Touch files for series arrival detection
| - ``/data/site/participants`` - Patient-organized directory structure
| - ``/data/site/srs`` - Structured reports directory
| - ``/data/site/raw`` - Raw DICOM files organized by Study/Series
| - ``/data/site/temp`` - Temporary files directory
| - ``../logs/`` - Log files directory
| - ``../.pids/`` - Process ID files directory



.. include:: processSingleFile3.py
   :start-after: """
   :end-before: """
