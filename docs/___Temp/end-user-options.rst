.. toctree::
   :maxdepth: 0
   :hidden:
   

*** END USER (options) *** 
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For:** Doctors, researchers, medical personnel

**Should contain:**

- How to use the FIONA interface
- How to browse medical images
- How to export data
- Step-by-step instructions
- Interface screenshots
- FAQ for users

-------

System Overview
~~~~~~~~~~~~~~~~~

The Fiona system is a comprehensive solution for managing DICOM medical images in a research environment. The system enables automatic reception, processing, anonymization, and transfer of imaging data between different PACS (Picture Archiving and Communication System) systems.

Core Functions for End Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.1 DICOM Image Reception and Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Automatic Reception**: The system automatically receives DICOM images from various scanners and workstations

**Series Classification**: Images are automatically classified according to defined rules

**Multi-Modality Support**: MR, CT, US, SR (Structured Reports), PR (Presentation States)

1.2 Research Project Management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Multi-Project Environment**: The system supports multiple independent research projects

**Data Routing**: Automatic routing of data to appropriate projects based on rules

**Auto-ID**: Automatic generation of participant identifiers for projects

1.3 Export and Archiving
^^^^^^^^^^^^^^^^^^^^^^^^^

**Multiple Export Formats**:
  - Native DICOM
  - NIFTI (for neuroimaging)
  - PURE (directory structure by series description)
  - Spectroscopy (spectroscopic data only)

**Anonymization**: Automatic removal of patient identifying data

**Secure Downloads**: Ability to create password-encrypted archives

1.4 REDCap Integration
^^^^^^^^^^^^^^^^^^^^^^^

**Data Synchronization**: Automatic synchronization with REDCap databases

**Transfer Requests**: Management of data transfer requests

**Metadata**: Storage and management of project metadata


Supported File Types
---------------------

DICOM Images
^^^^^^^^^^^^^
- All standard DICOM modalities
- Multi-frame and enhanced DICOM objects
- Structured reports and presentation states


Export Formats
^^^^^^^^^^^^^^^
- **DICOM**: Original format with anonymization
- **NIFTI**: Neuroimaging format with JSON sidecars
- **PURE**: Organized directory structure
- **RAM-MS**: Specialized format for multiple sclerosis studies
- **Transpara**: Format for prostate imaging studies

User Interface Components
---------------------------

Exports Application
^^^^^^^^^^^^^^^^^^^^
- Search and filter studies by project, participant, date
- Select export format and anonymization level
- Download encrypted archives
- Track export status and history

Assign Application
^^^^^^^^^^^^^^^^^^^
- View incoming studies awaiting assignment
- Manual assignment to research projects
- Coupling list management
- Study metadata review

Attach Application
^^^^^^^^^^^^^^^^^^^
- Upload whole slide imaging files
- Automatic conversion to DICOM format
- Metadata extraction and validation
- Integration with pathology databases

Workflows Application
^^^^^^^^^^^^^^^^^^^^^^^
- Launch containerized analysis workflows
- Monitor processing status
- Access results and outputs
- Integration with research pipelines


Support Contacts
^^^^^^^^^^^^^^^^^^
  Emails
