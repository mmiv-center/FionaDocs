heartbeat.sh
~~~~~~~~~~~~~

``heartbeat.sh`` is a monitoring script that performs health checks on DICOM ``storescp`` services by testing connectivity with ``echoscu``. If the connection test fails, it terminates unresponsive storescp processes and cleans up stuck ``detectStudyArrival.sh`` jobs that have been running for over an hour. The script is designed to run via cron every minute and relies on external process managers like monit to restart killed services automatically.


**Related Files**

.. mermaid::

   flowchart TD
    A["heartbeat.sh"] --> B["/data/config/config.json)"]
    A --> C["/usr/bin/echoscu<br>(DICOM Echo Utility)"]
    A --> D["storectl.sh"]
    A --> E["detectStudyArrival"]
    
    B --> F["DICOMIP &<br>DICOMPORT Values"]
    C --> G["Connection Test<br>to DICOM Server"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E inputFile
    class F,G outputFile


**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["/data/config/config.json"] --> B["heartbeat.sh"]
    C["storescp log files<br>/logs/storescpd*.log"] --> B
    
    B --> D["echoscu command<br>to DICOM server"]
    B --> E["/logs/heartbeat*.log"]
    
    F["Process list<br>(pgrep commands)"] --> B
    B --> G["storescp &<br>detectStudyArrival<br>processes"]
    
    B --> H["storectl.sh stop"]
    B --> I["/var/www/html/server/.pids/<br>detectStudyArrival*.lock"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class B mainScript
    class A,C,F inputFile
    class D,E,G,H,I outputFile



Data paths:

- Input Folders/Files:
   * ``/data/config/config.json``
   * ``/var/www/html/server/logs/storescpd*.log``

- Output Folders/Files:
   * ``/var/www/html/server/logs/heartbeat*.log`` 
   * ``/var/www/html/server/.pids/detectStudyArrival*.lock`` 




-----

.. include:: heartbeat.sh 
   :start-after: : '
   :end-before: ' #end-doc
