sendFiles.sh 
~~~~~~~~~~~~

This bash script automates the secure transfer of compressed DICOM and k-space data files from a local outbox directory to a remote DAIC (Data Analysis and Informatics Center) server using SFTP. The script compares local and remote MD5 checksums to avoid redundant transfers and implements file locking to prevent concurrent executions. It includes error handling for corrupt checksums, symbolic link conflicts, and disk space issues, with comprehensive logging of all operations.

**Related Files**

.. mermaid::

   flowchart LR
    A["/data/config/config.json"] --> B["sendFiles.sh"]
    B --> C["/var/www/html/server/logs/<br>sendFiles.log"]
    B --> D["/var/www/html/server/bin/<br>CommandScript"]
    B --> E["/var/www/html/server/bin/<br>CommandScriptMD5s"]
    B --> F["/var/www/html/server/.pids/<br>sendFiles.lock"]
    G["crontab<br>(Scheduler)"] --> B
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,G inputFile
    class C,D,E,F outputFile
    class B mainScript



**Data Flow Diagram**

.. mermaid::

   flowchart LR
    A["/data/outbox/<br>*.tgz files"] --> B["sendFiles.sh"]
    C["/data/outbox/<br>*.md5sum files"] --> B
    B --> D["SFTP Transfer<br>to DAIC Server"]
    D --> E["Remote DAIC Server<br>/data/outbox/"]
    B --> F["/data/DAIC/<br>(Permanent Storage)"]
    G["Remote MD5 Cache<br>md5server_cache.tar"] --> B
    B --> H["/var/www/html/server/logs/<br>sendFiles.log"]
    B --> I["Shadow Copy Files<br>*.tgz shadow_copy"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,G inputFile
    class E,F,H,I outputFile
    class B mainScript


Data Paths

- Input Directories:

   * ``/data/outbox/``
   * ``/data/config/config.json``

- Output Directories:

   * ``/data/DAIC/`` 
   * ``/var/www/html/server/logs/``
   * ``/var/www/html/server/.pids/``
   * Remote DAIC server endpoint (specified in config.json)

- Temporary Directories:

   * ``/tmp/md5sums_server_XXXX``






------


.. include:: sendFiles.sh 
   :start-after: : '
   :end-before: ' #end-doc
