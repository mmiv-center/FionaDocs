RIS Exports - User Documentation
================================

Application Description
-------------------------

RIS Exports is a medical data export system from PACS (Picture Archiving and Communication System) designed for users with export permissions. It enables creation of data sharing packages from DICOM images with de-identification/pseudonymization options, supports various export formats, and allows downloading ZIP files or sending them to TSD (Services for Sensitive Data). The application integrates with the REDCap system for demographic data management and offers series filtering functions and background processing for large studies.

Access to the Application
-------------------------

* Login to the system is required
* "Export" permissions for the project are necessary
* Contact for access: |admin_email| or Zhanbolat

How to Use the Application
--------------------------

1. **Project Selection**
   * From the dropdown list, select the project from which you want to export data
   * Only projects to which you have permissions are available

2. **Export Configuration**
    * **Pseudonymization Type**: Choose the de-identification/pseudonymization method
      * Research PACS format (default) - format with series information, DICOM.zip
      * RAM-MS anonymization - RAM-MS anonymization, DICOM.zip
      * Transpara type export - Transpara type export, DICOM.zip
      * NIFTI export - NIFTI export, NIFTI.zip
      * Siemens Spectroscopy only - Siemens Spectroscopy only, DICOM.zip
   
    * **Package Destination**:
      * Download - direct download
      * TSD - Services for sensitive data (University of Oslo)

3. **Participant Selection**
    * The participant list appears automatically after selecting a project
    * You can filter the study list using the search field
    * Check the checkboxes next to selected participants or use "Select All"

4. **Actions for Participants**
    * **Download** - direct ZIP file download
    * **Prepare** - background package preparation (for large studies)
    * **Change DOB, Age, Sex** - edit demographic data in REDCap
    * **Secure download (email)** - secure download with email link option
    * **Reset** - remove existing ZIP file (to recreate it if REDCap variables have been changed)

Important Information
---------------------

**Technical Limitations:**
* Image studies with more than 60,000 images may not be supported (HIT_QUERY_LIMIT error)
* Windows may alert you about too long path names in your ZIP files - use 7-zip instead to unpack
* Large studies may be too big for such an export (time-out error) - use "Prepare" option

**Data Security:**
* Data is stored in research PACS as de-identified data
* The project might retain a coupling list so the operation is a pseudonymization for the project
* A packaged study contains all the DICOM images from PACS after a further de-identification step
* Store such ZIP files only on drives that are under special protection, where storing of sensitive data is allowed

**Experimental Features:**
 * **Limit exports to specific series**: You can limit export to selected series
   * Use the Filter application to create a filter
   * Export that filter result as a spreadsheet (CSV format)
   * Upload the resulting spreadsheet here

 * **Specialized export formats**: Project specific data export has to be setup if projects require specialized de-identification procedures
   * Contact us if such a system should be setup for your project
   * Information that has to be corrected or is missing from the DICOM files can be added to the project on REDCap

Helper Tools
------------

* **ReviewZip**: Review your ZIP file in your web-browser to check if DICOM tags like the PatientBirthDate have been handled correctly
* **FIONA download**: Download a manifest file to automate export of all ZIP files

Troubleshooting
---------------

* **HIT_QUERY_LIMIT Error**: Your image study contains more than 60,000 images
* **Time-out Error**: Some studies might be too big for such an export - use "Prepare" option
* **Too long path names**: Windows might alert you about too long path names in your ZIP files - use 7-zip instead to unpack
* **No Permissions**: If you think you should have permission to download data from a specific project contact us to gain access

Contact
--------

* Hauke Bartsch: Hauke.Bartsch@helse-bergen.no
* Zhanbolat Satybaldinov: zhanbolat.satybaldinov@helse-bergen.no 