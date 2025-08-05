process_tiff.sh 
~~~~~~~~~~~~~~~~

The ``process_tiff.sh`` script processes pathology image files (SVS and NDPI formats) by extracting metadata, anonymizing the images, and either importing them directly to a PACS system or storing them in a designated project folder. It handles two workflow paths: path-based imports where files are pseudonymized and stored locally, and DICOM conversion where files are converted to DICOM format, anonymized, and sent to a research PACS. The script processes JSON metadata files from REDCap uploads, extracts scanner information, and updates the database with processing results.




**Related Files**

.. mermaid::

   flowchart LR
    A["process_tiff.sh"] --> B["wsi_anon<br>(Docker Container)"]
    A --> C["process_tiff_importREDCap.py"]
    A --> D["updatePathologyREDCap.py"]
    A --> E["dicom_wsi<br>(Docker Container)"]
    A --> F["anonymize<br>(Tool)"]
    A --> G["storescu<br>(DICOM Tool)"]
    H["storescu.cfg"] --> G
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class H inputFile
    class B,C,D,E,F,G outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart LR
    A["/var/www/html/applications/Attach/uploads<br>(JSON files)"] --> B["process_tiff.sh"]
    C["/var/www/html/applications/Attach/uploads<br>(SVS/NDPI files)"] --> B
    
    B --> D["/var/www/html/applications/Attach/uploads_done<br>(Processed JSON files)"]
    B --> E["Project Import Folder<br>(Anonymized WSI files)"]
    B --> F["Research PACS<br>(DICOM files)"]
    B --> G["/export2/Attach/project_cache/<br>(Project backup copies)"]
    
    H["REDCap Database<br>(Metadata updates)"] <--> B
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C inputFile
    class B mainScript
    class D,E,F,G,H outputFile




Data pats

- Input Paths:

   * ``/var/www/html/applications/Attach/uploads`` - Source JSON and image files
   * ``/var/www/html/applications/Attach/storescu.cfg`` - DICOM configuration file

- Output Paths:

   * ``/var/www/html/applications/Attach/uploads_done`` - Processed JSON files Project-specific import folders (defined in JSON: project_pat_import_folder)
   * ``/export2/Attach/project_cache/{InstitutionName}/`` - Optional project backup cache Research PACS server - DICOM storage destination

- Temporary Paths:

   * ``/tmp/`` - Temporary processing files Dynamically created temp directories for DICOM conversion and anonymization





------

.. include:: process_tiff.sh 
   :start-after: : '
   :end-before: ' #end-doc
