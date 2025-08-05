resendProject.py
~~~~~~~~~~~~~~~~~

This Python script manages medical imaging transfer requests by checking REDCap database records for studies where the transfer date occurred before the request date. It retrieves transfer requests from a REDCap API, filters them based on date logic to identify studies that need to be resent, and generates JSON transfer request files for reprocessing. The script supports filtering by specific project names and creates uniquely named JSON files in a designated transfer requests directory.

**Related Files**

.. mermaid::

   flowchart TD
    A["resendProject.py"] --> B["*.json files<br>(Transfer Requests)"]
    C["REDCap Database"] -->|"API calls"| A
    A --> D["/home/processing/<br>transfer_requests/"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B outputFile
    class C inputFile
    class D outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["Command Line Args"] --> B["resendProject.py"]
    C["REDCap API<br>(Transfer Records)"] --> B
    B --> D["Filtered Transfer<br>Requests"]
    D --> E["Individual JSON Files<br>(study_instance_uid_<br>project_name_<br>transfer_name_<br>repeat_instance.json)"]
    B --> F["REDCap Database<br>(Record Updates)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A inputFile
    class B mainScript
    class C inputFile
    class D mainScript
    class E outputFile
    class F outputFile


Data paths

- Input Paths:

   * REDCap database

- Output Paths:

   * ```/home/processing/transfer_requests/``
   * ``{study_instance_uid}_{transfer_project_name}_{transfer_name}_{redcap_repeat_instance}.json``




------

.. include:: resendProject.py
   :start-after: """
   :end-before: """
