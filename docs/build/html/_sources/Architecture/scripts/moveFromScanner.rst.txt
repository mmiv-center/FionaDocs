moveFromScanner.sh
~~~~~~~~~~~~~~~~~~~

This script is a DICOM scanner integration tool that automatically retrieves medical imaging data from a scanner via DICOM C-MOVE operations. It monitors active scan requests, checks for incomplete series, and pulls missing images using ``DCMTK`` tools (``findscu``, ``movescu``). The script runs every 15 seconds via cron job and moves completed studies to finished-scans directory when all images are received and the procedure is complete.

**Related Files**

.. mermaid::

   flowchart TD
    B["/data/config/config.json"] --> A["moveFromScanner.sh"]
    C["/usr/share/dcmtk/dicom.dic"] --> A
    D["/usr/bin/findscu<br>(DCMTK Tool)"] --> A
    E["/usr/bin/movescu<br>(DCMTK Tool)"] --> A
    F["/usr/bin/dump2dcm<br>(DCMTK Tool)"] --> A
    G["/usr/bin/dcmdump<br>(DCMTK Tool)"] --> A
    A --> H["${SERVERDIR}/.pids/<br>moveFromScanner.lock<br>(Lock File)"]
    A --> I["${SERVERDIR}/logs/<br>moveFromScanner.log<br>(Log File)"]

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E,F,G inputFile
    class H,I outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["${DATADIR}/active-scans/<br>(Study Requests)"] --> B["moveFromScanner.sh"]
    C["${DATADIR}/scanner/<br>(MPPS Files)"] --> B
    D["Scanner<br>(DICOM Server)"] --> B
    B --> E["${DATADIR}/site/raw/<br>${studyInstanceUID}/<br>${seriesInstanceUID}/<br>(DICOM Images)"]
    B --> F["${DATADIR}/finished-scans/<br>(Completed Studies)"]
    B --> G["${DATADIR}/failed-scans/<br>(Failed Studies)"]
    B --> H["${SERVERDIR}/logs/<br>moveFromScanner.log<br>(Processing Log)"]

    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D inputFile
    class B mainScript
    class E,F,G,H outputFile



Data Paths

- Input Directories:
* ``${DATADIR}/active-scans/``
* ``${DATADIR}/scanner/`` 
* ``${DATADIR}/config/enabled`` 
* ``/data/config/config.json`` 
- Output Directories:
* ``${DATADIR}/site/raw/${studyInstanceUID}/${seriesInstanceUID}/`` -
* ``${DATADIR}/finished-scans/`` 
* ``${DATADIR}/failed-scans/``
* ``${SERVERDIR}/logs/moveFromScanner.log`` 
* ``${SERVERDIR}/.pids/moveFromScanner.lock`` 
- Configuration Variables:
* ``DATADIR``
* ``SCANNERIP``, ``SCANNERPORT``
* ``SCANNERAETITLE``, ``DICOMAETITLE``







--------------

.. include:: moveFromScanner.sh 
   :start-after: : '
   :end-before: ' #end-doc
