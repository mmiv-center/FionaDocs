populateProjects.py
~~~~~~~~~~~~~~~~~~~~

This Python script populates REDCap projects with imaging study information by retrieving transferred studies from incoming transfers and creating corresponding entries in target projects. The script fetches transfer data from a central REDCap database, matches it with project tokens, and creates participant records with associated imaging instrument data for each study that has been forwarded to PACS. It processes transfers either for all active projects or a specific project when the --project parameter is provided, ensuring each study appears in its own REDCap project with proper repeat instance management.


**Related Files**

.. mermaid::

   flowchart TD
    B["imagingProjects.json<br>(Configuration File)"] --> A["populateProjects.py"]
    C["REDCap API<br>(localhost:4444/api/)"] --> A
    D["DataTransferProjects<br>(REDCap Project)"] --> A
    E["Incoming Transfers<br>(REDCap Project)"] --> A
    A --> F["Target Projects<br>(REDCap Projects)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E inputFile
    class F outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/home/processing/bin/<br>imagingProjects.json"] --> B["populateProjects.py"]
    C["DataTransferProjects"] --> B
    D["Incoming Transfers<br>"] --> B
    B --> E["Target REDCap<br>Projects"]
    B --> F["REDCap API<br>Server"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B mainScript
    class E,F outputFile

Data paths

- Input Paths:

 * ``/home/processing/bin/imagingProjects.json``

- Output Destinations:

 * Multiple REDCap projects (determined dynamically from DataTransferProjects)


 -------


.. include:: populateProjects.py
   :start-after: """
   :end-before: """
