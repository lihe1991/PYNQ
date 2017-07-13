
Pynq-Z1 audio Subsystem
============================

The Pynq-Z1 has a  3.5mm mono audio jack for audio-out, and an omnidirectional MEMS microphone integrated on the board for audio-in. 

The audio out needs to be driven by a PWM signal, and the digitized audio from the mic is in the pulse density modulated (PDM) format.

For more information on the audio subsystem see the relevant sections in the `PYNQ-Z1 reference guide <https://reference.digilentinc.com/reference/programmable-logic/pynq-z1/reference-manual>`_ 

The audio subsystem int he PYNQ-Z1 base overlay consists of an IP block to drive the PWM mono output, and another block to read the PDM input from the MIC.  
   
.. image:: ../../images/audio_subsystem.png
   :align: center
   
The PYNQ Audio module includes the following methods:

* ``bypass_start()`` - Stream audio controller input directly to output.
* ``bypass_stop()`` - Stop streaming input to output directly.
* ``load(file)`` - Loads file into internal audio buffer.
* ``play()`` - Play audio buffer via audio jack.
* ``record(seconds)`` - Record data from audio controller to audio buffer.
* ``save(file)`` - Save audio buffer content to a file.

For more information on the PYNQ audio class, run ``help()`` on the audio instance in the overlay.

E.g. 

   .. code-block:: Python
      
      from pynq import Overlay
      base = Overlay("base.bit")
      audio = base.audio
      help(audio)
 
Audio 
Examples
------------

See the example notebooks on the board in the following directory:

   .. code-block:: console

      base\audio\audio_playback.ipynb

