anonymizeAndSend.py
~~~~~~~~~~~~~~~~~~~~

This Python script processes DICOM medical imaging transfer requests by anonymizing patient data and sending anonymized studies to a research PACS system. The script reads JSON transfer requests, applies project-specific anonymization rules including burned-in image detection and pixel data rewriting, then sends the processed data via DICOM protocol while updating REDCap with transfer status. It handles various project features like presentation state removal, secondary capture filtering, and maintains audit trails of all processing operations.

**Related Files**

.. mermaid::

   flowchart LR
       B["/home/processing/transfer_requests/*.json"] --> A["anonymizeAndSend.py"]
       C["/data/site/raw/STUDY_UID/"] --> A
       D["/home/processing/bin/anonymize"] --> A
       E["/home/processing/bin/addNoImageImage"] --> A
       F["rewritepixel Docker container"] --> A
       G["dcmtk Docker container"] --> A
       H["REDCap API endpoints"] --> A
       A --> I["/home/processing/transfers_done/"]
       A --> J["/home/processing/transfers_fail/"]
       
       class A mainScript
       class B,C,D,E,F,G,H inputFile
       class I,J outputFile
       
       classDef inputFile fill:#e1f5fe
       classDef outputFile fill:#f3e5f5
       classDef mainScript fill:#fff3e0


**Data flow diagram**

.. mermaid::

   flowchart TD
       A[Transfer Request JSON] --> B[anonymizeAndSend.py]
       C[Raw DICOM Data] --> B
       D[REDCap Configuration] --> B
       B --> E[Anonymized DICOM]
       B --> F[Research PACS]
       B --> G[REDCap Status Update]
       B --> H[Success/Fail Logs]
       
       class A,C,D inputFile
       class B mainScript
       class E,F,G,H outputFile
       
       classDef inputFile fill:#e1f5fe
       classDef outputFile fill:#f3e5f5
       classDef mainScript fill:#fff3e0

Data paths

- Input directories:
   * ``/home/processing/transfer_requests/``,
   * ``/data/site/raw/``
- Output directories:
   * ``/home/processing/transfers_done/``,
   * ``/home/processing/transfers_fail/``
- Temporary processing:
   * System temp directories via ``tempfile.TemporaryDirectory()``


---------


.. include:: anonymizeAndSend.py
   :start-after: """
   :end-before: """
