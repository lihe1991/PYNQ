Pattern Generator
============================

The Pattern Builder can generate arbitrary digital patterns that are programmable from Python. 

.. image:: ../../images/pattern_generator.jpg
   :align: center

The Trace Analyzer has an internal Block Memory which stores a pattern that can be streamed to an external interface. The Trace Analyzer is controlled by a MicroBlaze subsystem. It is connected to a DMA, also controlled by the MicroBlaze subsystem which is used to load configuration information, including a pattern to the internal memory. 


Usage
--------------

The Pattern Generator class is instantiated by importing it from the logictools subpackage: 


.. code-block:: Python

   from pynq.lib.logictools import PatternGenerator

   pg = PatternGenerator(Arduino)

The Pattern Generator module includes the following methods:


Examples
-------------------

