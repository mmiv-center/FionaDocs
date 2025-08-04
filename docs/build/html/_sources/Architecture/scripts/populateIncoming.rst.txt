populateIncoming.py
~~~~~~~~~~~~~~~~~~~~~

This Python script populates the Study and Series information in the Incoming table in REDCap by processing DICOM metadata JSON files. It reads imaging series data from the filesystem, matches them against routing rules and coupling lists, and creates transfer requests for appropriate research projects. The script communicates with REDCap via API calls to store study/series metadata and generate transfer requests for data anonymization and distribution. It supports both incremental updates for new series and full project reimports via command-line arguments.

**Related Files**

.. mermaid::

   flowchart TD
    A["populateIncoming.py<br>(Main Script)"] --> B["REDCap API<br>(Coupling Lists)"]
    A --> C["REDCap API<br>(Routing Rules)"]
    A --> D["REDCap API<br>(Incoming Project)"]
    E["/data/site/raw/*/*.json<br>(DICOM Metadata)"] --> A
    A --> F["anonymizeAndSend.py<br>(Transfer Processing)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class E inputFile
    class B,C,D,F outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/data/site/raw/*/*.json<br>(DICOM Series Metadata)"] --> B["populateIncoming.py<br>(Main Processing)"]
    C["REDCap Coupling Lists<br>(Token: 03BAEA...)"] --> B
    D["REDCap Routing Rules<br>(Token: BEE3E9F...)"] --> B
    B --> E["REDCap Incoming Project<br>(Token: 82A0E31C...)"]
    B --> F["Transfer Requests<br>(for anonymizeAndSend)"]
    G["Command Line Args<br>(--importAll)"] --> B
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D,G inputFile
    class B mainScript
    class E,F outputFile

Data patsh

- Input Paths

 * ``/data/site/raw/*/*.json`` 

- Output Paths

 * RedCap endpoint





------


.. include:: populateIncoming.py
   :start-after: """
   :end-before: """
