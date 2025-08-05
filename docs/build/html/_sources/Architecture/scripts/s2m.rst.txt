s2m.sh 
~~~~~~~~~~~~
The ``s2m.sh`` script is a DICOM file transmission utility that sends DICOM directories to a local DICOM node using the dcmtk docker container. It supports sending individual directories, all studies for a specific ``PatientID``, or all studies from the last N days. The script reads DICOM network configuration from ``/data/config/config.json`` and can handle project-specific routing. It includes fallback mechanisms using direct storescu commands if Docker-based transmission fails.


**Related Files**

.. mermaid::

   flowchart LR
    A["s2m.share"] --> B["/data/config/config.json"]
    A --> C["dcmtk<br>(Docker Container)"]
    A --> D["/usr/bin/storescu<br>(DICOM command)"]
    A --> E["/data/site/raw/*/*.json<br>(Metadata Files)"]
    A --> F["/data/site/archive/<br>(DICOM Directories)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E,F inputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/data/site/archive/<br>(DICOM Source)"] --> B["s2m.sh"]
    C["/data/config/config.json<br>(Network Config)"] --> B
    D["/data/site/raw/*/*.json<br>(Patient Metadata)"] --> B
    B --> E["DICOM Node<br>(Remote Destination)"]
    B --> F["/usr/share/dcmtk/dicom.dic<br>(Dictionary File)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D,F inputFile
    class E outputFile
    class B mainScript


Data paths

- Input Paths:

   * ``/data/config/config.json``
   * ``/data/site/archive/``
   * ``/data/site/raw/*/*.json``
   * ``/usr/share/dcmtk/dicom.dic``

- Output Paths:

   * Remote destination for DICOM files, no local output files.






------


.. include:: s2m.sh 
   :start-after: : '
   :end-before: ' #end-doc
