Advanced Features
=================

This chapter shows advanced documentation features.

Complex Tables
--------------

Feature comparison table:

.. list-table:: Feature Comparison
   :widths: 25 25 25 25
   :header-rows: 1

   * - Feature
     - Version 1.0
     - Version 2.0
     - Notes
   * - Real-time Processing
     - No
     - Yes
     - Added in v2.0
   * - Multi-format Support
     - Yes
     - Yes
     - Multiple formats
   * - GPU Acceleration
     - Yes
     - Yes
     - CUDA support

CSV Table
---------

.. csv-table:: Sample Data
   :header: "Name", "Age", "City"
   :widths: 30, 10, 20

   "Alice", "25", "Bergen"
   "Bob", "30", "Oslo"
   "Charlie", "35", "Trondheim"

Mathematical Formulas
---------------------

Basic math formula:

.. math::

   f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}

Inline math: :math:`E = mc^2`

ASCII Diagrams
--------------

Simple diagram:

::

   Data Flow:
   
   Input -> Processing -> Output
             |
             v
         Validation

References
----------

.. [Smith2024] Smith, J. "Documentation Best Practices", 2024.

You can reference citations like this [Smith2024]_.

Glossary
--------

.. glossary::

   MMIV
      Mohn Medical Imaging and Visualization Centre

   API
      Application Programming Interface

Version Info
------------

.. versionadded:: 1.0
   Initial release.

.. versionchanged:: 2.0
   Added new features.
