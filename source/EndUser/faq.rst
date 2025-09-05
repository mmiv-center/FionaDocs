Frequently asked questions
--------------------------


How do I start using the system?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating a project for your data is of course the first step. One the frontpage of Fiona use the link at the top to |fiona-apply_name| for a new research project. After you got access from IKT to the "Sectra DMA Forskning" start menu link you can login there and see your empty project. Start by uploading data to your project following the steps in **How to add image data**.

Creating a project for your data is of course the first step. One the frontpage of Fiona use the link at the top to apply for a new research project. After you got access from IKT to the "Sectra DMA Forskning" start menu link you can login there and see your empty project. Start by uploading data to your project following the steps in How to send data. Information about these first steps are available in the EK handbook (see Forskning / Forskningsprosedyrer, 02.20.7.1 Forsknings PACS).


Where does the data come from?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both clinical and research systems are provided as services inside the hospital system. Whereas the clinical system supports the day-to-day workflows for patient care its sister system for research provides data services on a research cohort level. For imaging data both systems receive data directly from clinical scanners and enrollment into research projects is used by the scanner operators to decide if data is send to both systems or to the research PACS only. Imaging data may also be imported from external media. Non-imaging data is captured in the research system using electronic data capture (EDC) in REDCap. Both the imaging system and the EDC secure access on the project level, provide anonymization procedures and access to the data using role based accounts. They support automated workflows for data analysis and data processing as well as data exchange with third parties.

Best practices for project setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These are not rules, they are more like guidelines. They do may make the difference between an ok project and a project that is nice to work with (see FAIR data use).

 - A research PACS project is more than a copy of all participant data from the clinical systems. Only transfer data explicitly covered in your REK approval - this is actually a rule, not just a recommendation. Patients might be in the hospital and receive imaging appointments for a number of different purposes. Image studies not directly related to your research project should not be transferred. 
 - Limit the number of coupling lists to identify participants in your project. In the best case all project members should use a single pseudonymized (numeric) identifier for each participant linking imamging data with diagnostic information. A single coupling list of participant identifying information and pseudonymized identifier is optimal as it still ensures separate storage of sensitive information from data. 
 - Numerical identifiers for participant ids should use leading zeros ("project_001" instead of "project_1"). This allows for a consistent alphabetic sorting of participants in the research PACS Information window. The number of leading zeroes can be derived from the maximum number of participants in the study. 
 - Utilize non-numeric event names if your study is longitudinal. If you assign all image data to a single dummy event you will have more work later to specify baseline assessments needed for analysis (compute values relative to the baseline assessment etc.). If your project has an open number of events a two-event setup with "baseline" for the earliest good quality DICOM study and "followup" for all other DICOM studies is ok to use. All event-based studies should assign timing-based event names like "pre-op", "post-op", "6month", etc.. The event name is visible in the research PACS if you add the "Referring physician" column to the Information window. 
 - In order to support clinical studies a basic REDCap project (using RIS setup) contains five data collection instruments. 
 - *Basic Demography Form*: The entries in this form are used to link to the pseudonymized participant ID. All three fields usually contain the same value that is linked to the image information for PatientName and PatientID. 
 - *Imaging*: The imaging instrument is automatically populated by FIONA after each data transfer into the research PACS. The basic information captured is the study instance UID, event name, (shifted) study date and the study description. 
 - *Pathology*: The pathology instrument adds to the imaging instrument measures related to pathology imaging such as magnification factors, resolution and stain information based SNOMED-CT. 
 - *Adverse Events*, *Monitoring*, *Record Locking*, *Source Data Verification*: This instrument captures information required for clinical study type data capture. For each participant in the study all found adverse events (AE), serious adverse events (SAE) and suspected unexpected serious adverse reaction (SUSAR) are captured. The instrument includes also a section on medication monitoring, documentation for record locking and a section to document a source data verification step. Not all projects, especially non-clinical drug trials will need all of these fields. Adjust the instrument for your own study as needed. 
 - *e-Consent*: The template for electronic consent shows the use of signature fields to authenticate both the consenter and the consentee. Notice that HTML formatting for e-consent will be removed in the resulting PDF documenting the consent process (restriction of REDCap). Use the section headers as shown in the template file to obtain a better structured PDF version of the consent. Use images and the logo to style your consent.

Adjust instruments that you find useful in your study. Remove any instrument that you do not need.


Can data be deleted?
^^^^^^^^^^^^^^^^^^^^

You will not have permission to delete data yourself - but you can request data to be deleted from the system. Send an email to Hauke with the project name and detailed information of which participant, event, study, and series should be removed. With the same workflow you may request replacement of participants for which the wrong image series where submitted.

Can I use the research information system without an ethical approval (REK number)?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We do accept projects without REK that are for operational support like scan quality control projects. As always, the project owner is responsible to ensure that such a project follows all institutional guidelines. Operational support projects need to agree to the same pseudonymization procedures as other projects.

How to handle participant data after removal of participant consent?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Participants can retract their consent to be part of a running research study at any time. One option for such data is to request a removal of the image data (send email to rDMA team/Hauke). If the data was already part of published research you as the researcher might also have an obligation to store the data in case your findings need to be verified at some point in the future. Not using data in future research and allowing for a later verification of already performed research can be difficult to implement. We suggest in this case that you use one of two approaches. i) Export the raw data that is part of your paper and store an offline copy together with your analysis scripts for any future questions that you might have to respond to. Request data where consent has been retracted to be deleted from the research PACS. All remaining data in the research PACS is therefore ok to include in the next paper. Or, ii) you can use the worklist functionality of IDS7 to create a new worklist ("Ny statisk arbeitsliste") of subsets of participants. We suggest in this case that you work with three worklists, one to track participants that have removed their content - such data remains on the system but such participant data should not be used for future studies. One worklist per publication that contains references to the imaging studies that have been used. And one master worklist with participants that are ok to use in future papers by your project.

What happens at the end of the project?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The end date of a project is specified in the REK approval. We are using this information to inform you between 3 and 6 month before the end of the project. At this point you can request an extension of the project from REK. If such an extension has not be obtained the project data remains on the research PACS but access to the project will be removed by removal of the project role. The data will no longer be visible to you.

Can we send out emails to people at home?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, if your project is on "REDCap on Azure" people can answer to the links they receive by email. This is not possible on our internal (fiona) REDCap. There are some limitations to this functionality on our REDCap on Azure system. Emails are routed through a Microsoft Exchange custom domain which limits outgoing emails from one system to at most 500 emails per minute and 2,000 emails per hour. That limit is shared for all projects on REDCap on Azure. To not interfere with other projects we suggest to use a lower limit of 1,000 emails per day. Contact us if you need to send out more emails per day.
You can help us to increase the number of emails that can go out at once by checking your list of email addresses. Make sure they are all valid. This can help us to improve the reputation of our custom domain which can lead to higher hourly and daily limits.

How to integrate with external vendors?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An external vendor might be a company that performs image analysis for you. This can be done in two basic ways - sending images to the cloud (difficult because of loss of control over data) and installing the vendor software inhouse (much easier). The process to integrate such an external vendor into the research information system includes a number of steps. Namely:
 - Check against existing systems
 - Budget control
 - Risk assessment
 - Data processing agreement
 - Contractual agreements
 - Data protection impact assessment

Whereas some of these steps are mandatory most are dependent on the type of integration and prior work. A working integration will allow you as a researcher to control the sending of images from the research PACS to the vendor software. The software will perform its task and any resulting images will appear back in your project in the research PACS.

How anonymous is the data in the research information system?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As copies of the image data may exist in clinical systems, research image data is considered at least indirectly identifiable personal data. Data exported from the research PACS may retain that property and should be stored on secure systems. According to GDPR this may make it necessary to carry out a Data protection impact assessment (DPIA) prior to processing.

How anonymous is the data in the research information system?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As copies of the image data may exist in clinical systems, research image data is considered at least indirectly identifiable personal data. Data exported from the research PACS may retain that property and should be stored on secure systems. According to GDPR this may make it necessary to carry out a Data protection impact assessment (DPIA) prior to processing.

Do you change the data in any way?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. With input from the project we attempt to anonymize all data forwarded into the project space. This includes changes to the meta-data section and changes to burned in image information of some of the incoming data (secondary captures). These data processing steps are implemented to ensure an anonymization of the data with respect to the Fiona system and a pseudonymization of the data towards the project as they may retain a coupling list.

Why are all the study dates wrong?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The study date is one of the easiest to obtain information in order to link imaging studies between the clinical and the research PACS. This re-identification of participants is discouraged for anyone who is not in possession of the projects coupling list. Accurate timing information of imaging studies may also be required to analyze image data. In order to serve both the need to keep study participant information private and the need to allow for good science we opted to shift data collection dates in a consistent way per project. Relative timing between imaging events is as accurate as in the clinical PACS. It needs to be stressed that this only prevents a direct path to re-identification. Data export using FIONA's "Export" application can be used to undo study date pseudonymization for data sharing that requires correct dates.

Is there a list of DICOM tags changed during import?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, a list of about 270 tags inspected during import is available as part of the source code of the anonymization tool |github-dicomanonymizer_link| (|github-dicomanonymizer_url|). Tags listed with "remove" are deleted, tags listed with "keep" are kept etc.. The following list has been extracted from the anonymizer 2025-09-05.

+---------------------------------------+
| group | tag | DICOM tag name | action |
+---------------------------------------+
| 0008 | 0050 | AccessionNumber | hash |
| 0018 | 4000 | AcquisitionComments | keep |
| 0040 | 0555 | AcquisitionContextSeq | remove |
| 0008 | 0022 | AcquisitionDate | incrementdate |
| 0008 | 002a | AcquisitionDateTime | incrementdatetime |
| 0018 | 1400 | AcquisitionDeviceProcessingDescription | keep |
| 0018 | 9424 | AcquisitionProtocolDescription | keep |
| 0008 | 0032 | AcquisitionTime | keep |
| 0040 | 4035 | ActualHumanPerformersSequence | remove |
| 0010 | 21b0 | AdditionalPatientHistory | keep |
| 0038 | 0010 | AdmissionID | remove |
| 0038 | 0020 | AdmittingDate | incrementdate |
| 0008 | 1084 | AdmittingDiagnosesCodeSeq | keep |
| 0008 | 1080 | AdmittingDiagnosesDescription | keep |
| 0038 | 0021 | AdmittingTime | keep |
| 0010 | 2110 | Allergies | keep |
| 4000 | 0010 | Arbitrary | remove |
| 0040 | a078 | AuthorObserverSequence | remove |
| 0013 | 0010 | BlockOwner | CTP |
| 0018 | 0015 | BodyPartExamined | BODYPART |
| 0010 | 1081 | BranchOfService | remove |
| 0028 | 0301 | BurnedInAnnotation | keep |
| 0018 | 1007 | CassetteID | keep |
| 0040 | 0280 | CommentsOnPPS | keep |
| 0020 | 9161 | ConcatenationUID | hashuid |
| 0040 | 3001 | ConfidentialityPatientData | remove |
| 0070 | 0086 | ContentCreatorsIdCodeSeq | remove |
| 0070 | 0084 | ContentCreatorsName | empty |
| 0008 | 0023 | ContentDate | incrementdate |
| 0040 | a730 | ContentSeq | remove |
| 0008 | 0033 | ContentTime | keep |
| 0008 | 010d | ContextGroupExtensionCreatorUID | hashuid |
| 0018 | 0010 | ContrastBolusAgent | keep |
| 0018 | a003 | ContributionDescription | keep |
| 0010 | 2150 | CountryOfResidence | remove |
| 0008 | 9123 | CreatorVersionUID | hashuid |
| 0038 | 0300 | CurrentPatientLocation | remove |
| 0008 | 0025 | CurveDate | incrementdate |
| 0008 | 0035 | CurveTime | keep |
| 0040 | a07c | CustodialOrganizationSeq | remove |
| fffc | fffc | DataSetTrailingPadding | remove |
| 0018 | 1200 | DateofLastCalibration | incrementdate |
| 0018 | 700c | DateofLastDetectorCalibration | incrementdate |
| 0018 | 1012 | DateOfSecondaryCapture | incrementdate |  | createIfMissing |
| 0012 | 0063 | DeIdentificationMethod | {Per DICOM PS 3.15 AnnexE} |  | createIfMissing |
| 0012 | 0064 | DeIdentificationMethodCodeSequence | 113100/113101/113105/113107/113108/113109/113111 |  | createIfMissing |
| 0012 | 0062 | PatientIdentityRemoved | YES |  | createIfMissing |
| 0012 | 0020 | Clinical Trial Protocol ID | ProjectName |  | createIfMissing |
| 0012 | 0021 | Clinical Trial Protocol Name | ProjectName |  | createIfMissing |
| 0012 | 0040 | Clinical Trial Subject ID | PatientID |  | createIfMissing |
| 0012 | 0050 | Clinical Trial Time Point ID | EventName |  | createIfMissing |
| 0012 | 0051 | Clinical Trial Time Point Description | EventName |  | createIfMissing |
| 0008 | 2111 | DerivationDescription | keep |
| 0018 | 700a | DetectorID | keep |
| 0018 | 1000 | DeviceSerialNumber | keep |
| 0018 | 1002 | DeviceUID | keep |
| fffa | fffa | DigitalSignaturesSeq | remove |
| 0400 | 0100 | DigitalSignatureUID | remove |
| 0020 | 9164 | DimensionOrganizationUID | hashuid |
| 0038 | 0040 | DischargeDiagnosisDescription | keep |
| 4008 | 011a | DistributionAddress | remove |
| 4008 | 0119 | DistributionName | remove |
| 300a | 0013 | DoseReferenceUID | hashuid |
| 0010 | 2160 | EthnicGroup | keep |
| 0008 | 0058 | FailedSOPInstanceUIDList | hashuid |
| 0070 | 031a | FiducialUID | hashuid |
| 0040 | 2017 | FillerOrderNumber | empty |
| 0020 | 9158 | FrameComments | keep |
| 0020 | 0052 | FrameOfReferenceUID | hashuid+PROJECTNAME |
| 0018 | 1008 | GantryID | keep |
| 0018 | 1005 | GeneratorID | keep |
| 0040 | 4037 | HumanPerformersName | remove |
| 0040 | 4036 | HumanPerformersOrganization | remove |
| 0088 | 0200 | IconImageSequence | remove |
| 0008 | 4000 | IdentifyingComments | keep |
| 0020 | 4000 | ImageComments | keep |
| 0028 | 4000 | ImagePresentationComments | remove |
| 0040 | 2400 | ImagingServiceRequestComments | keep |
| 4008 | 0300 | Impressions | keep |
| 0008 | 0012 | InstanceCreationDate | incrementdate |
| 0008 | 0014 | InstanceCreatorUID | hashuid |
| 0008 | 0081 | InstitutionAddress | remove |
| 0008 | 1040 | InstitutionalDepartmentName | remove |
| 0008 | 0082 | InstitutionCodeSequence | remove |
| 0008 | 0080 | InstitutionName | ProjectName |  | createIfMissing |
| 0010 | 1050 | InsurancePlanIdentification | remove |
| 0040 | 1011 | IntendedRecipientsOfResultsIDSequence | remove |
| 4008 | 0111 | InterpretationApproverSequence | remove |
| 4008 | 010c | InterpretationAuthor | remove |
| 4008 | 0115 | InterpretationDiagnosisDescription | keep |
| 4008 | 0202 | InterpretationIdIssuer | remove |
| 4008 | 0102 | InterpretationRecorder | remove |
| 4008 | 010b | InterpretationText | keep |
| 4008 | 010a | InterpretationTranscriber | remove |
| 0008 | 3010 | IrradiationEventUID | hashuid |
| 0038 | 0011 | IssuerOfAdmissionID | remove |
| 0010 | 0021 | IssuerOfPatientID | remove |
| 0038 | 0061 | IssuerOfServiceEpisodeId | remove |
| 0028 | 1214 | LargePaletteColorLUTUid | hashuid |
| 0010 | 21d0 | LastMenstrualDate | incrementdate |
| 0028 | 0303 | LongitudinalTemporalInformationModified | MODIFIED |
| 0400 | 0404 | MAC | remove |
| 0008 | 0070 | Manufacturer | keep |
| 0008 | 1090 | ManufacturerModelName | keep |
| 0010 | 2000 | MedicalAlerts | keep |
| 0010 | 1090 | MedicalRecordLocator | remove |
| 0010 | 1080 | MilitaryRank | remove |
| 0400 | 0550 | ModifiedAttributesSequence | remove |
| 0020 | 3406 | ModifiedImageDescription | remove |
| 0020 | 3401 | ModifyingDeviceID | remove |
| 0020 | 3404 | ModifyingDeviceManufacturer | remove |
| 0008 | 1060 | NameOfPhysicianReadingStudy | remove |
| 0040 | 1010 | NamesOfIntendedRecipientsOfResults | remove |
| 0010 | 2180 | Occupation | keep |
| 0008 | 1070 | OperatorName | remove |
| 0008 | 1072 | OperatorsIdentificationSeq | remove |
| 0040 | 2010 | OrderCallbackPhoneNumber | remove |
| 0040 | 2008 | OrderEnteredBy | remove |
| 0040 | 2009 | OrderEntererLocation | remove |
| 0400 | 0561 | OriginalAttributesSequence | remove |
| 0010 | 1000 | OtherPatientIDs | remove |
| 0010 | 1002 | OtherPatientIDsSeq | remove |
| 0010 | 1001 | OtherPatientNames | remove |
| 0008 | 0024 | OverlayDate | incrementdate |
| 0008 | 0034 | OverlayTime | keep |
| 0028 | 1199 | PaletteColorLUTUID | hashuid |
| 0040 | a07a | ParticipantSequence | remove |
| 0010 | 1040 | PatientAddress | remove |
| 0010 | 1010 | PatientAge | keep |
| 0010 | 0030 | PatientBirthDate | empty |
| 0010 | 1005 | PatientBirthName | remove |
| 0010 | 0032 | PatientBirthTime | remove |
| 0010 | 4000 | PatientComments | keep |
| 0010 | 0020 | PatientID | Re-Mapped |  | createIfMissing |
| 0038 | 0400 | PatientInstitutionResidence | remove |
| 0010 | 0050 | PatientInsurancePlanCodeSeq | remove |
| 0010 | 1060 | PatientMotherBirthName | remove |
| 0010 | 0010 | PatientName | Re-Mapped |  | createIfMissing |
| 0010 | 2154 | PatientPhoneNumbers | remove |
| 0010 | 0101 | PatientPrimaryLanguageCodeSeq | remove |
| 0010 | 0102 | PatientPrimaryLanguageModifierCodeSeq | remove |
| 0010 | 21f0 | PatientReligiousPreference | remove |
| 0010 | 0040 | PatientSex | keep |
| 0010 | 2203 | PatientSexNeutered | keep |
| 0010 | 1020 | PatientSize | keep |
| 0038 | 0500 | PatientState | keep |
| 0040 | 1004 | PatientTransportArrangements | remove |
| 0010 | 1030 | PatientWeight | keep |
| 0040 | 0243 | PerformedLocation | remove |
| 0040 | 0241 | PerformedStationAET | keep |
| 0040 | 0244 | PerformedProcedureStepStartDate | incrementdate |
| 0040 | 4030 | PerformedStationGeoLocCodeSeq | keep |
| 0040 | 0242 | PerformedStationName | keep |
| 0040 | 4028 | PerformedStationNameCodeSeq | keep |
| 0008 | 1052 | PerformingPhysicianIdSeq | remove |
| 0008 | 1050 | PerformingPhysicianName | remove |
| 0040 | 0250 | PerformProcedureStepEndDate | incrementdate |
| 0040 | 1102 | PersonAddress | remove |
| 0040 | 1101 | PersonIdCodeSequence | remove |
| 0040 | a123 | PersonName | empty |
| 0040 | 1103 | PersonTelephoneNumbers | remove |
| 4008 | 0114 | PhysicianApprovingInterpretation | remove |
| 0008 | 1048 | PhysicianOfRecord | remove |
| 0008 | 1049 | PhysicianOfRecordIdSeq | remove |
| 0008 | 1062 | PhysicianReadingStudyIdSeq | remove |
| 0040 | 2016 | PlaceOrderNumberOfImagingServiceReq | empty |
| 0018 | 1004 | PlateID | keep |
| 0040 | 0254 | PPSDescription | keep |
| 0040 | 0253 | PPSID | remove |
| 0040 | 0244 | PPSStartDate | incrementdate |
| 0040 | 0245 | PPSStartTime | keep |
| 0010 | 21c0 | PregnancyStatus | keep |
| 0040 | 0012 | PreMedication | keep |
| 0013 | 1010 | ProjectName | always |
| 0018 | 1030 | ProtocolName | keep |
| 0054 | 0016 | Radiopharmaceutical Information Sequence | process |
| 0018 | 1078 | Radiopharmaceutical Start DateTime | incrementdatetime |
| 0018 | 1079 | Radiopharmaceutical Stop DateTime | incrementdatetime |
| 0040 | 2001 | ReasonForImagingServiceRequest | keep |
| 0032 | 1030 | ReasonforStudy | keep |
| 0400 | 0402 | RefDigitalSignatureSeq | remove |
| 3006 | 0024 | ReferencedFrameOfReferenceUID | hashuid+PROJECTNAME |
| 0038 | 0004 | ReferencedPatientAliasSeq | remove |
| 0008 | 0092 | ReferringPhysicianAddress | remove |
| 0008 | 0090 | ReferringPhysicianName | empty |  | createIfMissing |
| 0008 | 0094 | ReferringPhysicianPhoneNumbers | remove |
| 0008 | 0096 | ReferringPhysiciansIDSeq | remove |
| 0040 | 4023 | RefGenPurposeSchedProcStepTransUID | hashuid |
| 0008 | 1120 | RefPatientSeq | remove |
| 0008 | 1111 | RefPPSSeq | remove |
| 0008 | 1150 | RefSOPClassUID | keep |
| 0400 | 0403 | RefSOPInstanceMACSeq | remove |
| 0008 | 1155 | RefSOPInstanceUID | hashuid+PROJECTNAME |
| 0010 | 2152 | RegionOfResidence | remove |
| 3006 | 00c2 | RelatedFrameOfReferenceUID | hashuid+PROJECTNAME |
| 0040 | 0275 | RequestAttributesSeq | remove |
| 0032 | 1070 | RequestedContrastAgent | keep |
| 0040 | 1400 | RequestedProcedureComments | keep |
| 0032 | 1060 | RequestedProcedureDescription | keep |
| 0040 | 1001 | RequestedProcedureID | remove |
| 0040 | 1005 | RequestedProcedureLocation | remove |
| 0032 | 1032 | RequestingPhysician | remove |
| 0032 | 1033 | RequestingService | remove |
| 0010 | 2299 | ResponsibleOrganization | remove |
| 0010 | 2297 | ResponsiblePerson | remove |
| 4008 | 4000 | ResultComments | keep |
| 4008 | 0118 | ResultsDistributionListSeq | remove |
| 4008 | 0042 | ResultsIDIssuer | remove |
| 300e | 0008 | ReviewerName | remove |
| 0040 | 4034 | ScheduledHumanPerformersSeq | remove |
| 0038 | 001e | ScheduledPatientInstitutionResidence | remove |
| 0040 | 000b | ScheduledPerformingPhysicianIDSeq | remove |
| 0040 | 0006 | ScheduledPerformingPhysicianName | remove |
| 0040 | 0001 | ScheduledStationAET | keep |
| 0040 | 4027 | ScheduledStationGeographicLocCodeSeq | keep |
| 0040 | 0010 | ScheduledStationName | keep |
| 0040 | 4025 | ScheduledStationNameCodeSeq | keep |
| 0032 | 1020 | ScheduledStudyLocation | keep |
| 0032 | 1021 | ScheduledStudyLocationAET | keep |
| 0032 | 1000 | ScheduledStudyStartDate | incrementdate |
| 0008 | 0021 | SeriesDate | incrementdate |
| 0008 | 103e | SeriesDescription | keep |
| 0020 | 000e | SeriesInstanceUID | hashuid+PROJECTNAME |
| 0008 | 0031 | SeriesTime | keep |
| 0038 | 0062 | ServiceEpisodeDescription | keep |
| 0038 | 0060 | ServiceEpisodeID | remove |
| 0013 | 1013 | SiteID | SITEID |
| 0013 | 1012 | SiteName | SITENAME |
| 0010 | 21a0 | SmokingStatus | keep |
| 0018 | 1020 | SoftwareVersion | keep |
| 0008 | 0018 | SOPInstanceUID | hashuid+PROJECTNAME |
| 0008 | 2112 | SourceImageSeq | remove |
| 0038 | 0050 | SpecialNeeds | keep |
| 0040 | 0007 | SPSDescription | keep |
| 0040 | 0004 | SPSEndDate | incrementdate |
| 0040 | 0005 | SPSEndTime | keep |
| 0040 | 0011 | SPSLocation | keep |
| 0040 | 0002 | SPSStartDate | incrementdate |
| 0040 | 0003 | SPSStartTime | keep |
| 0008 | 1010 | StationName | remove |
| 0088 | 0140 | StorageMediaFilesetUID | hashuid |
| 3006 | 0008 | StructureSetDate | incrementdate |
| 0032 | 1040 | StudyArrivalDate | incrementdate |
| 0032 | 4000 | StudyComments | keep |
| 0032 | 1050 | StudyCompletionDate | incrementdate |
| 0008 | 0020 | StudyDate | incrementdate |  | createIfMissing |
| 0008 | 1030 | StudyDescription | keep |
| 0020 | 0010 | StudyID | hash |
| 0032 | 0012 | StudyIDIssuer | remove |
| 0020 | 000d | StudyInstanceUID | hashuid+PROJECTNAME |
| 0008 | 0030 | StudyTime | keep |  | createIfMissing |
| 0020 | 0200 | SynchronizationFrameOfReferenceUID | hashuid |
| 0040 | db0d | TemplateExtensionCreatorUID | hashuid |
| 0040 | db0c | TemplateExtensionOrganizationUID | hashuid |
| 4000 | 4000 | TextComments | remove |
| 2030 | 0020 | TextString | remove |
| 0008 | 0201 | TimezoneOffsetFromUTC | remove |
| 0088 | 0910 | TopicAuthor |                       remove |
| 0088 | 0912 | TopicKeyWords |                       remove |
| 0088 | 0906 | TopicSubject |                        remove |
| 0088 | 0904 | TopicTitle |                          remove |
| 0008 | 1195 | TransactionUID |                      hashuid |
| 0013 | 1011 | TrialName |                           PROJECTNAME |
| 0040 | a124 | UID |                                 hashuid |
| 0040 | a088 | VerifyingObserverIdentificationCodeSeq | remove |
| 0040 | a075 | VerifyingObserverName |               empty |
| 0040 | a073 | VerifyingObserverSequence |           remove |
| 0040 | a027 | VerifyingOrganization |               remove |
| 0038 | 4000 | VisitComments |                       keep |
| 0033 | 1013 | MITRA OBJECT UTF8 ATTRIBUTES 1.0,/*SomeSiemensMITRA,*/                    remove |
| 0033 | 1016 | MITRA OBJECT UTF8 ATTRIBUTES 1.0,/*SomeSiemensMITRA,*/                    remove |
| 0033 | 1019 | MITRA OBJECT UTF8 ATTRIBUTES 1.0,/*SomeSiemensMITRA,*/                    remove |
| 0033 | 101c | MITRA OBJECT UTF8 ATTRIBUTES 1.0,/*SomeSiemensMITRA,*/                    remove |
| 0009 | 1001 | SectraIdentRequestID |                remove |
| 0009 | 1002 | SectraIdentExaminationID |            remove |
| 0071 | 1022 | SIEMENS MED PT |                     incrementdatetime |
+----------------------------------------------------------------------+

The placeholder "PROJECTNAME" will be replaced with the name of the research project during pseudonymization.

Tags not listed above are untouched by the pseudonymization tool.

Can I export to TSD/Safe?
^^^^^^^^^^^^^^^^^^^^^^^^^

TSD supports data upload links. This API is expected by our system to allow a direct submission of data folders (zip-format) to your TSD storage space. This feature has to be setup for your projects, contact us to receive more information. There is no comparable technology for Safe yet. Contact Christine Stansberg to request such an interface.

The following information from your TSD project on (https://data.tsd.usit.no/i/) are required:

 - TSD group name:
 - TSD ID: e0b0c0e-abcd-abcd-abcd-a0b0c0d0e0f0 (example)
 - TSD user name.


Can I export to clinical PACS?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, export to clinical PACS is possible using "NoAssign". Mostly this option allows pseudonymized data to be forwarded to other institutions using clinical PACS to PACS features like OneConnect.

In order to send to clinical PACS use the NoAssign application of fiona. You may need "Export" permissions for your project to use this application. The application will list all studies currently found in quarantine on fiona. Specify the project, participant, event information and the workflow type "FIONA anonymization". Select the examination you want to forward and "Export...". A dialog "Are you sure?" will allow you to select a destination in the final step. Both "CDRobot" and "clinical PACS" are supported destinations.

.. note::
   Additionally to the standard pseudonymization done by fiona files will have a fake Date of Birth (0010,0030) DICOM attribute value of "19000101". This may be required if receiving PACS systems expect valid clinical data. By default the value of this attribute is empty inside research PACS. Only exporting data using NoAssign will add the dummy value.

*PACS to PACS connectivity*: If images pseudonymized on FIONA are forwarded to another PACS inform them on how to find your pseudonymized images. Tell them:

 - The AccessionNumber (Undersøkelse-ID) DICOM tag will start with the letters "FIONA" followed by some random letters and numbers.
 - The PatientName and PatientID tags will be the same (entered on FIONA, can be something like <project>_<numeric_id>, e.g. "TOBE_0022").
 - The ReferringPhysician DICOM tag will contain the name of the imaging event (e.g. "Eventname:baseline").
 - Further information on the pseudonymization procedure can be found here: |github-dicomanonymizer_url|

What other types of data can you store in PACS?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Our PACS system can store image data from radiology, cardiology, urology, oncology (DICOM) and pathology (whole-slide image format). Other types of files can be embedded into DICOM and stored that way. For example, the Siemens Spectroscopy (DICOM) format (.ima files) can be stored and exported again. These files can be read successfully by spectroscopy software packages like OXSA. The Siemens TWIX format (.dat, .rda) are not suitable for PACS storage, use the .ima format instead.

Some of the spectroscopy DICOM files are non-image files. PACS viewers might not show them in the interface. In order to verify that they are stored correctly (other than downloading them again using Export) the FIONA system will add a secondary capture image that lists the hidden non-image objects including their size and series description.

The generation of the secondary capture image is currently limited to Siemens non-image files (SOPClassUID = 1.3.12.2.1107.5.9.1). Contact your FIONA team if you want to include other files.


Research information system
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have created a research information system in response to common issues faced in integrating research algorithms into clinical practise. We started with a system that required many people to work together to provide access to research data, which does not sound like a bad thing, research is based on good cooperation between many people with diverse backgrounds. Looking at the type of things that needed to happen you realize that highly skilled hospital staff hand-carried a bag filled with 80 individual DVDs from one hospital area to another. Those DVDs each contained individually de-identified radiological images exported from an MRI machine where such a process may take up to 10 minutes per disk.

Based on these experiences we realized that many research tasks required for the successful running of a medical research study like data identification, data export, de-identification are not well supported if research institutions are setup as external entities to the health-care enterprise they are supposed to benefit.

The purpose of the Fiona Project is to create a research information system that no-one is affraid of using and that provides an interface between hospital procedures that generate data and research institutions that consume them. The system focuses on supporting two aspects of medical data - all the lab samples, questionnaires, diagnosis reports and clinical history and the medical image data in the form of DICOM images.


Safety first - Separation of hospital and research
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our research information system is independent from the clinical systems at our hospitals. It is setup as a shadow system that connects to all hospital infra-structure and that has the overall shape and appearance of the clinical system but it is specifically geared to serve the needs of research projects.

How similar are the hospital and the research systems? Both hospital and research system use the same user accounts and permission services (active directory). This allows us to provide access to our research services with the same user-names and passwords as for the clinical system. Both the hospital and the research system use the same version of a vendor neutral archive and image viewing software (PACS). Whereas the instances of the clinical and the research system are separate and data storage is independent features of the clinical system like modality specific hanging protocols, image annotation tools and keyboard shortcuts are shared. This provides access to commercial image viewing software to researchers for data inspection and quality control which is essential for machine learning projects. For their clinical partners it provides a familiar interface to rate the products of research algorithms. Most importantly is removes the gap between the quality of data generated by research tools and the quality and level of automation that needs to be provided if they want to be evaluated for clinically use. This allows researchers to act as solution providers towards the hospital without the need for the integration of the research tools in commercial software applcations frist. Such a safe solution for the clinically relevant accelerated evaluation of novel solutions can help to understand the limitations of novel systems and limit the risks involved in the development of commercial solution.


Safety first - Separation of research projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a clincal setting a health region will share a single clinical system which helps limiting the costs of such systems. Each hospital will be setup to see parts of the data such as all information from the hospital itself but not nessesarily the information from patients at other hospitals. Often this is not a true separatation but it is enforced by individual worklists and role based permissions. A general patient search at one institution will still turn up patients scans at the connected hospitals in the health region. Whereas this is a feature for a clinical system a research information system needs to be more restrictive as access to data is more restricted by regional institutional review boards that allow for the use of research data in approved projects only.

Our system uses project access restrictions to provide a full separation of project data from each other. This includes project specific data identifiers in the VNA that allow project data to be used and deleted without interfering with other projects that might use the same patients data. Only users of the research PACS that are part of the projects role will have access to list the data and to see the assessments and images.


Safety first - Moving data between hospital and research
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Data is transferred only from the hospital to the research information system, not the other way around. This limitation is not technical but operational. Only personnel with access to clinical data can forward such data to be added to a project in the research system. Such data transfers are possible from the clinical PACS as well as from modality systems at all Helse Vest hospitals that collect data as part of research studies.

We decided to store all image data and assessment data in a de-identified form before any analysis. As data is often collected by a research study as part of a general clinical workflow those data are labelled with patient identifying information. This includes names and identification numbers as well as sensitive information on where and when the data was collected. Such information is part of the medical file formats meta-data, burned into the pixel information in files and part of spreadsheets used to track the data.

The data de-identification is implemented as an automated process that connects the clinical systems of a hospital with the research system using an edge-device called FIONA. This system acts as an intermediary translation service that maps sensitive data to de-identified data in the research information system. Input required by the translation service is only a mapping of the clinical data to the particular project, the de-identified patient identifier and the event the data belongs to.


A system aware of study design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whereas clinical system structures each patient individually in a research system participants are grouped on more levels for example by project, research arm, assessment event, imaging study, image series, and individual image. Such complex hierarchies allow for group level analysis of hundreds and thousands of participant data simultaneously without the need to individually export and handle the data. Especially the introduction of an associated event name to collected data allows for many features of statistical analysis. Our system includes these classifications in a central location for both the assessment as well as the image data. This limits the amounts of decision and assumptions that have to be made by various researchers in the structure of their analysis.


Study management and study tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our research information system allows all participant data to be forwarded into the system at the time of data collection as part of a clinical study. There is no time-lag between when data is collected at a scanner and the time that image data is accessible in the research system. If technicians that collect the data are aware of the need to transfer the data into a specific project they will forward the data once to the clinical system - if that is required for safety reads - and a second time into the research systems edge device called FIONA. In a second step they need to assign the project, de-identified patient id and event name to the forwarded data. Such an identification step is the only requirement to map clinical data to the complex structure of research projects. After minutes the data becomes accessible to the research project in a proper de-identified manner.


Data translations from clinical to research system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The list of meta-data tags that are removed by the FIONA edge system when data is assigned to a project is long. We document which tags are changed by making the source code and the process publicly accessible at our |github-dicomanonymizer_link|  page. We hope that this will improve the quality and security of our solution by allowing other groups to evaluate the software in their settings. This includes for example the need to evaluate the de-identified images generated by the software with other image distribution and viewing solutions and the need to test the data interpretation of the tool with new DICOM image files.

Some image data generated in the hospital setting will include textural information about the patient as burned in pixel information. This is common in some modalities such as ultra-sound but also appears in secondary capture images generated by specialized workstations applications for perfusion, diffusion and molecular imaging. Our research information system detects such images and attempts to automatically remove burned in image information by overwriting the detected areas with rectanges of a uniform color. Due to the fully automated process secondary capture images can be forwarded into the research PACS and are safe to use after a review by the project.


Specialized applications
~~~~~~~~~~~~~~~~~~~~~~~~


To provide access to the feature of the research PACS we provide web-applications for data submission, project setup and configuration, review and data export. All of these features are accessible on the home page of the Fiona project page at the institution. Based on your role you will need to use only some of these applications.

Assign
^^^^^^

.. figure:: ../_static/assign.jpeg
   :align: center
   :scale: 50%

.. raw:: html

   <div style="margin-bottom: 20px;"></div>

The Assign application is the entry page for project data. The application lists incoming data that is in quarantine and allows the user to select the appropriate project, de-identified participant name and the event name of the imaging study. This is sufficient for a manual assignment of captured data as it is aquired in the hospital setting. For legacy data and external data in large quantities several automated import strategies are available. If data is de-identified outside of the research information system by writing a new patient ID such files are recognized by the edge system using either the send destination (AETitle of the addressed service on the edge FIONA) or by the pattern used in the patient ID. This detection of incoming data is used to detect the destination research project and trigger the de-identification step without another manual identification step. Additionally to such automated data routing the Assign application also provides a mapping table upload that can be used to identify project and event based on the datas accession number.


Export
^^^^^^

.. figure:: ../_static/export.jpeg
   :align: center
   :scale: 50%

.. raw:: html

   <div style="margin-bottom: 20px;"></div>

As data is already in de-identified format in the research PACS exporting them for the use in external systems is straight forward. The VNA system for example allows users to export individual imaging studies with an embedded image viewer in the same way as clinical systems do. To allow for greater flexibility in data export capabilities the Export web-application allows user to export image data for a project in a variety of file formats. This includes study specific zip files that follow detailed specifications on the embedded directory structures, side-loading description files and the naming of DICOM tags and dates embedded in the data. The Export tool also supports more generic export formats such as NIFTI-format files for volumetric data.

NoAssign
^^^^^^^^

.. figure:: ../_static/noassign.jpeg
   :align: center
   :scale: 50%

.. raw:: html

   <div style="margin-bottom: 20px;"></div>

Fiona's NoAssign application can be used to pseudonymize data without adding them to research PACS. Studies need to be forwarded to fiona.ihelse.net but will remain in quarantine there (for up to 7 days). If NoAssign is used during this time period the user may select a study from the list and either "download" the study as a pseudonymized zip file or forward the pseudonymized study to other clinical systems like "CDRobot" or "clinical PACS".


Review
^^^^^^

.. figure:: ../_static/review-dicom.jpeg
   :align: center
   :scale: 50%

.. raw:: html

   <div style="margin-bottom: 20px;"></div>

Any automated de-identification requires frequent review to ensure that the process is working as expected. In order to support this work by the research project without requiring technical expertise we provide the Review web-application that lists all remaining tags in the data after the anonymization.


Attach
^^^^^^

.. figure:: ../_static/attach.jpeg
   :align: center
   :scale: 50%

.. raw:: html

   <div style="margin-bottom: 20px;"></div>

Image data not already in clinical systems can be uploaded in the Attach application. This includes DICOM files from USB/CD/DVD as well as whole-slide images files for pathology. After uploading them using Attach they will appear in the list of examinations on FIONA and can be either forwarded to research PACS using Assign, or exported again using NoAssign.

Processing
^^^^^^^^^^

Processing of data is a step that links software into the research PACS. Data is forwarded from the project to the software which in turn sends result data back to the FIONA system. Those dataset are automatically forwarded to the research project and appear side-by-side with the original data. This type of integration requires a setup of the software and the setup of a send destination. Examples for such software endpoints are workstations from BrainLab and TeraRecon as well as data processing systems like CerCare and NeuroQuant.


System architecture
~~~~~~~~~~~~~~~~~~~

The research PACS component is designed to run side-by-side with the clinical system.

.. figure:: ../_static/fiona-system-architecture.jpeg
   :align: center

   Research PACS integration into a hospital environment.

