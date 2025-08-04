createTransferRequestsForProcessed.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script automatically detects processed medical imaging series that need to be forwarded to research PACS systems by identifying series with ``StudyInstanceUIDs`` that contain dots (indicating they're new/processed data). It retrieves transfer requests from REDCap, modifies DICOM metadata to match original study identifiers, and forwards the data either directly to storage or through anonymization processes depending on the project type. The script also extracts structured report data for specific projects like ``Transpara`` studies and ``NOPARK``.

**Related Files**

.. mermaid::

   flowchart LR
    A["createTransferRequestsForProcessed.py"]
    B["/home/processing/bin/extractDataFromTransparaSR.sh"]
    C["/home/processing/bin/extractDataFromDaTQUANT.sh"]
    D["/var/www/html/server/utils/s2m.sh"]
    E["/home/processing/logs/extractDataFromTransparaSR.log"]
    F["/home/processing/logs/extractDataFromDaTQUANT.log"]
    G["/usr/bin/dcmodify"]
    H["/usr/bin/storescu"]
    I["Docker containers (dcmtk)"]
    J["/data/site/raw/*/*.json"]
    K["/data/site/raw/*/series_folders"]

    J --> |JSON metadata| A
    K --> |DICOM series data| A
    A --> |calls for Transpara projects| B
    A --> |calls for NOPARK project| C
    A --> |calls for anonymization| D
    A --> |uses for DICOM modification| G
    A --> |uses for direct PACS storage| H
    A --> |uses for DICOM operations| I
    B --> |processing logs| E
    C --> |extraction logs| F

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,G,H,I,J,K inputFile
    class E,F outputFile

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0


**Data Flow Diagram**

.. mermaid::

   flowchart LR
      A["createTransferRequestsForProcessed.py"]
      B["/home/processing/bin/extractDataFromTransparaSR.sh"]
      C["/home/processing/bin/extractDataFromDaTQUANT.sh"]
      D["/var/www/html/server/utils/s2m.sh"]
      E["/home/processing/logs/extractDataFromTransparaSR.log"]
      F["/home/processing/logs/extractDataFromDaTQUANT.log"]
      G["/usr/bin/dcmodify"]
      H["/usr/bin/storescu"]
      I["Docker containers (dcmtk)"]
      J["/data/site/raw/*/*.json"]
      K["/data/site/raw/*/series_folders"]

      J --> |JSON metadata| A
      K --> |DICOM series data| A
      A --> |calls for Transpara projects| B
      A --> |calls for NOPARK project| C
      A --> |calls for anonymization| D
      A --> |uses for DICOM modification| G
      A --> |uses for direct PACS storage| H
      A --> |uses for DICOM operations| I
      B --> |processing logs| E
      C --> |extraction logs| F

      %% Styling
      classDef inputFile fill:#e1f5fe
      classDef outputFile fill:#f3e5f5
      classDef mainScript fill:#fff3e0
      
      class A mainScript
      class B,C,D,G,H,I,J,K inputFile
      class E,F outputFile

      %% Styling
      classDef inputFile fill:#e1f5fe
      classDef outputFile fill:#f3e5f5
      classDef mainScript fill:#fff3e0


Data paths:

- Input Paths: 
   * ``/data/site/raw/*/``
- Output Paths: 
   * ``Research PACS server``,
   * ``/home/processing/logs/``,
   * ``Temporary directories (created dynamically)``.



.. include:: createTransferRequestsForProcessed.py 
   :start-after: """
   :end-before: """
