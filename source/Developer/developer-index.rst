#########################
Developer Documentation
#########################

**For:** Developers, system architects

Fiona has been developed in Bergen, Norway on behalf of the Helse Vest regional health authorities as a platform to organize data exchange between the different health regions nationally. Specifically Fiona is supposed to enable the secure and high-quality exchange of medical images between research projects in Norway. Such data exchange is required for multi-center projects and for projects in which data processing is done outside the health region that collected the image data.

For such tasks Fiona is supposed to (i) provide tools that link image data across Fiona instances. (ii) Provide algorithms that can process image data across institutional borders and (iii) verify and ensure that data processing tasks leave data in a state suitable for further data exchange and analysis. 

Fiona is organized as a hierarchical system of applications that access common functionality and data processing services. Each application is build for a specific purpose and allows for access control and tracking of all user initiated actions. Any new application should use existing base services and work together with other applications. Its design should allow us to distribute such applications to any other Fiona instance.

Note: Inform us on any development you are starting. We would like to support such works if possible to enhance Fiona and make it easier for researchers to use the system.

************************
Setup a new application
************************

Start by copying an existing application that provides a similar user interface. Applications use Bootstrap for a consistent user interface design. Update the bootstrap version of your application to the latest version available on getbootstrap.com. Download all libraries as ESM modules or self contained javascript (min.js) files and add them to the applications /js/ directory. This step is required in case a Fiona installation is working without access to the internet. It is also considered useful to prevent external tracking of the use of these libraries.

All backend features on Fiona are exposed as paths that accept JSON for configuration and deliver data as JSON. These functions are written in php and they will check for local permissions of the current user based on session information.

To support the versioning in Fiona applications should not use the full path from the webserver root. Instead use relative path to refer to the application or other applications. You may also use path that can resolve to the latest version of fiona such as: "https://fiona.ihelse.net/?path=applications/MyApp". 

User permissions
=================

The permission framework on Fiona uses a role-based authorization with basic authentication. The application **User** provides access to this setup. Create a new set of permissions and a role for your application. Add the permissions to your role and assign the role to a test user.

Note: Fiona roles that start with "Project" are roles that are project specific. Such roles if assigned to a user will only allow access if the user has also access to the project.

***********
Components
***********

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


***************************
Folder and File structure
***************************

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
