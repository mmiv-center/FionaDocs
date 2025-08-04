clearOldFiles.sh
~~~~~~~~~~~~~~~~~

This bash script automatically manages disk space by deleting oldest archive directories when partition usage exceeds 80%. It monitors the ``/data/`` partition and systematically removes directories from ``/data/site/archive/`` in chronological order (oldest first) until free space reaches at least 20%. The script also removes corresponding directories in ``/data/site/raw/`` based on extracted UIDs from archive directory names.


**Related Files**

.. mermaid::

   flowchart TD
    A["/data/site/archive/<br>Archive directories sorted by age"]:::inputFile
    B["clearOldFiles.sh<br>Main cleanup script"]:::mainScript
    C["/data/site/raw/<br>Raw data directories<br>corresponding to archives"]:::inputFile
    
    A --> B
    C --> B
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/data partition<br>Disk usage monitoring"]:::inputFile
    B["clearOldFiles.sh<br>Space management logic"]:::mainScript
    C["/data/site/archive/<br>Oldest directories deleted"]:::outputFile
    D["/data/site/raw/<br>Corresponding directories deleted"]:::outputFile
    
    A --> B
    B --> C
    B --> D
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0



Data paths

- Input folder:
   * ``/data/site/archive/``,
   * ``/data/site/raw/``,
   * ``/data/``
- Output folder: No output directories, delete only.



.. include:: clearOldFiles.sh
   :start-after: : ' 
   :end-before: ' #end-doc
