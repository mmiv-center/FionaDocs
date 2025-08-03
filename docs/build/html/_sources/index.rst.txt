FIONA Documentation
===================

**FIONA** is a comprehensive medical imaging data management and processing platform designed for healthcare research environments. The system handles DICOM medical imaging data throughout its entire lifecycle - from initial acquisition at imaging scanners to final anonymized export for research purposes. Provides DICOM anonymization, quarantine management, and automated transfer from clinical to research PACS systems while ensuring General Data Protection Regulation (GDPR) compliance. 

**The architecture** of the Fiona system can be divided into five layers: network layer, processing layer, storage layer, transfer layer and management layer.

.. mermaid::    
    
    flowchart TD
        subgraph network [" <b>Network Layer</b> "]
            PACS[📡 Clinical PACS<br/>DICOM File Source]
            StoreSCP[📥 storescpFIONA<br/>DICOM SCP]
        end
        
        subgraph processing [" <b>Processing Layer</b> "]
            ProcessFile[🔄 processSingleFile3.py<br/>DICOM Processing]
            DetectStudy[🔍 detectStudyArrival.sh<br/>Study Detection]
            Classification[⚙️ Classification<br/>Rule Engine]
            NamedPipe((Named Pipe))
        end
        
        subgraph storage [" <b>Storage Layer</b> "]
            FileSystem[💾 File System<br/>/data/site/]
            SymLinks[🔗 Symbolic Links<br/>Study/Series]
        end
        
        subgraph transfer [" <b>Transfer Layer</b> "]
            Anonymize[🔒 anonymizeAndSend.py<br/>Anonymization]
            SendFiles[📤 sendFiles.sh<br/>SFTP Transfer]
            ResPACS[🏥 Research PACS<br/>Destination]
            REDCap[(🗄️ REDCap)]
        end
        
        subgraph mgmt [" <b>Management Layer</b> "]
            Management[⚙️ System Management<br/>heartbeat.sh, cron.sh, monitoring]
        end
        
        %% Data Flow
        PACS -->|DICOM| StoreSCP
        StoreSCP -->|DICOM Files| ProcessFile
        ProcessFile -->|metadata| NamedPipe
        NamedPipe -->|trigger| DetectStudy
        DetectStudy -->|study info| Classification
        Classification -->|classification| SymLinks
        FileSystem -->|files| SymLinks
        SymLinks -->|study data| Anonymize
        Anonymize -->|anonymized| SendFiles
        SendFiles -->|SFTP| ResPACS
        REDCap -->|consent| Anonymize
        
        %% Management connections
        Management -.->|monitor| StoreSCP
        Management -.->|monitor| ProcessFile
        Management -.->|monitor| FileSystem
        
        %% Styling
        classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
        classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
        classDef storage fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
        classDef transfer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
        classDef mgmt fill:#ffebee,stroke:#d32f2f,stroke-width:2px
        classDef pipe fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
        
        class PACS,StoreSCP network
        class ProcessFile,DetectStudy,Classification process
        class FileSystem,SymLinks storage
        class Anonymize,SendFiles,ResPACS,REDCap transfer
        class Management mgmt
        class NamedPipe pipe


- **Network Layer**: DICOM communication services that receive imaging data from scanners and send to research PACS using standard medical imaging protocols.
- **Processing Layer**: Core data processing engines that extract metadata, perform anonymization, and execute containerized analysis workflows on medical imaging studies.
- **Storage Layer**: Organized file system architecture with symbolic links, structured directories, and automated lifecycle management for imaging data and metadata.
- **Transfer Layer**: Secure data distribution system that creates anonymized exports, manages transfer requests, and delivers data to external research repositories.
- **Management Layer**: Administrative services including health monitoring, configuration management, audit logging, and automated maintenance operations.

The system operates as a distributed service with daemon processes, cron jobs, and web applications
working together to provide automated medical imaging research data management.


.. EndUser
.. -------

.. toctree::
   :maxdepth: 1
   :hidden:
   
   EndUser/index



.. Server Admin
.. ------------

.. toctree::
   :maxdepth: 1
   :hidden:

   ServerAdmin/index
  



.. Architecture
.. -------------

.. toctree::
   :maxdepth: 1
   :hidden:
   
   Architecture/index
   

.. Possible updates (temporary)
.. -----------------------------

.. toctree::
   :maxdepth: 1
   :caption: Possible updates (tmp)
   :hidden:
   
..   Temp/index

   
Contact Information
-------------------

* Website: https://fiona.ihelse.net
* Location: Haukeland University Hospital, Bergen, Norway

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
