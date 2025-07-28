*** ARCHITECTURE (options) ***
==============================================

**For:** Developers, system architects

**Contains:**

- Source code documentation
- System components description
- APIs and interfaces
- Scripts and tools
- Data flow diagrams




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


