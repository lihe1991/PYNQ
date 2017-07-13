
Boolean Generator
============================


The Boolean Generator can generate combinatorial Boolean logic functions from custom hardware. Fucntions of up to 5 inputs with 1 output are supported. Exteranl IO and internal signals can be used as inputs/outputs. 

The size of the FSM internal memory will dictate the number of states that can be supported. 

.. image:: ../../images/boolean_generator.png
   :align: center

The Boolean generator is controlled from a MicroBlaze subsystem which loads the configuration to implement the logic functions. AND, OR, NOT, XOR are supported. 

Usage
--------------

The FSM Generator class is instantiated by importing it from the logictools subpackage: 


.. code-block:: Python

   from pynq.lib.logictools import FSMGenerator

   fsm = FSMGenerator(Arduino)

The FSM Generator module includes the following methods:

Examples
--------------



