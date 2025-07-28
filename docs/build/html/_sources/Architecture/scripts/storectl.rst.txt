The ``storectl.sh`` script is a system service controller for managing DICOM storage operations. It starts/stops the storescpFIONA daemon which receives DICOM files over the network and processes them through a named pipe system. 

Input/Output File Dependencies
------------------------------

.. mermaid::
   
   graph TD
   config.json --> storectl.sh
   enabled --> storectl.sh
   storectl.sh --> storescpd.pid
   storectl.sh --> storescpd.log
   storectl.sh --> processSingleFilePipe 
   
.. raw:: html

   <br>
   
**File Descriptions:**
   
- ``config.json`` - Main configuration file containing DATADIR, DICOMPORT, and project settings
- ``enabled`` - Control file to enable/disable the service (first character: 0=disabled, 1=enabled)
- ``storectl.sh`` - Main control script for managing the DICOM storage daemon
- ``storescpd.pid`` - Process ID file for tracking the running daemon
- ``storescpd.log`` - Log file recording daemon activities and errors
- ``processSingleFilePipe`` - Named pipe for communicating file reception events to processing system



Data Flow Dependencies
----------------------

.. mermaid::

    graph TD
    DICOMNetwork --> storescpFIONA
    storescpFIONA --> receiveSingleFile.sh
    receiveSingleFile.sh --> processSingleFilePipe
    processSingleFilePipe --> processSingleFile.py
    storescpFIONA --> ArchiveDirectory
    
.. raw:: html

   <br> 
    
**Data Flow Components:**

- ``DICOMNetwork`` - External DICOM devices sending medical imaging data over network
- ``storescpFIONA`` - DICOM storage daemon that receives and processes incoming DICOM files
- ``receiveSingleFile.sh`` - Script executed for each received DICOM file to handle initial processing
- ``processSingleFilePipe`` - Named pipe used for inter-process communication between components
- ``processSingleFile.py`` - Python script that processes DICOM file metadata and organizes data
- ``ArchiveDirectory`` - File system location where DICOM files are permanently stored

    
**Directories:**

- ``${DATADIR}/site/archive`` - DICOM file storage location
- ``${DATADIR}/site/.arrived`` - Temporary arrival directory
- ``${SERVERDIR}/.pids/`` - PID file storage
- ``${SERVERDIR}/logs/`` - Log file directory


.. include:: storectl.sh 
   :start-after: : '
   :end-before: ' #end-doc
