Base Overlay overview
======================

The *base* overlay is the default PYNQ overlay. It is included in the PYNQ SD card image, and is loaded to the Zynq PL at boot time. The base overlay design includes the hardware IP to control the board peripherals, and connects these IP blocks to the Zynq PS. With the base overlay, board peripherals can be used from the Python environment immediately after the system boots. 

Board peripherals typically include GPIO devices (LEDs, Switches, Buttons), Video, Audio, and any other general purpose and custom interfaces. In the case of a general purpose interfaces, for example Pmod and Arduino headers, the base overlay may include an IOP for the interface, or a simple GPIO interface.

Reference design
---------------------

The base overlay design can also be used as a reference design for a board when creating new overlays. The base overlay project will include the setting which should be used for any new overlay design. 

Any controllers, or IP that are not required can be removed from the base overlay design, and any custom hardware blocks can be added. 

Base overlay project files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All project source files for the base overlay can be found here:

    ``<GitHub Repository>/boards/<board>/base``

The makefile and/or .tcl file in the directory can be used to rebuild the overlay. 

The base overlay can include IP from the Vivado library, and custom IP. Any custom IP for overlays can be found here:

    ``<GitHub Repository>/boards/ip`` 

For more details on rebuilding the overlay, or creating a new overlay, see the `Overlay Design Methodology <../overlay_design_methodology_index.html>`_ section. 

Porting PYNQ
--------------
If PYNQ is ported to another board, a base overlay should be created and used as the default PYNQ overlay for that board. 

