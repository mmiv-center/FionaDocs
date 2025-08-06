whatIsInIDS7.py
~~~~~~~~~~~~~~~~

The ``whatIsInIDS7.py`` script processes DICOM medical imaging files from the IDS7 research PACS system and extracts metadata to populate a ``REDCap`` database. It parses DICOM files using ``dcm2json``, extracts key study information (patient data, study details, series counts), handles duplicate studies by merging data, and uploads the processed information to REDCap via API calls. The script can process all studies or filter by institution name when provided as a command-line argument.


**Related Files**

.. mermaid ::

   flowchart TD
    A["getAllPatients)"] --> B["parseAllPatients"]
    B --> C["whatIsInIDS7.py"]
    C --> D["REDCap Database"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A inputFile
    class B inputFile
    class C mainScript
    class D outputFile





**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/tmp/pullStudies*/\*/\*<br>(DICOM files)"] --> B["whatIsInIDS7.py"]
    B --> C["REDCap Database"]
    D["dcm2json<br>(DCMTK tool)"] --> B
        
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A inputFile
    class D inputFile
    class B mainScript
    class C outputFile



Data Paths:

- Input paths:

   * ``/tmp/pullStudies{InstitutionName}/*/*`` - DICOM files directory structure Command line arguments: sys.argv[1] (optional institution name filter)

- Output paths:

   * ``REDCap`` API endpoint

- External dependencies:

   * ``dcm2json`` - DCMTK toolkit
   * ``/usr/share/dcmtk/dicom.dic``



















----------------------------


.. include:: whatIsInIDS7.py
   :start-after: """
   :end-before: """
