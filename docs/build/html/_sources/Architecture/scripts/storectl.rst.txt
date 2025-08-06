storectl.sh
~~~~~~~~~~~~

This script manages a DICOM storage service (``storescp`` daemon) that receives medical imaging data on a specified port. It starts or stops the ``storescpFIONA`` service for the  ``processing`` user, which listens for incoming DICOM files and moves them to project-specific directories. The service can be controlled via an enabled/disabled flag file and supports multiple projects with different configurations (ABCD as default).


**Related Files**

.. mermaid::

   flowchart TD
    A["storectl.sh"]:::mainScript
    B["/data/config/config.json"]:::inputFile
    C["/data/config/enabled"]:::inputFile
    D["/usr/share/dcmtk/dicom.dic"]:::inputFile
    E["receiveSingleFile.sh"]:::outputFile
    F["storescpFIONA"]:::outputFile
    G["/tmp/.processSingleFilePipe<br>(Named Pipe)"]:::outputFile
    H["logs/storescpd.log"]:::outputFile
    I[".pids/storescpd.pid"]:::outputFile
    
    B --> A
    C --> A
    D --> A
    A --> F
    A --> E
    A --> G
    A --> H
    A --> I
    F --> G

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class B,C,D inputFile
    class E,F,G,H,I outputFile
    class A mainScript


**Data Flow Diagram**

.. mermaid::


   flowchart TD
    A["DICOM Client"]:::inputFile
    B["storectl.sh"]:::mainScript
    C["storescpFIONA"]:::mainScript
    D["Named Pipe<br>(/tmp/.processSingleFilePipe)"]:::outputFile
    E["Archive Directory<br>(/data/site/archive)"]:::outputFile
    F["Arrived Directory<br>(/data/site/.arrived)"]:::outputFile
    G["processSingleFile.py"]:::outputFile
    
    A --> |"DICOM data"| C
    B --> |"start/stop"| C
    C --> |"received<br>files"| E
    C --> |"file events"| D
    C --> |"metadata"| F
    D --> |"file paths"| G

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A inputFile
    class D,E,F,G outputFile
    class B,C mainScript


Data Paths


- Input paths:

   * ``/data/config/``
   * ``/usr/share/dcmtk/``
   * ``/var/www/html/server/``

- Output paths (data saved to):

   * ``/data/site/archive/`` 
   * ``/data/site/.arrived/``
   * ``/var/www/html/server/logs/`` 
   * ``/var/www/html/server/.pids/`` 
   * ``/tmp/`` 






---------------------------------

.. include:: storectl.sh 
   :start-after: : '
   :end-before: ' #end-doc
