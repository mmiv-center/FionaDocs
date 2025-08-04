cron.sh
~~~~~~~~

This script is an automation scheduler that reads event-action links from a JSON configuration file (``/var/www/html/applications/User/asttt/code/links.json``) and executes corresponding triggers and actions. It processes each link by checking if the associated event trigger conditions are met, and if so, executes the corresponding action script. The script supports email notifications with optional CSV attachments and uses temporary directories for processing outputs. It's designed to run as a cron job for automated task execution based on predefined event-action mappings.

**Related Files**

.. mermaid::

   flowchart TD
    B["links.json<br>(Configuration)"] --> A["cron.sh<br>(Main Script)"]
    C["events/*<br>(Trigger Scripts)"] --> A
    D["actions/*<br>(Action Scripts)"] --> A
    E["info.json<br>(Event Metadata)"] --> C
    F["info.json<br>(Action Metadata)"] --> D
    A --> G["sendAsEmail.sh<br>(Email Handler)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A mainScript
    class B,C,D,E,F inputFile
    class G outputFile



**Data Flow Diagram**

.. mermaid::

   flowchart TD
    A["links.json<br>(Event-Action Links)"] --> B["cron.sh<br>(Main Processor)"]
    C["events/*/info.json<br>(Event Configs)"] --> B
    D["events/*/script<br>(Trigger Scripts)"] --> B
    E["actions/*/info.json<br>(Action Configs)"] --> B
    F["actions/*/script<br>(Action Scripts)"] --> B
    
    B --> G["Temporary Directory<br>(Process Output)"]
    G --> H["email.txt<br>(Email Content)"]
    G --> I["attachment.csv<br>(Optional Attachment)"]
    
    H --> J["sendAsEmail.sh<br>(Email Sender)"]
    I --> J
    
    B --> K["Script Logs<br>(Error Logging)"]
    
    %% Styling
    classDef inputFile fill:#e1f5fe
    classDef outputFile fill:#f3e5f5
    classDef mainScript fill:#fff3e0
    
    class A,C,D,E,F inputFile
    class B mainScript
    class G,H,I,J,K outputFile



Data Paths

- Input Paths:
   * ``/var/www/html/applications/User/asttt/code/links.json`` 
   * ``/var/www/html/applications/User/asttt/code/events/*`` 
   * ``/var/www/html/applications/User/asttt/code/actions/*`` 
   * ``events/*/info.json` and `actions/*/info.json`` 

- Output Paths:
   * ``/tmp/asst_cronXXXXX/``
   * ``/tmp/asst_cronXXXXX/email.txt`` 
   * ``/tmp/asst_cronXXXXX/attachment.csv`` 
   * ``${script}_log``




------


.. include:: cron.sh
   :start-after: : '
   :end-before: ' #end-doc
