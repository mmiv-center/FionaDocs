FIONA Documentation
===================

FIONA (Flash-based Input/Output Network Appliance) - A secure research data gateway for medical imaging. Provides DICOM anonymization, quarantine management, and automated transfer from clinical to research PACS systems while ensuring General Data Protection Regulation (GDPR) compliance.

The architecture of the Fiona system consists of several layers: network layer, processing layer, storage layer, transfer layer and management layer.

.. mermaid::    
    
    flowchart TD
        subgraph network [" Network Layer "]
            PACS[📡 Clinical PACS<br/>DICOM File Source]
            StoreSCP[📥 storescpFIONA<br/>DICOM SCP]
        end
        
        subgraph processing [" Processing Layer "]
            ProcessFile[🔄 processSingleFile3.py<br/>DICOM Processing]
            DetectStudy[🔍 detectStudyArrival.sh<br/>Study Detection]
            Classification[⚙️ Classification<br/>Rule Engine]
            NamedPipe((Named Pipe))
        end
        
        subgraph storage [" Storage Layer "]
            FileSystem[💾 File System<br/>/data/site/]
            SymLinks[🔗 Symbolic Links<br/>Study/Series]
        end
        
        subgraph transfer [" Transfer Layer "]
            Anonymize[🔒 anonymizeAndSend.py<br/>Anonymization]
            SendFiles[📤 sendFiles.sh<br/>SFTP Transfer]
            ResPACS[🏥 Research PACS<br/>Destination]
            REDCap[(🗄️ REDCap)]
        end
        
        subgraph mgmt [" Management Layer "]
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
