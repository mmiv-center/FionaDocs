:tocdepth: 2

.. _export-guide:

Export
======

.. raw:: latex

   \sphinxsetup{bookmarksdepth=3}

Search and filters
------------------

Above the study list there is a search field and a "Filters" menu. They only hide rows of the list; they do not change any data.

Search field
^^^^^^^^^^^^

Type text in the search field. The list updates while you type. The search is not case sensitive and looks in all columns except "Actions". Click the "x" in the field to clear it and show the whole list again.

``*`` means "anything". The field also accepts regular expressions (you can test patterns at `regex101 <https://regex101.com>`_).

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Search text
     - Shows rows ...
   * - ``MR``
     - containing MR
   * - ``PatientID*baseline*MR``
     - containing these words in this order
   * - ``MR|CT``
     - containing MR or CT
   * - ``\b202406``
     - with a number starting with 202406, e.g. a study date in June 2024
   * - ``100200\b``
     - with a number ending with 100200, e.g. an accession number

.. figure:: ../../_static/export-search-1.png
   :width: 100%

   The search field with the text "DEMO*baseline*MR". Only matching rows are shown.

Filters
^^^^^^^

Click the arrow next to "Search" to open the filters. There are four groups with check boxes:

- **Events**: the event of the study (baseline, year_2, ...).
- **Modalities**: the modality of the study (MR, CT, ...).
- **Actions**: the state of the download button: Not prepared (blue), Preparing (orange), Ready (green), Failed (red).
- **ZIP File Size**: the size of the ready ZIP file. A range includes its lower limit and excludes its upper limit. Rows without a ready ZIP file are hidden when a size is ticked.

The number in brackets is the number of rows in the project with this value. It does not depend on the other filters.

"Clear" next to a group unticks that group. "Clear All" at the top of the menu unticks all groups. The "Search" button and the arrow have a green fill when at least one filter is active.

.. figure:: ../../_static/export-search-2.png
   :width: 60%

   The open "Filters" menu with "MR" and "Ready" ticked. The ticked options are marked in orange.

How conditions are combined
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Ticked options inside one group are combined with **OR**: "Ready" and "Failed" show rows that are ready or failed.
- Different groups and the search text are combined with **AND**: a row is shown only if it matches all of them.

Secure download (email)
-----------------------

The Export application can send a study as a password-protected archive to one or more e-mail addresses. The recipients get a download link and, in a separate e-mail, the password.

Steps
^^^^^

1. Select the project and the export format.
2. In the row of the study, open the menu and click "Secure download (email)". The window for a secure download opens.

   .. figure:: ../../_static/export-email-1.png
      :width: 100%

      The menu of a study row. "Secure download (email)" is marked in orange.

3. A random 12-character password is already filled in. You can keep it, enter your own password, or click "generate" to create a new random password.
4. Enter the e-mail address of the recipient. To send to several recipients, separate the addresses with a semicolon (;) or a comma (,), for example ``name1@helse-bergen.no;name2@ihelse.net``. All addresses must belong to Helse Bergen (ending with @helse-bergen.no or @ihelse.net).
5. Click "Send as email".

   .. figure:: ../../_static/export-email-2.png
      :width: 60%

      The window "Secure download link" with a generated password and two recipients. The "Send as email" button is marked in orange.

Result
^^^^^^

- The export is added to the download queue, the same queue as used by "Prepare". When the archive is ready, each recipient gets two e-mails from no-reply@helse-bergen.no:

  - "FIONA link to archive": the project name, a link to the archive and your e-mail address as the contact person.
  - "no-reply", about 15 seconds later: the password only.

.. figure:: ../../_static/export-email-3.png
   :width: 90%

   The first e-mail, "FIONA link to archive". The link to the archive is marked in orange.

.. figure:: ../../_static/export-email-4.png
   :width: 90%

   The second e-mail, "no-reply". The password is marked in orange.

- The archive is a 7z file encrypted with the password. File names inside the archive are also hidden.
- The recipient must log in to Fiona to download the archive.
- The link is active for 7 days. If it has expired, the recipient should contact you for a new link.
- To open the 7z file, the recipient needs a program that supports 7z archives, for example 7-Zip. Ask your IT department to install it.

.. note::

   Only e-mail addresses ending with @helse-bergen.no or @ihelse.net are accepted. If any address is not accepted, no e-mail is sent to any recipient and no error message is shown.

.. note::

   The data is pseudonymized but counts as health data. Store it only in secure locations.

.. raw:: latex

   \sphinxsetup{bookmarksdepth=5}
