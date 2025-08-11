Export image data from research PACS
---------------------------------------

Data in the research PACS is secured by generic procedures during data import that delete or rewrite some DICOM tags, changes dates and replaces unique identifiers. A documentation of this process is available on the GitHub repository of the projects for removal of DICOM meta-tags: |github-dicomanonymizer_link| (|github-dicomanonymizer_url|), and for the removal of burned in image information: |github-rewritepixel_link| (|github-rewritepixel_url|).

Data stored in the research PACS is therefore in general suited for data sharing IF pseudonymized data is allowed. In order to support users with the task of data pseudonymization the research information system provides the “Review” web application that lists all existing DICOM tags in a research project (|fiona_url|).

.. note::

   Pseudonymized data is defined here as data for which a coupling list exists somewhere in the universe. This is in contrast to anonymized data where such a list does not exist and can also not be created.

Further de-identification procedures might require changes to image data such as face stripping, removal of outer ear tissue, cortical folding pattern, etc.. Such potential sources of information for re-identification have been proposed in the literature but actual attacks based on them have not recently been documented. Better documented and perhaps more relevant are re-identification using spreadsheet data where external sources are linked to the projects data to discover the supposedly hidden identity of the research participants. For example it might be possible to link Gender, day of birth and the hospital name to a real participant name using a birth or voting registry.


**Export using IDS7**

The image data from a study can be exported from the research PACS using a right-click menu entry available in the Informasjonsvindu “Exporter til medium”. Such exports will generate either a derived patient ID – if an Anonymization Profile is selected or a faithful copy of the data with all pseudonymized DICOM tags intact.

.. note::

   This export does not prevent re-identification. Specifically the PatientID field is created from the pseudonymized ID used in the research PACS and therefore not random.

The export is also case-by-case, which is tedious if many data need to be exported. The export will also result in directory names that do not reflect the research project structure as participant identifier – event name – modality – image series. It may be advantageous to export from IDS7 if a single image study needs to be shared without special requirements. Such export folders will also contain an image viewer.


**Export to project specific formats, NIfTI and zip-files**

The research information system supports a separate export facility that is more suited to implement project specific de-identification. Such export requirements include specific DICOM value changes (replacing underscores with dashes), adding birth date information back, formatting and cleaning of series descriptions, zip-file exports with specific folder structures etc.. This export is appropriate if the receiving institution has specific requirements on how data should be shared.

Request access to the specialized data exports for your project from Hauke.Bartsch@helse-bergen.no. Provide your export specification and we will implement your anonymization scheme and make it available to you and other researchers. As an example the “Export” application currently supports the export in NIfTI formats (using dcm2niix) and the export in several zip-file formats.

Research Information System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The research information system (RIS) of the Western Norway Health Authorities (Helse-Vest) also called the "Steve Project" is a secure computer system that stores research data for approved research projects at Haukeland University Hospital and connected hospitals of the Helse Vest region. The project is supported by the radiology department of Haukeland University Hospital and the Mohn Medical Imaging and Visualization Center and approved for research project use by IKT Helse Vest. The physical location of the data is at the premises of IKT Helse Vest Norway. Dedicated storage area and research software (Sectra, IDS7) provides researchers with appropriate permission access to their data. All data is stored in a de-identified format inside the RIS. Maintaining a coupling list is the responsibility of each project and not part of the functionality of the RIS.

Based on the REK/DIPA rules for each project a lifetime tracking of the research data per project ensures that data can be anonymized based on data sharing requirements, and that data can be deleted at the end of the project phase - if required. We suggest that research data is allowed to be fully anonymized at the end of the project and remain in RIS for general research access.

Key features of the RIS include:

- Hosted side-by-side with the clinical PACS as an independent installation.
- Accepts de-identified patient identifiers only.
- All data is moved through a de-identification process upon import into RIS.
- All data is assigned to one or more specific research projects and the visibility of data is restricted to individuals with project role access rights.
- Projects require a valid REK approval, such documentation has to be provided at the start of a project by the project owner.
- The project owner can identify additional user accounts that can access the data.
- User access to the research PACS is controlled by IKT and requires a valid Haukeland University Hospital user account.
