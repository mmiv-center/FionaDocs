ADMINISTRATION
===============

**For:** IT administrators, DevOps

.. toctree::
   :maxdepth: 1


End-user contract
-------------------

.. note::

    The following text is from the Apply website for the Steve system. Please check this page for updates to the wording.

By creating a project on the research information system you agree to the following:

1. All data stored in the RIS belongs to the research project owner represented by the PI of the project. Adding and verifying added data to the RIS is the responsibility of the project owner. The RIS team will help research projects to automate this process.

2. Sensitive participant information needs to be stored under a separate account and needs to be accessible to authorized (data-manager and above) user accounts only. All other research data is stored as de-identified data (pseudonymized, with external coupling list) or in an anonymized format. This restriction includes sensitive information such as Norwegian identification numbers, real names or parts of real names, other birth certificate information and initials. It is the responsibility of the project to review the result of the de-identification procedures implemented by the RIS team on image meta-data using https://fiona.medtek.hbe.med.nvsl.no/applications/ReviewDICOMTags and the result of the detection and removal of burned in image data (IDS7). The project will inform the RIS team in a timely manner if the
pseudonymization procedure of the RIS team needs to be updated. This restriction is in place to allow for the largest possible user base for the RIS including PhD students and external collaborators.

3. All research data is stored as part of RIS projects identified by a project name of 5-20 characters. Users can gain access to the data upon request from the project PI or an appointed representative of the PI.

4. Projects are expected to utilize best-practises for data handling such as accounts based on roles like data-entry (add data only) and data-manager (change data, export data). Personally identifying fields have to be marked as such (Identifier? field of the instrument designer) and data access groups shall be used for multi-site project setups.

5. Projects will undergo a short review from the RIS team before they are moved by the RIS team from development mode into production mode for data capture. This review may generate suggestions for the project on how to implement best practices for longitudinal data captures, missing validation and the use of additional software features. All research data is collected and stored with a valid REK approval for the time period specified in the REK approval. The REK approval is required at the time that the RIS project is created. Any change of the REK approval start and end dates need to be reported to the RIS team. At the end of the project period data can be either: a) deleted or  b) fully anonymized (suggested choice). It is up to the project to inform the RIS team about the correct way of handling the data at the end of the project. By default we will assume that data needs to be deleted. Based on the project end date (REK) the RIS team will inform the PI of the project of a pending change of the project status to the archive state. An archive state project will not allow for further data entry, or changes to captured data. After a period of about 1 year the project data will be exported and provided to the project PI for download. An archived project can be deleted by the RIS team after an unspecified time period. If the project data can be fully anonymized, the RIS team may create a copy of the data with new participant identifiers (without a coupling list). After a re-import a fully anonymized version of the project data can become accessible to other RIS users. The original project data will change to archive state, a copy is provided to the projects PI and the data can be deleted by the RIS team after about 1 year.


Features for data migration
----------------------------

The Assign web-application allows users to upload a coupling list that maps the accession number (Undersøkelse-ID) of the study to the pseudonymized participant identifier. Such mappings must be uploaded before the first image study of the project has been forwarded to FIONA. Incoming DICOM studies in FIONA that match entries in the coupling list will automatically be assigned to the project.

How to handle errors?
----------------------

Correcting errors during data import are not difficult to fix. Try to follow up on such errors on an ongoing basis. The quarantine FIONA station may have still have a copy of the data in its cache which simplifies the process. Contact Hauke.Bartsch@helse-bergen.no in such cases and ask for help. This will allow you to fix issues such as:

- Wrong assignment of participant identifiers to DICOM studies
- Wrong assignment of event names to DICOM studies
- Missing images or image series for existing DICOM studies
- Missing entries for DICOM studies on “Assign”


Export to project specific formats, NIfTI and zip-files
---------------------------------------------------------

The research information system supports a separate export facility that is more suited to implement project specific de-identification. Such export requirements include specific DICOM value changes (replacing underscores with dashes), adding birth date information back, formatting and cleaning of series descriptions, zip-file exports with specific folder structures etc.. This export is appropriate if the receiving institution has specific requirements on how data should be shared.

Request access to the specialized data exports for your project from Hauke.Bartsch@helse-bergen.no. Provide your export specification and we will implement your anonymization scheme and make it available to you and other researchers. As an example the “Export” application currently supports the export in NIfTI formats (using dcm2niix) and the export in several zip-file formats.


Sensitive Data Projects – Separation of Sensitive Information and Data
-----------------------------------------------------------------------

A sensitive data project is one that is used to capture human subject data and in general will require a REK (regional ethics board approval). In order to setup such a project in REDCap we suggest the follow structure and features of REDCap to be used. These recommendations have been generated based on discussions in relevant risk assessments.

All sensitive data should be stored in a separate REDCap “ID” project including Norwegian Identification Numbers, names or parts of names, addresses and full birth dates (see Figure 1). This project should have its own roles of “Data Manager”, “Data Entry”, and “Controller”.  eople with permission to access and/or edit this information can use this database to keep contact information up-to-date and to enroll new participants into the study. Each participant should be assigned a pseudonymized ID in the sensitive data project that links the entry to the corresponding participant in the data project. Examples for this ID are: <project name>-<site number>-0001, <project name>-<site number>-0002, etc..

All other data should be stored in a separate REDCap “Data” project using the pseudonymized participant ID as a “record_id” (first field in the study).

.. figure:: ../_static/redcap-sensitive-data.png   
   :align: center

   Sensitive data projects should be split into a REDCap project for data (using pseudonymized ids) and a REDCap project for sensitive data including the coupling list.


User rights management
~~~~~~~~~~~~~~~~~~~~~~~~


When a project leader / principal investigator (PI) is given a REDCap account and project, they are given “project owner” roles. The project owner can then provide access to project members in “roles”. A role defines a given set of custom permissions which defines the user’s access to data, export permissions and ability to make changes to data.

Each project can have predefined roles. We recommend the predefined roles “Data Manager” (ability to change study design, export), “Data Entry” (add, change, or delete data) and “Controller” to define roles for data viewing, editing, and deleting records. In more complex cases, different access settings can be given on different forms in the study (see also API access with REDCap). Individual users are assigned to project roles as part of gaining access to one project.

The user rights management is the responsibility of the project owner and/or the users they add to the project with User Rights access. User roles should be set at the lowest access level that is necessary (e.g., export rights only for users who need this permission). Access to the project should be reviewed regularly and personnel who no longer require access need to be removed from the project.


User rights – multi-center projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a project where several institutions participate with their own project participants (several hospitals etc.) each group of participants should be assigned to a separate “data access group”. This functionality allows records in a study to be part of the user rights management. A user with access to a single data access group can only see participants that belong to this group. If this user creates a new participant, they will be automatically assigned to the group.


How to handle Email Addresses in Data Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Email addresses are special identifying fields that can be stored in data projects for the purpose of creating automated invites for participants to fill out forms from home. In projects that use this feature email fields need to be present in the data project in order to allow for email distribution to participants.

1. Add such email fields to a separate instrument of the REDCap data project and mark the instrument as viewable by specific roles only (like Data Managers).
2. Mark the email field as an “Identifier” field to prevent export of the field’s data by user  of roles that cannot view sensitive fields.
3. Add the Action Tag “@PASSWORDMASK” to the field to prevent accidental viewing of the fields values if the instrument is displayed on screen.
4. Add a field validation as “Email” to prevent some miss-typing of emails.


Automatic data exports from REDCap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data may be exported from REDCap using the REDCap API, a technical interface to automate the export of project and participant information using scripting. To provide such access a dedicated user-account "api_<real username>" should be created which is specific for a single project. Configure the account with a limited set of read permissions to specific fields or instruments using a new API role. The REDCap API will borrow these restrictive permissions for controlled access.

Setup: An administrator can generate an API "token" for this account and share the token and examples of accessing the resource (curl-based access) with the user.

Any change in the role of the <real username> should also apply to the connected API account. Specifically loosing access to the project should be implemented for both <real username> and api_<real username>.


Steps at the end of a REDCap project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REDCap is a tool for data collection. At the end of data capture projects using REDCap receive a notification of study end. At this point projects may provide updated REK information(extension of data capture notice). If no such notice is received REDCap projects will:

- Lock all data participants (no further update/add).
- Provide a copy of the REDCap project (CDISC format) to the project’s principal investigator or delegate.
- Provide a copy of the project data (CSV) and data dictionary (PDF) to the principal investigator or delegate.
- Request a confirmation that project data (CDISC and CSV) have been received by the project.
- Permanently delete all project data.

This process will be documented in the REDCap project tracking project “DataTransferProjects”, the project management tool with information on identity of the person requesting project removal and confirmations for all steps of the project removal process.

.. figure:: ../_static/redcap-end-of-project.png   
    :width: 80%
    :align: center
    
    End-of-project tracking for REDCap projects
