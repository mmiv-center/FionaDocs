*** ADMIN (options) ***
==============================================

**For:** IT administrators, DevOps

**Should contain:**

- FIONA installation instructions
- Server configuration
- User management
- Monitoring and logs
- Backup and recovery
- Troubleshooting
- System requirements

-------





System Architecture
====================

The Fiona system consists of the following main components:

2.1 DICOM Servers
------------------

**storescp**: Server receiving DICOM data

**findscu/movescu**: Clients for searching and retrieving data from PACS

**echoscu**: Connection monitoring

2.2 Processing Components
-------------------------

**processSingleFile**: Daemon processing individual DICOM files

**detectStudyArrival**: Detection of completed image series reception

**anonymizeAndSend**: Data anonymization and transmission

2.3 Project Management
----------------------

**populateIncoming**: Analysis of incoming data

**populateProjects**: REDCap project updates

**populateAutoID**: Automatic identifier generation

Installation and Configuration
===============================

2.1 System Requirements
-----------------------

**OS**: Linux (Ubuntu/Debian preferred)

**Python**: 3.x with libraries: pydicom, pycurl, json

**DCMTK**: DICOM tools

**Docker**: For containerized processes

**REDCap**: Research data management system

2.2 Directory Structure
-----------------------

.. code-block::

    /data/
    ├── config/
    │   ├── config.json          # Main configuration
    │   └── enabled              # Enable/disable flag
    ├── site/
    │   ├── archive/             # DICOM archive (scp_<StudyInstanceUID>)
    │   ├── raw/                 # Raw data (StudyInstanceUID/SeriesInstanceUID)
    │   ├── participants/        # Per-patient links
    │   ├── srs/                 # Structured Reports
    │   └── .arrived/            # Arrival information for series
    └── outbox/                  # Data for external transmission

2.3 Configuration (config.json)
-------------------------------

.. code-block:: json

    {
      "DATADIR": "/data",
      "DICOMPORT": "7840",
      "DICOMIP": "127.0.0.1",
      "DICOMAETITLE": "FIONA",
      "PROCESSING_USER": "processing",
      "SITES": {
        "PROJECT_NAME": {
          "DATADIR": "/dataPROJECT",
          "DICOMPORT": "7841"
        }
      }
    }

Processes and Services
======================

2.4 Main Daemons
----------------

1. **storescp** (storectl.sh):
   - DICOM listening port
   - File reception and storage
   - processSingleFile invocation

2. **processSingleFile** (processSingleFile3.py):
   - DICOM metadata processing
   - Image series classification
   - Directory structure creation

3. **detectStudyArrival** (detectStudyArrival.sh):
   - Series transfer completion detection
   - Post-processing initiation
   - Data archiving

2.5 Cron Jobs
-------------

.. code-block:: bash

    # Basic processes (every minute)
    */1 * * * * /var/www/html/server/bin/storectl.sh start
    */1 * * * * /var/www/html/server/bin/heartbeat.sh
    */1 * * * * /var/www/html/server/bin/detectStudyArrival.sh

    # Data processing (every 5 minutes)
    */5 * * * * /usr/bin/python3 /var/www/html/server/bin/populateIncoming.py
    */5 * * * * /usr/bin/python3 /var/www/html/server/bin/createTransferRequest.py
    */5 * * * * /usr/bin/python3 /var/www/html/server/bin/anonymizeAndSend.py

    # Export (every 30 minutes)
    */30 * * * * /var/www/html/server/bin/sendFiles.sh

    # Cleanup (daily)
    0 2 * * * /var/www/html/server/bin/clearOldFiles.sh
    0 3 * * * /var/www/html/server/bin/clearStaleLinks.sh

Monitoring and Troubleshooting
===============================

2.6 System Logs
----------------

- ``/var/www/html/server/logs/`` - main system logs
- ``/home/processing/logs/`` - processing user logs
- Monitoring through syslog

2.7 Common Problems
-------------------

1. **Disk Space Issues**: clearOldFiles.sh, clearExports.sh
2. **Blocked Processes**: heartbeat.sh restarts services
3. **REDCap Problems**: Check tokens in tokens.json
4. **DICOM Connectivity**: echoscu for connection testing

Security
========

2.8 Data Anonymization
----------------------

- Patient identifier removal
- Date modification (42-day shift for RAM-MS)
- DICOM tag export control

2.9 Access Control
------------------

- ``processing`` user for system processes
- ``www-data`` group for web interface
- 777 permissions for shared directories


Backup and Recovery
===================

Backup Strategy
---------------

**Critical Data**:
  - Archive directory (``/data/site/archive/``)
  - Configuration files (``config.json``, ``tokens.json``)
  - REDCap databases
  - Log files for audit trail

**Backup Schedule**:
  - Daily: Configuration and logs
  - Weekly: Full archive backup
  - Monthly: Complete system backup

Recovery Procedures
-------------------

1. **Service Recovery**: Use heartbeat.sh and systemctl
2. **Data Recovery**: Restore from archive backups
3. **Configuration Recovery**: Restore config files and restart services
4. **Database Recovery**: REDCap backup restoration

Performance Tuning
===================

Optimization Settings
---------------------

**Parallel Processing**:
  - Multiple processSingleFile instances
  - Chunked REDCap API calls
  - Background export processing

**Storage Optimization**:
  - Symbolic links instead of file copies
  - Automatic cleanup of old data
  - Compressed archives for export

**Network Optimization**:
  - Connection pooling for DICOM operations
  - Bandwidth limiting for external transfers
  - Timeout management for long operations

Maintenance Procedures
======================

Daily Tasks
-----------

- Monitor disk space usage
- Check service status
- Review error logs
- Verify REDCap connectivity

Weekly Tasks
------------

- Clean up old export files
- Update routing rules if needed
- Backup configuration files
- Performance monitoring

Monthly Tasks
-------------

- Full system backup
- Update documentation
- Review user access permissions
- System security audit
