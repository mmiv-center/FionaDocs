mppsctl.sh 
~~~~~~~~~~~

This bash script manages a DICOM Multiple Performed Procedure Steps (MPPS) server daemon. It starts the ``ppsscpfs_e`` daemon to track medical scans on the server, with configurable port settings and service enable/disable functionality. The script supports start/stop operations and includes logging capabilities for monitoring the MPPS service status. It's designed to run as a cron job every minute to ensure the service remains active.


**Related Files**

.. mermaid::

   flowchart LR
    A["mppsctl.sh"] --> B["config.json<br>(/data/config/)"]
    A --> C["enabled<br>(/data/config/)"]
    A --> D["dicom.dic<br>(/usr/share/dcmtk/)"]
    A --> E["dcmpps.lic<br>(/usr/share/dcmtk/)"]
    F["ppsscpfs_e<br>(DICOM daemon)"]
    A --> G["mpps.pid<br>(PID file)"]
    A --> H["ppsscpfs.log<br>(Log file)"]
    
    B -->|"reads port config"| A
    C -->|"checks if service enabled"| A
    D -->|"DICOM dictionary"| F
    E -->|"license file"| F
    A -->|"starts/stops"| F
    A -->|"creates/removes"| G
    A -->|"writes logs to"| H

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E,F inputFile
    class G,H outputFile




**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["Configuration Data<br>(/data/config/)"] --> B["mppsctl.sh"]
    C["DICOM Dictionary<br>(/usr/share/dcmtk/)"] --> B
    B --> D["ppsscpfs_e<br>(MPPS Daemon)"]
    D --> E["Scanner Output<br>(/data/scanner/)"]
    B --> F["PID File<br>(.pids/mpps.pid)"]
    B --> G["Log File<br>(logs/ppsscpfs.log)"]
    H["DICOM Clients"] <--> D
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class B mainScript
    class A,C,D,H inputFile
    class E,F,G outputFile



Data pahts

- Input Directories/Files:

* ``/data/config/config.json``
* ``/data/config/enabled``
* ``/usr/share/dcmtk/dicom.dic`` 
* ``/usr/share/dcmtk/dcmpps.lic`` 

- Output Directories/Files:

* ``/data/scanner/``
* ``${SERVERDIR}/.pids/mpps.pid`` 
* ``${SERVERDIR}/logs/ppsscpfs.log`` 

- Working Directory:

* ``${SERVERDIR}`` 



-------

.. include:: mppsctl.sh 
   :start-after: : '
   :end-before: ' #end-doc
