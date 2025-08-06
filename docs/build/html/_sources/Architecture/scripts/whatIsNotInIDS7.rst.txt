whatIsNotInIDS7.py
~~~~~~~~~~~~~~~~~~~

This script cleans up a REDCap database by removing records that no longer exist in the research PACS system. It queries the REDCap project "whatIsInIDS7" to retrieve all stored records, then validates each record's existence in the research PACS using DICOM findscu commands. Records that are not found in the PACS (indicated by zero SeriesInstanceUID occurrences) are marked for deletion and optionally removed from REDCap in batches of 200.



**Related Files**

.. mermaid::

   flowchart TD
    A["whatIsNotInIDS7.py"] --> B["findscu<br>(External DICOM Tool)"]
    B --> C["Research PACS Server"]
    A --> D["REDCap API"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D inputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["REDCap Database"] --> B["whatIsNotInIDS7.py"]
    B --> C["Research PACS"]
    C --> B
    B --> A
   
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A inputFile
    class B mainScript
    class C inputFile



Data Paths


- Input Source:

   * ``REDCap`` API

- Output Destination: 

   * ``REDCap`` API








-------


.. include:: whatIsNotInIDS7.py
   :start-after: """
   :end-before: """
