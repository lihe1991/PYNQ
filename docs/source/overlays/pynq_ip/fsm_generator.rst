
FSM Generator
============================


The FSM Generator can generate a finite state machine in programmable hardware from a Python description. 

The size of the FSM internal memory will dictate the number of states that can be supported. 

.. image:: ../../images/fsm_generator.jpg
   :align: center

The FSM generator has an internal Block Memory which implements the finite state machine. The Trace Analyzer is controlled by a MicroBlaze subsystem. It is connected to a DMA, also controlled by the MicroBlaze subsystem which is used to load configuration information, including the Block Memory configuration to implement the FSM. 

Usage
--------------

The FSM Generator class is instantiated by importing it from the logictools subpackage: 


.. code-block:: Python

   from pynq.lib.logictools import FSMGenerator

   fsm = FSMGenerator(Arduino)

The FSM Generator module includes the following methods:

Examples
--------------



