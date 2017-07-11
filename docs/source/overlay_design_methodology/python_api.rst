Creating a Python API
=========================

The Python API is the user interface for the overlay, exposeing the programmable functionalityin the design. 

An API for a PYNQ overlay can consist of

* a simple Python wrapper that interfaces directly with the hardware IP blocks in the overlay
* a more substantial Python layer utilising other Python packages
* a Python library that interfaces to a lower level higher performance library (written in C/C++ for example) to control the overlay

Connecting to the PL 
----------------------

The API for an overlay will manage the transfer of data between the Python environment in the PS, and the overlay in the PL. This may be the transfer of data directly from the PS to a peripheral or managing system memory to allow a peripheral in the PL to read or write data from DRAM that can also be access by from the Python environment.

A number of Python classes to support data transfer are available. These are the MMIO, Xlnk, DMA and GPIO classes. Each of these classes correspond to an interface type, and are covered in more detail in the next section. They allow transfer of data by reading and writing registers in an overlay, transfer of data from DRAM to the overlay using DMAs, reading and writing simple control data using GPIOs, and allocation of memory to allow the overlay to write data directly to DRAM that can then be accessed from the Python environment. 

These classes are the building blocks for creating a custom Python API for an overlay. This allows a Python wrapper to interface directly with an overlay.

