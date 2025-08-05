removeOldEntries.sh 
~~~~~~~~~~~~~~~~~~~~

This bash script removes old entries from the ``incoming.txt`` file based on timestamp comparison. It reads each line from the file, extracts the first field as a timestamp, and keeps only entries that are newer than 7 days (604800 seconds). The script uses a temporary file for atomic file operations and provides detailed logging of the cleanup process.

**Related Files**

.. mermaid::

   flowchart TD
    A["removeOldEntries.sh"] --> B["incoming.txt<br>(/var/www/html/applications/Assign/)"]
    A --> C["Temporary File<br>(/tmp/.tfile)"]
    C --> B
    D["System Date Command<br>(date)"] --> A
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B outputFile
    class C,D inputFile



**Data Flow Diagram**


.. mermaid::

   flowchart TD
    A["incoming.txt<br>(/var/www/html/applications/Assign/)"] --> B["removeOldEntries.sh<br>Timestamp Filtering"]
    C["System Timestamp<br>(current date)"] --> B
    B --> D["Temporary File<br>(/tmp/.tfile)<br>Filtered Data"]
    D --> E["incoming.txt<br>(/var/www/html/applications/Assign/)<br>Updated Output"]
    B --> F["Console Logs<br>Process Information"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C inputFile
    class B mainScript
    class D,E,F outputFile


Data paths

- Input/Output Directories:

   * ``/var/www/html/applications/Assign/incoming.txt``
   * ``/tmp/.tfile``



-------------------

.. include:: removeOldEntries.sh 
   :start-after: : '
   :end-before: ' #end-doc
