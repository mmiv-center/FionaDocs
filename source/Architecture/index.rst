ARCHITECTURE
==============

**For:** Developers, system architects

.. toctree::
   :maxdepth: 1


Folder and File structure
--------------------------

.. only:: html

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
                           |    ├── <a href="scripts/heartbeat.html">heartbeat.sh</a>
                           |    ├── <a href="scripts/processSingleFile3.html">processSingleFile3.py</a>
                           |    ├── <a href="scripts/sendFiles.html">sendFiles.sh</a>
                           |    └── <a href="scripts/storectl.html">storectl.sh</a>
                           |
                           └── utils/
                                 └── <a href="scripts/s2m.html">s2m.sh</a>

       </pre>



.. only:: latex

    .. code-block:: html

       /home/processing/
       |          └── bin/
       │               ├── anonymizeAndSend.py
       │               ├── clearExports.sh
       │               ├── clearOldFiles.sh
       │               ├── clearStaleLinks.sh
       │               ├── createTransferRequestsForProcessed.py
       │               ├── createTransferRequests.py
       │               ├── populateAutoID.py
       │               ├── populateIncoming.py
       │               ├── populateProjects.py
       │               └── utils/
       │                      ├── getAllPatients2.sh
       │                      ├── parseAllPatients.sh
       │                      ├── resendProject.py
       │                      ├── whatIsInIDS7.py
       │                      └── whatIsNotInIDS7.py
       │
       /var/
         └── www/
              └── html/
                    ├── applications/
                    │          ├── Assign/
                    │          │     └── php
                    |          |          └── removeOldEntries.sh
                    │          ├── Attach/
                    │          │     └── process_tiff.sh
                    │          ├── Exports/
                    │          │     └── php
                    |          |          └── createZipFileCmd.php
                    │          ├── User/
                    │          │     └── asttt/
                    │          │            └── code/
                    │          │                  └── cron.sh
                    │          └── Workflows/
                    │                 └──php
                    |                    └── runOneJob.sh
                    │
                    └── server/
                           ├── bin/
                           |    ├── heartbeat.sh
                           |    ├── processSingleFile3.py
                           |    ├── sendFiles.sh
                           |    └── storectl.sh
                           |
                           └── utils/
                                 └── s2m.sh





Components
-----------------------------

.. only:: latex

    .. toctree::
       :maxdepth: 2
       :hidden:

       scripts/anonymizeAndSend
       scripts/clearExports
       scripts/clearOldFiles
       scripts/clearStaleLinks
       scripts/createTransferRequests
       scripts/createTransferRequestsForProcessed
       scripts/createZipFileCmd
       scripts/cron
       scripts/getAllPatients2
       scripts/heartbeat
       scripts/parseAllPatients
       scripts/populateAutoID
       scripts/populateIncoming
       scripts/populateProjects
       scripts/processSingleFile3
       scripts/process_tiff
       scripts/removeOldEntries
       scripts/resendProject
       scripts/runOneJob
       scripts/s2m
       scripts/sendFiles
       scripts/storectl
       scripts/whatIsInIDS7
       scripts/whatIsNotInIDS7

#. :doc:`scripts/anonymizeAndSend` - Processes imaging studies, performs anonymization, and sends them to research PACS
#. :doc:`scripts/clearExports` - Removes old export files when storage reaches capacity thresholds
#. :doc:`scripts/clearOldFiles` - Removes old studies from ``/data/site/archive`` when disk usage exceeds 80%
#. :doc:`scripts/clearStaleLinks` - Removes broken symbolic links and empty directories from data structures
#. :doc:`scripts/createTransferRequests` - Generates transfer requests for studies that need anonymization and forwarding to research projects
#. :doc:`scripts/createTransferRequestsForProcessed` - Handles transfer requests for processed/derived imaging data from workstations back to research PACS
#. :doc:`scripts/createZipFileCmd` -  Creates anonymized ZIP archives for research data distribution
#. :doc:`scripts/cron` - Processes trigger-action pairs from JSON configuration files for event-driven automation
#. :doc:`scripts/getAllPatients2` - Retrieves patient and study information from research PACS using findscu
#. :doc:`scripts/heartbeat` - Checks DICOM service responsiveness and restarts failed components
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

