createTransferRequests.py
~~~~~~~~~~~~~~~~~~~~~~~~~~

This Python script retrieves medical imaging transfer records from a REDCap database via API and creates JSON transfer request files for studies that need to be transferred. It checks for new image series by comparing transfer dates with file modification times in the raw data directory. The script only creates transfer requests for records that have complete information (project name, transfer name) and haven't been processed yet.


**Related Files**

.. mermaid::

   flowchart TD
    A["createTransferRequests.py"]
    B["REDCap API"]
    C["/data/site/raw/{study_uid}/*.json"]
    D["/home/processing/transfer_requests/<br>generated transfer requests as JSON files"]
    
    B --> |DICOM data| A
    C --> |Raw image series| A
    A --> D
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C inputFile
    class D outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
      A["REDCap"]
      B["createTransferRequests.py"]
      C["/data/site/raw/{study_uid}/*.json"]
      D["/home/processing/transfer_requests/<br>{study_uid}_{project}_{name}_{instance}.json"]
      
      A -->|API call| B
      C -->|File timestamp check| B
      B -->|Creates JSON files| D
      
      %% Styling
      classDef inputFile fill:#e1f5fe
      classDef outputFile fill:#f3e5f5
      classDef mainScript fill:#fff3e0
      
      class A,C inputFile
      class B mainScript
      class D outputFile


Data paths

- Input directories:
   *  ``/data/site/raw/{study_instance_uid}/``
- Output directories:
   * ``/home/processing/transfer_requests/``

-------

.. include:: createTransferRequests.py
   :start-after: """
   :end-before: """
