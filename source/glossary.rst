.. _glossary:

##########
Glossary
##########

*************
Abbreviations
*************

.. glossary::
   :sorted:

   AE
      Adverse Event. Any unwanted medical event in a participant of a clinical study. See also
      :term:`SAE` and :term:`SUSAR`.

   AETitle
      Application Entity Title. The name that identifies a DICOM node (a modality, a PACS or
      Fiona) on the network. Fiona can use the AETitle a study was sent to in order to route
      the study to the right project.

   API
      Application Programming Interface. A technical interface for scripts and programs, for
      example the REDCap API used to export project data automatically.

   CDISC
      Clinical Data Interchange Standards Consortium. Organization that defines standard
      formats for clinical study data. REDCap can export a project in a CDISC format.

   DICOM
      Digital Imaging and Communications in Medicine. The international standard for storing and
      sending medical images and their meta-data (tags such as PatientID or StudyDate).

   DMA
      Part of the name "Sectra DMA Forskning", the start menu item that gives access to the
      research PACS.

   DPIA
      Data Protection Impact Assessment. An assessment of privacy risks that the GDPR may require
      before personal data is processed.

   EDC
      Electronic Data Capture. Collection of study data in electronic forms, in Fiona done in
      REDCap.

   EK
      Elektronisk kvalitetshåndbok. The electronic quality handbook of the hospital that contains
      the official procedures, for example for the research PACS.

   FAIR
      Findable, Accessible, Interoperable, Reusable. Guiding principles for good research data
      management.

   GDPR
      General Data Protection Regulation. The EU regulation on the protection of personal data.

   HBE
      Helse Bergen HF, the health trust that runs Haukeland University Hospital.

   HUNT Cloud
      A secure cloud environment for sensitive research data, run by NTNU (Norwegian University
      of Science and Technology).

   IDS7
      Sectra IDS7, the image viewer and diagnostic workstation software used to view the data in
      both the clinical and the research PACS.

   IKT
      Helse Vest IKT, the IT service provider of the Western Norway health region (IKT:
      informasjons- og kommunikasjonsteknologi).

   PACS
      Picture Archiving and Communication System. A system that stores medical images and makes
      them available for viewing. Fiona forwards data to a separate :term:`research PACS`.

   PI
      Principal Investigator. The person responsible for a research project and the owner of the
      project data.

   REK
      Regionale komiteer for medisinsk og helsefaglig forskningsetikk (Regional Committees for
      Medical and Health Research Ethics). A valid REK approval is required for every project in
      the RIS.

   RIS
      Research Information System. The combination of the research PACS, REDCap and Fiona that
      stores de-identified research data per project.

   SAE
      Serious Adverse Event. An :term:`AE` that is life-threatening, requires hospitalization or
      has similar serious consequences.

   SAFE
      Secure Access to Research Data and E-infrastructure. A secure environment for sensitive
      research data, run by the University of Bergen (|uib_safe_link|).

   SUSAR
      Suspected Unexpected Serious Adverse Reaction. A serious, unexpected reaction that may be
      caused by a study drug.

   TSD
      Tjenester for sensitive data (Services for Sensitive Data). A secure environment for
      sensitive research data, run by the University of Oslo. Fiona can export data to TSD
      projects.

   UID
      Unique Identifier. A globally unique number in DICOM that identifies a study
      (StudyInstanceUID), a series (SeriesInstanceUID) or a single image (SOPInstanceUID).

   VNA
      Vendor Neutral Archive. An image archive that stores data in standard formats, independent
      of the viewer software.

   WSI
      Whole-Slide Imaging. Digital scans of complete pathology slides.


*****
Terms
*****

.. glossary::
   :sorted:

   AccessionNumber
   Undersøkelse-ID
      The DICOM tag that identifies an imaging examination in the hospital systems. Coupling
      lists uploaded in Assign can map accession numbers to projects and participants.

   burned-in information
      Patient information (names, numbers, dates) written into the image pixels instead of the
      DICOM tags. Common in ultrasound and :term:`secondary capture` images. Fiona tries to
      detect and remove it automatically.

   CDRobot
      A destination for exported studies that writes the data to CD/DVD. Available in the
      NoAssign application.

   coupling list
      The list that links the real identity of participants to their pseudonymized
      :term:`participant ID`. It is kept by the project, not by the RIS.

   data access group
      A REDCap feature that restricts users to the participants of their own group, for example
      one group per hospital in a multi-center study.

   de-identification
      Removal or replacement of information that identifies a person. Covers both
      :term:`pseudonymization` and :term:`anonymization`.

   anonymization
      De-identification without any way back to the real identity: no :term:`coupling list`
      exists. Anonymized data is no longer personal data.

   e-Consent
      Electronic consent. A REDCap form in which participants give informed consent with typed
      names and signature fields.

   edge device
   edge system
      The system at the boundary between the hospital network and the research systems. In the
      RIS this is Fiona: all data enters through it and is de-identified there.

   event name
      The name of a time point or visit in a study (for example "baseline" or "week01"). Every
      imaging study is assigned to a project, a participant and an event name.

   fPACS
      Short for "forsknings-PACS", the research PACS.

   modality
      A device that acquires images (MR, CT, ultrasound, etc.) or the DICOM code for its type.
      The computer that sends the images is called a modality station.

   OneConnect
      A PACS-to-PACS connection that allows images to be shared with other institutions through
      the clinical PACS.

   participant ID
      The pseudonymized identifier of a participant in a project (for example "project_001").
      It replaces PatientID and PatientName in the research PACS.

   pseudonymization
      De-identification where the real identity is replaced by a :term:`participant ID`. The
      identity can be restored with the :term:`coupling list`, so pseudonymized data is still
      personal data.

   quarantine
      The temporary storage on Fiona where incoming studies wait until they are assigned to a
      project. Studies stay there for about 7 days.

   research PACS
      A separate PACS for research data, independent from the clinical PACS but using the same
      software. It contains only de-identified data, grouped by project.

   secondary capture
      Images created by software (for example screenshots from post-processing workstations)
      instead of by a modality. They often contain :term:`burned-in information`.

   study date shifting
      Moving all study dates of a project by the same offset. It hides the real dates but keeps
      the time between examinations correct.

   transfer request
      The record in REDCap that tracks the forwarding of one imaging study from Fiona to the
      research PACS.

   worklist
      A list of studies in IDS7. Static worklists ("Ny statisk arbeidsliste") can be used to
      group studies, for example the studies used in one publication.
