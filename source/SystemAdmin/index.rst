System Administration
***********************

Fiona Admin
=============

**For:** Fiona admin

Fiona administration will need to perform the following tasks

  - create of a new project
  - provide access to existing project to new user
  - fix pseudonymization errors on request from users
  - archive finished projects

Create a new project space
--------------------------

A new project is created in the **DataTransferProjects** table (REDCap). The information in that form indicate how images are changed from clinical space into (pseudonymized) research space. For example incoming DICOM data can contains measurements (presentation state objects) and screenshots (secondary capture images). Some project would want to have such data removed and only transfer **raw data**. The DataTransferProjects record will indicate these choices for each individual project. Fiona reads that information from DataTransferProjects when new images arrive.

Additionally to the record in DataTransferProjects a new project also receives a dedicated REDCap project with the same name as the record identifier in DataTransferProjects. This project is used to **design** the study layout. For example how many visits will be moved for each participant in the study. These REDCap **events** are read by Fiona and used to populate the **Assign** page (list of named visits).

Note: If the REDCap project is used by the researchers for collecting additional data some events might be non-imaging. Those events can be marked in the REDCap project and will not appear on the Fiona interface.

Create a new API key for your admin user to access the project. Store that access key in the DataTransferProjects record for the project together with the project number.

Create the project space on PACS. This depends on the PACS but it should code for project identity in the image data using the **InstitutionName** DICOM tag as the project name. Users with a project role should be able to see such DICOM files.

Enable the project by setting the DataTransferProjects table entry for **Active Project** to allow it to show up on Fiona.

Provide access to new user
--------------------------

A new user needs access to PACS and a role assignment that allows them to see the image data there. No dedicated account is required on Fiona or REDCap. Such access is only provided if Fiona is used for automated data export (can also be done directly from PACS) or if REDCap is used by the project to collect additional research information.

Fix pseudonymization errors upon request
----------------------------------------

As DICOM data arrives randomly on Fiona based on other traffic on the network the research identify of a clinical dataset is cached in REDCap (project **Incoming**). In case an assignment was done in error such cached information needs to be removed before data can be forwarded again to fix the issue.

Identify the study using the Incoming project on REDCap. Records are stored there by study instance uid. Each record will have a transfer request attached. Delete either the whole record or the transfer request. Secondarily remove the data from research PACS. This might involve 3 separate steps. First you need to pull the study from the PACS archive, next you need to reset the study to original (removes the archive copy) and lastly you can delete the study. These steps require special permissions on the PACS system.

As a last step inform the user that he/she can start again sending the data to Fiona and use Assign to enter the correct research identity for that record.

.. note::
  
  For a while Fiona will have a copy of the data. Such copies are deleted automatically by Fiona over time. If you want to remove this cache you can manually delete such cases from ``/data/site/archive/scp_<study instance uid>/`` and from ``/data/site/raw/<study instance uid>``. If you remove the data in such a way you still need to remove them with the above mentioned steps from Incoming and from PACS.


Archive finished projects
-------------------------

Project data can be assigned to a project space as long as the project is under a current institutional review board permission (REK). At the end of that period, after all data have been added to the project the **Active Project** checkbox in DataTransferProjects should be removed. This will remove the projects name from the Assign application on Fiona so no more data can be added.

If the REDCap project is used for additional data capture it should also be moved to data analysis and archive state.

Such archiving should be done in communication with the researcher. They can request a offline version of their data - use the Fiona application **Export**.

An issue that requires further work is how to finally remove the project data from PACS to free up space. Different from clinical data which is stored for longer periods the research data can be archived on external systems (like Sigma2). Access to the PACS system is required to delete data on bulk.


IT Admin
==========

**For:** IT admin

Setup / Installation
----------------------

FIONA can be deployed on a single Linux-based virtual machine. For best performance we suggest to use a dedicated database system (MariaDB). At Helse Vest the FIONA virtual machine setup is

.. code-block:: json

   {
     "architecture": "x86_64",
     "cpus": "16, Intel(R) Xeon(R) Gold 6154 @ 3.00GHz",
     "memory": "64GB",
     "partitions": { 
       "/": "200GB",
       "/data": "1,000GB",
       "/export": "2,000GB",
       "/var/lib/docker/overlay2": "200GB"
     }
   }

The database server running MariaDB should be able to scale based on the detailed logging information generated by REDCap for its 21 CFR Part 11 compliance. At our institutions the system is running with 200GB main memory (5 years of operation) and an off system backup.

The FIONA website is running on apache2 as the webserver, which requires a certificate (https). REDCap is provided as an apache virtual host (port 4444).


System maintenance
--------------------

In the Helse Vest health region FIONA is running on an Ubuntu LTS server with automated updates (unattended-upgrades package). A reboot entry in cron ensures that kernel updates become effective on a weekly basis.

.. code-block:: bash

   // default entries in /etc/apt.conf.d/50unattended-upgrades
   Unattended-Upgrade::Allowed-Origins {
      "${distro_id}:${distro_codename}";
      "${distro_id}:${distro_codename}-security";
      "${distro_id}ESMApps:${distro_codename}-apps-security";
      "${distro_id}ESM:${distro_codename}-infra-security";
   }

We have made good experiences with always upgrading to the lastest LTS release with ``do-release-upgrade``.

REDCap (Research Electronic Data Capture) is a database interface used by FIONA to store temporary information on the assignment of research identifies to clinical data (based on DICOM numeric IDs such as StudyInstanceUID). Updates of REDCap are frequent and may include security relevant updates. At regular intervals (suggested weekly) check the REDCap Control Center for "New REDCap versions are available to upgrade". Install these updates regularly using REDCap's web interface. REDCap will download and install the newest version on request of the admin user and perform any required updates to its SQL database table structures.


Yearly maintenance
^^^^^^^^^^^^^^^^^^

FIONA will use the database of REDCap continuously requesting information and updating entries. As REDCap is HIPPA compliant (21 CFR Part 11) it will log all such access in two databases that can grow over time to contain millions of entries. We suggest to remove log entries generated by FIONA (user marked as **admin**) to limit the backup size for REDCap. The two tables used by REDCap are **redcap_log_view** and **redcap_log_event**.

To remove entries regularly (once a year) we use code like the following (SQL):

.. code-block:: sql

   DELIMITER //
   CREATE OR REPLACE PROCEDURE redcap.deleteChunksLogEventWhatIsInIDS7()   
     BEGIN
       SELECT MIN(log_event_id) INTO @a FROM redcap_log_event;
       my_loop: LOOP
         SELECT log_event_id INTO @z FROM redcap_log_event WHERE log_event_id >= @a ORDER BY log_event_id LIMIT 1000,1;
         IF @z IS NULL THEN
            LEAVE my_loop;
         END IF;
         DELETE FROM redcap_log_event WHERE log_event_id >= @a AND log_event_id < @z AND project_id = "28" AND user = "admin";
         SET @a = @z;
         SELECT @a;
       END LOOP my_loop;
       DELETE FROM redcap_log_event WHERE log_event_id >= @a AND project_id = "28" AND user = "admin";
     END //
   
   DELIMITER ;
   
   CALL redcap.deleteChunksLogEventWhatIsInIDS7();

The above SQL procedure will chunk the operation based on the index log_event_id. This works even if the database already contains millions of log entries. Note that such removal only marks rows as empty. It does not reduce the size of the database without further optimization. But the removal of log entries will allow the system to re-use them for the continued operation.

The above code removes log events created by the admin user for a project ID "28". This corresponds on our system to a FIONA specific REDCap project called "WhatIsInIDS7". Further project_id's for which entries can be removed are project **Incoming**, **Routing** and **ResearchProjects**. You can lookup their numeric ids in REDCap's user interface.


