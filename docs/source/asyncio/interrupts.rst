********************************************
Interrupts
********************************************

.. contents:: Table of Contents
   :depth: 2

Introduction
=========================================
Each IOP has its only interrupt controller. This allows IOP peripherals (IIC, SPI, GPIO, Uart, Timers) to interrupt the MicroBlaze processor inside the IOP. The IOP uses the `AXI Interrupt Controller <https://www.xilinx.com/products/intellectual-property/axi_intc.html>`_. It can be used in an IOP application in the same way as any other MicroBlaze application to manage this local interrupts.

The base overlay also has a interrupt controller connected to the interrupt pin of the Zynq PS. The overlay interrupt controller can be triggered by the MicroBlaze inside an IOP to signal to the PS and Python that an interrupt has occurred in the overlay. 

.. image:: ../images/pynqz1_base_overlay_intc_pin.png
   :align: center

Interrupts in PYNQ can be handled in different ways as discused in the examples below. 

*asyncio* introduces a new method of handling interrupts from within the Python code running on the ARM CPUs.  

The asyncio package is a relatively new Python library, (added provisionally in Python 3.4 and declared stable in 3.6) `Python 3.6 documentation on asyncio <https://docs.python.org/3.6/whatsnew/3.6.html#asyncio>`_. 

It is included in this Pynq release as part of Python 3.6.


Asyncio
=========

Motivation 
----------

A Python program can use the asyncio library to manage multiple IO-bound tasks asynchronously, thereby avoiding any blocking caused by waiting for responses from slower IO subsystems.  Instead, the program can continue to execute other tasks that are ready to run.  When the previously-busy tasks are ready to resume, they will be executed in turn, and the cycle is repeated.

In the Pynq framework, real-time tasks are most often implemented using the appropriate IP blocks in the programmable logic.  While such tasks are executing in the PL, they can raise interrupts on the ARM A9 CPUs at any time. Python's asyncio library provides an effective way to manage such events from asynchronous, IO-bound tasks.

The asyncio library has several advantages:

* it does not require multiple threads or processes so it uses fewer system resources 

* it schedules execution using cooperative multitasking so it avoids problems of race conditions and deadlocks

* it uses coroutines to abstract the user from direct handling of callbacks.  This allows the user to write concurrent code in a style that preserves the familiarity of sequential code, resulting in simpler and more manageable programs

Introduction to Asyncio
-----------------------

The asyncio concurrency framework relies on coroutines, futures, tasks, and an event loop.  We will introduce these briefly before demonstrating their use with some introductory examples.  

Coroutines
^^^^^^^^^^
Coroutines are a new Python language construct.  They introduce two new keywords `async` and `await` to the Python syntax. Coroutines are stateful functions whose execution can be paused. This means that they can yield execution, while they wait on some task or event to complete. While suspended, coroutines maintain their state.  They are resumed once the outstanding activity is resolved.  The `await` keyword determines the point in the coroutine where a it yields control and from which execution will resume.

Futures
^^^^^^^
A future is an object that acts as a proxy for a result that is initially unknown, usually because the action has not yet completed.  Futures are essential components in the internals of asyncio.  Futures encapsulate pending operations so that they can be put in queues, their state of completion can be queried, and their results  can be retrieved when ready. They are meant to be instantiated exclusively by the concurrency framework, rather than directly by the user.

Tasks
^^^^^
Coroutines do not execute directly.  Instead, they are  wrapped in tasks and registered with an asyncio event loop.  Tasks are a subclass of Futures.

Event Loop
^^^^^^^^^^
The event loop is responsible for executing all ready tasks, polling the status of suspended tasks, and scheduling outstanding tasks.

An event loop runs only one task at a time.  It relies on cooperative scheduling.  This means that no task interrupts another, and each task yields control to the event loop when its execution is blocked.  The result is single-threaded, concurrent code in which the next cycle of the loop does not start until all the event handlers are executed sequentially.

Example
-------------------------

A simple example is shown below.  It consists of a coroutine called ```wake_up``` which is defined using the new ```async def``` syntax.  Function ```main``` creates an asyncio event loop.  Then it wraps the ```wake_up``` coroutine in a task called ```wake_up_task``` and registers it with the event loop to be scheduled for execution.  Within the coroutine,  the ```await``` statement marks the point at which execution is initially suspended, and later resumed.  The loop executes the following schedule:

* it starts to execute the ```wake_up_task```
* then it suspends ```wake_up_task```, while preserving its state
* next asyncio.sleep runs for a random number of seconds (1 to 5 inclusive)
* the ```wake_up_task``` is resumed
* the task runs to completion using the recovered state

Finally the event loop itself is closed.  

.. code-block:: Python

    import asyncio
    import random
    import time
    
    # Coroutine
    async def wake_up(delay):
        '''A coroutine that will yield to asyncio.sleep() for a few seconds
           and then resume, having preserved its state while suspended
        '''
        
        start_time = time.time()
        print(f'The time is: {time.strftime("%I:%M:%S")}')
        print(f"Suspending coroutine 'wake_up' at 'await` statement\n")
        await asyncio.sleep(delay)
        print(f"Resuming coroutine 'wake_up' from 'await` statement")
        end_time = time.time()
        sleep_time = end_time - start_time
        print(f"'wake-up' was suspended for precisely: {sleep_time} seconds")
     
    # Event loop 
    if __name__ == '__main__':
        delay = random.randint(1,5)
        my_event_loop = asyncio.get_event_loop()
        try:
            print("Creating task for coroutine 'wake_up'\n")
            wake_up_task = my_event_loop.create_task(wake_up(delay))
            my_event_loop.run_until_complete(wake_up_task)
        except RuntimeError as err:
            print (f'{err}' +
                   ' - restart the Jupyter kernel to re-run the event loop')
        finally:
            my_event_loop.close()


A sample run of the code produces the following output:

.. code-block:: Console

    Creating task for coroutine 'wake_up'
    
    The time is: 11:09:28
    Suspending coroutine 'wake_up' at 'await` statement
    
    Resuming coroutine 'wake_up' from 'await` statement
    'wake-up' was suspended for precisely: 3.0080409049987793 seconds 


Notes on event loop performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any blocking call in event loop should be replaced with a coroutine. If you do not do this, when a blocking call is reached, it will block the rest of the loop. 

If you need blocking calls, they should be in separate threads. Compute workloads should also be in separate threads/processes. 

Interrupts in PYNQ using asyncio
==================================

Asyncio can be used for managing interrupt events from the overlay. A coroutine can be run in an event loop and used to check the status of the interrupt controller in the overlay, and handle any event. Other user functions can also be run in the event loop. If an interrupt is triggered, the next time the "interrupt" coroutine is scheduled, it will service the interrupt. The responsiveness of the interrupt coroutine will depend on how frequently the user code yields control in the loop. 

Interrupts in the Base Overlay
------------------------------

The I/O peripherals in the base overlay will trigger interrupts when switches are toggled or buttons are pressed. Both the *Button* and *Switch* classes have a function ``wait_for_level`` and a coroutine ``wait_for_level_async`` which block until the corresponding button or switch has the specified value. This follows a convention throughout the PYNQ python API that that coroutines have an ``_async`` suffix.

As an example, consider an application where each LED will light up when the corresponding button is pressed. First a coroutine specifying this functionality is defined:

.. code-block:: Python

    async def button_to_led(number):
        button = pynq.board.Button(number)
        led = pynq.board.LED(number)
        while True:
            await button.wait_for_level_async(1)
            led.on()
            await button.wait_for_level_async(0)
            led.off()

Next add instances of the coroutine to the default event loop

.. code-block:: Python

    tasks = [asyncio.ensure_future(button_to_led(i) for i in range(4)]

Finally, running the event loop will cause the coroutines to be active. This code runs the event loop until an exception is thrown or the user interrupts the process.

.. code-block:: Python

    asyncio.get_event_loop().run_forever()


IOP and Interrupts
------------------------------

The IOP class has an ``interrupt`` member variable which acts like an *asyncio.Event* with a ``wait`` coroutine and a ``clear`` method. This event is automatically wired to the correct interrupt pin or set to ``None`` if interrupts are not available in the loaded overlay. 

e.g.

.. code-block:: Python

    def __init__(self)
        self.iop = request_iop(iop_id, IOP_EXECUTABLE)
        if self.iop.interrupt is None:
           warn("Interrupts not available in this Overlay")

There are two options for running functions from this new IOP wrapper class. The function can be called from an external asyncio event loop (set up elsewhere), or the function can set up its own event loop and then call its asyncio function from the event loop.

Async function
----------------------

By convention, the PYNQ python API offers both an asyncio coroutine and a blocking function call for all interrupt-driven functions. It is recommended that this should be extended to any user-provided IOP drivers. The blocking function can be used where there is no need to work with asyncio, or as a convenience function to run the event loop until a specified condition. The coroutine is given the ``_async`` suffix to avoid breaking backwards compatibility when updating existing functions.

The following code defines an asyncio coroutine. Notice the ``async`` and ``await`` keywords are the only additional code needed to make this function an asyncio coroutine.

.. code-block:: Python

    async def interrupt_handler_async(self, value):
        if self.iop.interrupt is None:
            raise RuntimeError('Interrupts not available in this Overlay')
        while(1):
            await self.iop.interrupt.wait() # Wait for interrupt
            # Do something when an interrupt is received
            self.iop.interrupt.clear()

Function with event loop
---------------------------

The following code wraps the asyncio coroutine, adding to the default event loop and running it until the coroutine completes.

.. code-block:: Python
    
    def interrupt_handler(self):   
    
        if self.interrupt is None:
            raise RuntimeError('Interrupts not available in this Overlay')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(
            self.interrupt_handler_async()
        ))

Custom interrupt handling
---------------------------

The Python *Interrupt* class can be found here:

.. code-block:: console

    <GitHub Repository>\pynq\interrupt.py

This class abstracts away management of the AXI interrupt controller in the PL. It is not necessary to examine this code in detail to use interrupts. The interrupt class takes the pin name of the interrupt line and offers a single ``wait`` coroutine. The interrupt is only enabled in the hardware for as long as a coroutine is waiting on an *Interrupt* object. The general pattern for using an Interrupt is as follows:

.. code-block:: Python

    while condition:
        await interrupt.wait()
        # Clear interrupt

This pattern avoids race conditions between the interrupt and the controller and ensures that an interrupt isn't seen multiple times.

Interrupt pin mappings
=========================

Interrupts are also available from the GPIO (Pushbuttons, Switches, Video, Trace buffer Arduino, Trace buffer Pmods). 

=============== ========== =====================================
Name             IOP ID     Pin
=============== ========== =====================================
PMODA            1          iop1/dff_en_reset_0/q
PMODB            2          iop2/dff_en_reset_0/q
ARDUINO          3          iop3/dff_en_reset_0/q
Buttons                     btns_gpio/ip2intc_irpt
Switches                    swsleds_gpio/ip2intc_irpt
Video                       video/dout
Trace(Pmod)                 tracepmods_arduino/s2mm_introut
Trace(Arduino)              tracebuffer_arduino/s2mm_introut
=============== ========== =====================================


Interrupt examples using asyncio
===================================

Example notebooks
-----------------

The `asyncio_buttons.ipynb <https://github.com/Xilinx/PYNQ/blob/master/Pynq-Z1/notebooks/examples/asyncio_buttons.ipynb>`_ notebook can be found in the examples directory. The Arduino LCD IOP driver provides an example of using the IOP interrupts.