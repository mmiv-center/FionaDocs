Architecture Overview
============================

Diagram of Fiona system architecture including: network layer, processing layer, storage layer, transfer layer and management layer

.. mermaid::    
    
    graph TB
        subgraph network [" Network Layer "]
            PACS[📡 Clinical PACS<br/>DICOM Source]
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



System Purpose
--------------

FIONA serves as an intermediary system that:

* Receives medical image data from clinical PACS systems
* Processes and classifies incoming DICOM studies
* Anonymizes data according to research requirements
* Manages data transfer back to research PACS systems
* Provides project-specific data organization

Core Components
---------------

Data Reception
~~~~~~~~~~~~~~

* **storescpFIONA** - Custom DICOM SCP (Service Class Provider) server
* **storectl.sh** - Service controller for DICOM reception
* **Named pipes** - Communication mechanism between components

Data Processing
~~~~~~~~~~~~~~~

* **processSingleFile3.py** - Main DICOM processing daemon
* **detectStudyArrival.sh** - Study arrival detection and workflow management
* **Classification system** - Rule-based study classification

Data Management
~~~~~~~~~~~~~~~

* **File system organization** - Project-specific directory structures
* **Symbolic link management** - Study/Series organization
* **Data cleanup** - Automated file maintenance

Data Transfer
~~~~~~~~~~~~~

* **anonymizeAndSend.py** - Data anonymization and transfer
* **sendFiles.sh** - Automated file transfer to research PACS
* **Transfer request system** - REDCap integration for transfer management

System Architecture
-------------------

FIONA operates as a multi-layered system:

1. **Network Layer** - DICOM protocol handling
2. **Processing Layer** - Data classification and organization
3. **Storage Layer** - File system management
4. **Transfer Layer** - Data export and anonymization
5. **Management Layer** - Monitoring and control

General overwier (ver. 1)

.. mermaid::

   graph TB
       A[PACS Scanner]
       B[REDCap Database] 
       C[External Services]
       D[DICOM Input]
       E[Data Processing]
       F[File Storage]
       G[Export Layer]
       H[Web Interface]
       
       A --> D
       D --> E
       E --> F
       F --> G
       G --> C
       E --> B
       H --> E
       
-----

More detailed system overwier (ver. 2).

.. mermaid::

    graph TB
        subgraph ext [" External Systems "]
            PACS[📡 PACS/Scanner]
            REDCap[🗄️ REDCap Database]
            Cloud[☁️ External Services]
        end
        
        subgraph fiona [" FIONA System "]
            Input[📥 DICOM Input<br/>Store SCP, MPPS]
            Processing[🔄 Data Processing<br/>Parse, Anonymize, Route]
            Storage[💾 File Storage<br/>Archive & Metadata]
            Export[📦 Export Engine<br/>ZIP, Format Convert]
            Management[⚙️ System Management<br/>Monitor, Jobs, Health]
            WebUI[🌐 Web Interface<br/>Portal & API]
        end
        
        %% Main flow
        PACS -->|Medical Images| Input
        Input --> Processing
        Processing --> Storage
        Storage --> Export
        Export --> Cloud
        
        %% REDCap integration
        Processing <-->|Project Data| REDCap
        
        %% User interaction
        WebUI --> Processing
        WebUI --> Export
        
        %% Management
        Management --> Input
        Management --> Processing
        Management --> Storage
        
        %% Styling
        classDef external fill:#ffebee,stroke:#d32f2f,stroke-width:2px
        classDef core fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
        classDef interface fill:#e0f2f1,stroke:#00796b,stroke-width:2px
        
        class PACS,REDCap,Cloud external
        class Input,Processing,Storage,Export,Management core
        class WebUI interface

Key Features
------------

* **Multi-project support** - Handles multiple research projects simultaneously
* **Automated workflows** - Minimal human intervention required
* **Data anonymization** - Compliant with research privacy requirements
* **Scalable design** - Can handle high-volume data processing
* **Monitoring and logging** - Comprehensive system monitoring

Technology Stack
----------------

* **Python** - Core processing logic
* **Bash** - System administration and automation
* **PHP** - Web interface components
* **DICOM toolkit** - Medical image handling
* **REDCap** - Transfer request management
* **Docker** - Containerized processing components

Deployment Model
----------------

FIONA is typically deployed as:

* **Single-server installation** - All components on one machine
* **Processing user account** - Dedicated system user for operations
* **Service-based architecture** - Daemon processes for continuous operation
* **Cron-based scheduling** - Automated task execution

Such an architecture ensures reliable, automated processing of medical image data while maintaining compliance with research and privacy requirements. 

