Code Examples
=============

This chapter shows how to include code in documentation.

Basic Code Block
----------------

Simple code without highlighting:

::

    def hello_world():
        print("Hello, World!")
        return True

Python Code
-----------

Python code with syntax highlighting:

.. code-block:: python

   def analyze_data(data):
       """
       Analyze input data.
       
       Parameters:
       -----------
       data : list
           Input data
           
       Returns:
       --------
       dict
           Results
       """
       result = sum(data) / len(data)
       return {'average': result, 'count': len(data)}

JavaScript Code
---------------

.. code-block:: javascript

   function processData(data) {
       const result = data.map(item => item * 2);
       return {
           original: data,
           processed: result,
           length: data.length
       };
   }

Inline Code
-----------

You can include inline code like ``import numpy`` or reference functions like ``analyze_data()`` within text.

Configuration Example
---------------------

YAML configuration:

.. code-block:: yaml

   project:
     name: "Documentation Example"
     version: "1.0.0"
   
   settings:
     output: "html"
     theme: "default"
