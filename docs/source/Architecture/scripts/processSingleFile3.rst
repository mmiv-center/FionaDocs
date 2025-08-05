processSingleFile3.py
~~~~~~~~~~~~~~~~~~~~~~

ProcessSingleFile3.py is a daemon process that monitors a named pipe for DICOM file processing requests and creates organized directory structures with symbolic links. The daemon reads DICOM files, extracts header information including Siemens CSA headers, and organizes them into Study/Series hierarchies while generating JSON metadata files. It supports classification rules for automatic categorization of medical imaging data and handles structured reports separately from regular imaging data.


**Related Files**

.. mermaid::

   flowchart TD
    B["classifyRules.json<br>(Classification Rules)"] --> A["processSingleFile3.py"]
    C["/tmp/.processSingleFilePipe<br>(Named Pipe)"] --> A
    F["/data/config/config.json"] --> A
    A --> D["../logs/processSingleFile*.log"]
    A --> E["../.pids/processSingleFile*.pid"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,F inputFile
    class D,E outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["DICOM Files"] --> B["processSingleFile3.py"]
    C["Named Pipe<br>(/tmp/.processSingleFilePipe)"] --> B
    D["classifyRules.json<br>(Rules File)"] --> B
    E["/data/config/config.json<br>(Config File)"] --> B
    
    B --> F["/data/site/raw/<br>StudyUID/SeriesUID/<br>(Symbolic Links)"]
    B --> G["/data/site/participants/<br>PatientID/StudyDate_Time/<br>(Patient Structure)"]
    B --> H["/data/site/srs/<br>Manufacturer/StudyUID/<br>(Structured Reports)"]
    B --> I["/data/site/.arrived/<br>(Touch Files)"]
    B --> J["Series JSON Files<br>(.json metadata)"]
    B --> K["Log Files<br>(../logs/)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D,E inputFile
    class B mainScript
    class F,G,H,I,J,K outputFile


Data pahts

- Input Paths:
 
  * ``/data/config/config.json`` - Configuration file containing project settings classifyRules.json - Classification rules file (same directory as script)
  * ``/tmp/.processSingleFilePipe[projname]`` - Named pipe for receiving file processing requests
  * Source DICOM files (paths received via named pipe)


- Output Paths:

  * ``/data/site/raw/[StudyUID]/[SeriesUID]/`` - Organized DICOM structure with symbolic links
  * ``/data/site/participants/[PatientID]/[StudyDate_StudyTime]/`` - Patient-oriented  directory structure
  * ``/data/site/srs/[Manufacturer]/[StudyUID]/`` - Structured reports directory
  * ``/data/site/.arrived/`` - Touch files for series arrival detection
  * ``/data/site/temp/`` - Temporary directory for atomic JSON file operations
  * ``../logs/processSingleFile[projname].log`` - Log files
  * ``../.pids/processSingleFile[projname].pid`` - Process ID files
  * Series JSON metadata files (.json files alongside DICOM directories)

--------

.. include:: processSingleFile3.py
   :start-after: """
   :end-before: """
