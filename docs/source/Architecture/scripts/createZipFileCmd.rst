createZipFileCmd.php
~~~~~~~~~~~~~~~~~~~~~~

This PHP script is a command-line cron job that processes medical imaging export requests by creating ZIP archives of DICOM studies. It pulls DICOM data from an imaging server, applies anonymization transformations based on project-specific rules, optionally converts to NIFTI format, and packages the results into downloadable ZIP files. The script handles secure email delivery with password protection and supports export to TSD (Norwegian research data storage).


**Related Files**

.. mermaid::

   flowchart TD
    A["createZipFileCmd.php"]
    B["constants.php"]
    C["/var/www/html/php/AC.php"]
    D["/data/config/config.json"]
    E["prepared_downloads_list.jobs"]
    F["tokens.json"]
    G["execMeasurements.json"]
    H["pullStudyFromIDS7.sh"]
    I["mapping.json"]
    J["mapping2.json"]
    
    B --> A
    C --> A
    D --> A
    E --> A
    F --> A
    A --> G
    A --> H
    H --> I
    H --> J
    I --> A
    J --> A
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E,F,H,I,J inputFile
    class G outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["Job List<br>prepared_downloads_list.jobs"]
    B["createZipFileCmd.php"]
    C["REDCap API<br>Patient Data"]
    D["IDS7 Imaging Server<br>DICOM Studies"]
    E["Temp Directory<br>/export2/Export/tmp_*"]
    F["ZIP Archive<br>/export2/Export/files/"]
    G["MD5 Checksum<br>*.md5"]
    H["TSD Upload<br>(optional)"]
    I["Email Notification<br>(optional)"]
    J["Log Files<br>/home/processing/logs/"]
    
    A -->|"Read job queue"| B
    C -->|"Patient metadata"| B
    D -->|"DICOM images"| B
    B -->|"Create temp files"| E
    B -->|"Anonymize & package"| F
    B -->|"Generate checksum"| G
    B -->|"Upload to TSD"| H
    B -->|"Send secure link"| I
    B -->|"Log activities"| J
    E -->|"Clean up"| B
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B mainScript
    class F,G,H,I,J outputFile
    class E inputFile


Data pahts

- Input paths: 
   * ``/var/www/html/applications/Exports/php/prepared_downloads_list.jobs``, 
   * ``/data/config/config.json``,
   * ``/var/www/html/applications/Exports/php/tokens.json``
- Output paths:
   * ``/export2/Export/``,
   * ``/export2/Export/files/``,
   * ``/home/processing/logs/``,
   * ``/var/www/html/applications/Exports/php/execMeasurements.json`` 


.. include:: createZipFileCmd.php
   :start-after: /*** 
   :end-before: ***/
