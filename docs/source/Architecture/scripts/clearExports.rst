clearExports.sh
~~~~~~~~~~~~~~~~

This bash script manages disk space by automatically deleting old export files when disk usage exceeds 80%. It first removes temporary directories older than 1000 minutes, then systematically deletes the oldest ZIP files in ``/export2/Export/files/`` until disk usage drops to 80% or below. The script provides timestamped logging throughout the cleanup process to track which files are being removed.

**Related File**

.. mermaid::

   flowchart TD
       A["clearExports.sh main script"] --> B["/export2/Export/<br>root directory"]
       A --> C["/export2/Export/files/<br>zip directory"]
       B --> D["tmp_* temporary directories"]
       C --> E["*.zip export archive files"]
       
       classDef inputFile fill:#e1f5fe
       classDef outputFile fill:#f3e5f5
       classDef mainScript fill:#fff3e0
       
       class A mainScript
       class B,C,D,E inputFile

**Data Flow Diagram**


.. mermaid::

   flowchart TD
      A["/export2/Export/tmp_* directories"] --> B["clearExports.sh"]
      C["/export2/Export/files/*.zip files"] --> B
      B --> E["deleted tmp directories"]
      B --> F["deleted zip files"]
      B --> G["console output with timestamps"]
      
      classDef inputFile fill:#e1f5fe
      classDef outputFile fill:#f3e5f5
      classDef mainScript fill:#fff3e0
      
      class B mainScript
      class A,C inputFile
      class E,F,G outputFile

   

Data paths

- Input directories:
   * ``/export2/Export/``,
   * ``/export2/Export/files/``     
- Output directories:
   * Files are deleted (no output directories)





.. include:: clearExports.sh
   :start-after: : ' 
   :end-before: ' #end-doc
