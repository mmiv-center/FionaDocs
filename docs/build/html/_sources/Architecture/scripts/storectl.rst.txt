
The ``storectl.sh`` script is a system service controller for managing DICOM storage operations. It starts/stops the storescpFIONA daemon which receives DICOM files over the network and processes them through a named pipe system. 


**The Main Dependecnes:**

| - **user:** processing
| - **depends-on:** 
|	- /data/config/config.json,
|	- storescpFIONA,
|	- receiveSingleFile.sh,
|	- processSingleFile.py
| - **log-file:** 
|	- ${SERVERDIR}/logs/storescpd${projname}.log,
|	- ${SERVERDIR}/logs/storescpd-start.log
| - **pid-file:** ${SERVERDIR}/.pids/storescpd${projname}.pid
| - **start:** ./storectl.sh start [PROJECT_NAME]
| - **license:** TBE


**Input/Output File Dependencies**

.. mermaid::
   
   flowchart TD
   config["/data/config/config.json"]
   enabled["/data/enabled"]
   dict["/usr/share/dcmtk/dicom.dic"]
    
   storectl["storectl.sh"]
   receiveSingle["receiveSingleFile.sh"]
    
   pidFile["${SERVERDIR}/.pids/storescpd${projname}.pid"]
   logFile["${SERVERDIR}/logs/storescpd${projname}.log"]
   startLog["${SERVERDIR}/logs/storescpd-start.log"]
    
   config -->|"reads DATADIR, DICOMPORT"| storectl
   enabled -->|"checks service status"| storectl
   dict -->|"sets environment variable"| storectl
    
   storectl -->|"creates/deletes PID"| pidFile
   storectl -->|"writes daemon logs"| logFile
   storectl -->|"writes startup logs"| startLog
   storectl -->|"executes on reception"| receiveSingle
    
   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef outputFile fill:#f3e5f5
   classDef mainScript fill:#fff3e0
    
   class config,enabled,dict inputFile
   class pidFile,logFile,startLog outputFile
   class storectl,receiveSingle mainScript
   
      
**File Descriptions:**
   
| - ``config.json`` - Main configuration file containing DATADIR, DICOMPORT, and project settings
| - ``enabled`` - Control file to enable/disable the service (first character: 0=disabled, 1=enabled)
| - ``storectl.sh`` - Main control script for managing the DICOM storage daemon
| - ``storescpd.pid`` - Process ID file for tracking the running daemon
| - ``storescpd.log`` - Log file recording daemon activities and errors
| - ``processSingleFilePipe`` - Named pipe for communicating file reception events to processing system



**Data Flow Dependencies**

.. mermaid::

   flowchart TD
   dicomSender["DICOM Sender"]
   storescpFIONA["storescpFIONA daemon"]
    
   arrivedDir["${DATADIR}/site/.arrived/"]
   archiveDir["${DATADIR}/site/archive/"]
   pipe["/tmp/.processSingleFilePipe${projname}"]
   
   receiveSingle["receiveSingleFile.sh"]
   processSingle["processSingleFile.py"]
   storectl["storectl.sh"]
    
   dicomSender -->|"DICOM files"| storescpFIONA
   storescpFIONA -->|"stores files"| arrivedDir
   storescpFIONA -->|"archives files"| archiveDir
   storescpFIONA -->|"triggers execution"| receiveSingle
   receiveSingle -->|"sends events"| pipe
   pipe -->|"processes events"| processSingle
    
   storectl -->|"starts/stops"| storescpFIONA
    
   %% Styling
   classDef inputFile fill:#e1f5fe
   classDef outputFile fill:#f3e5f5
   classDef mainScript fill:#fff3e0
    
   class dicomSender,arrivedDir inputFile
   class archiveDir,pipe outputFile
   class storectl,receiveSingle,processSingle,storescpFIONA mainScript 
   
 
**File Descriptions**

| 1. Input Files:

| - ``/data/config/config.json`` - Main configuration file containing data directories and DICOM ports
| - ``/data/enabled`` - Optional control file to disable the service (first character "0" disables)
| - ``/usr/share/dcmtk/dicom.dic`` - DICOM dictionary file for parsing DICOM data structures

| 2. Output Files:

| - ``${SERVERDIR}/.pids/storescpd${projname}.pid`` - Process ID file for daemon management
| - ``${SERVERDIR}/logs/storescpd${projname}.log`` - Main service log file for daemon output
| - ``${SERVERDIR}/logs/storescpd-start.log`` - Startup log file for initialization messages
| - ``/tmp/.processSingleFilePipe${projname}`` - Named pipe for inter-process communication   


    
**Directories:**

| - ``${DATADIR}/site/archive`` - DICOM file storage location
| - ``${DATADIR}/site/.arrived`` - Temporary arrival directory
| - ``${SERVERDIR}/.pids/`` - PID file storage
| - ``${SERVERDIR}/logs/`` - Log file directory


.. include:: storectl.sh 
   :start-after: : '
   :end-before: ' #end-doc
