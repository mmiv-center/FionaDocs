clearStaleLinks.sh
~~~~~~~~~~~~~~~~~~~

This bash script performs maintenance on image archive directories by cleaning up broken symbolic links and empty folders. It processes three specific directories (``/data/site/raw/``, ``/data/site/participants/``, ``/data/site/srs/``) to remove stale symbolic links that no longer point to valid files, delete empty directories, and clean up orphaned JSON metadata files. The script ensures data integrity by maintaining a clean directory structure in the archive system.

**Related Files**

.. mermaid::

   flowchart TD
    A[clearStaleLinks.sh] --> B["/data/site/raw/<br>Raw image archive directory"]
    A --> C["/data/site/participants/<br>Participants data directory"] 
    A --> D["/data/site/srs/<br>SRS data directory"]
    A --> E["*.json files<br>Metadata files for directories"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E inputFile

**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["Broken symbolic links<br>in target directories"] --> B[clearStaleLinks.sh]
    C["Empty directories<br>in target directories"] --> B
    D["Orphaned *.json files<br>without corresponding directories"] --> B
    
    B --> E["Cleaned directory structure<br>Removed stale links"]
    B --> F["Deleted empty directories<br>Maintained directory hierarchy"]
    B --> G["Removed orphaned JSON files<br>Clean metadata state"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B mainScript
    class E,F,G outputFile


Data paths

- Input/Processing Directories:
   * ``/data/site/raw/``,
   * ``/data/site/participants/``,
   * ``/data/site/srs/``
- Output: The same directories (cleaned and maintained)


.. include:: clearStaleLinks.sh
   :start-after: : ' 
   :end-before: ' #end-doc
