populateAutoID.py
~~~~~~~~~~~~~~~~~~

This script automates the creation of transfer requests for medical imaging studies by checking auto-ID enabled projects in REDCap. It retrieves incoming DICOM data, generates or retrieves existing patient IDs using configurable naming patterns, and creates transfer requests for studies that don't already have them. The script interfaces with multiple REDCap databases using different API tokens and calls an external ``gen-id.py`` utility to generate new patient identifiers when needed.


**Related Files**

.. mermaid::

   flowchart TD
    A["populateAutoID.py"] --> B["/home/processing/bin/gen-id/gen-id.py<br>(ID Generator)"]
    C["REDCap Project Database<br>(Auto-ID Config)"] --> A
    D["REDCap Incoming Database<br>(Study Data)"] --> A
    E["REDCap AutoID Database<br>(Generated IDs)"] --> A
    A --> F["REDCap Transfer Database<br>(Transfer Requests)"]
    A --> E
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E inputFile
    class E,F outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["REDCap Projects API"] --> B["populateAutoID.py"]
    C["REDCap Incoming API<br>(Study data from last 14 days)"] --> B
    D["REDCap AutoID API<br>(Existing patient IDs)"] --> B
    B --> E["gen-id.py<br>(Generate new patient ID)"]
    E --> B
    B --> F["REDCap AutoID API<br>(Store new patient ID)"]
    B --> G["REDCap Transfer API<br>(Create transfer request)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B,E mainScript
    class F,G outputFile



Data path


- Input Sources:

 * ``/home/processing/bin/gen-id/gen-id.py``

- Output Destinations:

 * Temporary files (created and cleaned up automatically)





-----

.. include:: populateAutoID.py
   :start-after: """
   :end-before: """
