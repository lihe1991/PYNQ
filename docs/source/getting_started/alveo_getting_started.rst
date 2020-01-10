.. _alveo:

***************************
Alveo Getting Started Guide
***************************

Prerequisites
=============

  * An x86 machine with at least an Alveo card mounted
  * A version of the `Xilinx Runtime <https://github.com/Xilinx/XRT>`_ (XRT) above or equal ``2.3`` installed in the system. Previous versions of XRT might still work, but are not supported. Moreover, the functionalities offered by the Embedded Runtime Library (ERT) will not work with versions of XRT below ``2.3``.
  * Any XRT-supported version of either RedHat/CentOS or Ubuntu as Operating System
  * Python and PIP must be installed. The minimum Python version is ``3.5.2``, although the recommended minimum version is ``3.6.x``

Initial setup
=============

The first thing you will have to do, before installing PYNQ as well as well as before every session, is source the XRT setup script.
To do so, open up a bash bash and type:

.. code-block:: bash
    
    source /opt/xilinx/xrt/setup.sh

The path ``/opt/xilinx/xrt`` is the predefined install path for XRT and should not be changed. Therefore, the setup script will always be located there.

Install PYNQ system-wide
========================

In case you want to install the PYNQ package system-wide, make sure you have Python already installed, alongside PIP for packages installation. The minimum required version is Python 3.5.2, although it is recommended to have at least Python ``3.6`` and above.
To install PYNQ, after having sourced XRT as shown previously, in the same shell you can type

.. code-block:: bash
    
    sudo pip3 install pynq

By default, installing ``pynq`` will not install ``jupyter``. In case you want it, you can install it using PIP

.. code-block:: bash
    
    sudo pip3 install jupyter

Or install the ``alveopynq`` examples package, that will install it as a dependency, alongside the other packages required to run the included example notebooks.

.. note:: When installing jupyter with a version of Python less than ``3.6``, you will have to make sure to have a compatible version of ``ipython`` installed. Therefore, in this case after installing jupyter, force-install ipython with an appropriate version. The recommended is version ``7.9``, and you can ensure this is the version installed by running ``sudo pip3 install --upgrade ipython==7.9``.

.. note:: Although possible, we recommend not to install ``pynq`` system-wide, but rather create a Conda environment for it. You can read how to do it below.

Install the Alveo examples
--------------------------

In order to get the introductory examples, you will have to also install the ``alveopynq`` package, like so

.. code-block:: bash
    
    sudo pip3 install alveopynq


Install PYNQ in a Conda environment
===================================

There are cases in which installing ``pynq`` as a system-wide package will not be possible due to permissions, or some requirements are missing. In this case, the best approach is to install `Conda <https://docs.conda.io/en/latest/>`_ and create a Conda environment where to install everything. In general, this will also avoid polluting the system environment and it is the way we recommend to get everything setup.

To install Conda, you can follow the `official installation guide <https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html>`_.

After you have installed it (make sure conda is in your ``PATH``, and in case not source activation script in ``<your-conda-install-path>/bin/activate``), follow these simple steps to get everything you need:

  1. Save the following code snipped as ``environment.yml``

      .. code-block:: yaml

         name: pynq-env
         channels:
           - conda-forge
           - defaults
         dependencies:
           - cffi=1.13.2=py38h2e261b9_0
           - jupyterlab=1.2.4=pyhf63ae98_0
           - jupyterlab-plotly-extension=1.0.0=py_0
           - numpy=1.17.4=py38hc1035e2_0
           - pip=19.3.1=py38_0
           - plotly=4.4.1=py_0
           - python=3.8.0=h0371630_2

  2. Create the ``pynq-env`` environment using the above configuration

      .. code-block:: bash

         conda env create -f environment.yml

  3. Activate the newly created environment, install pynq (remember that the XRT setup script need to be sourced in the current shell session before installing ``pynq``)

      .. code-block:: bash

         conda activate pynq-env
         pip install pynq

Install the Alveo examples
--------------------------

Similarly to the system-wide case, to get the introductory examples ``alveopynq`` package will also be required

.. code-block:: bash
    
    pip install alveopynq

Activate the environment again later
------------------------------------
Again, make sure that conda is in your ``PATH``, and then simply run
.. code-block:: bash
    
    source /opt/xilinx/xrt/setup.sh
    conda activate pynq-env


Run jupyter and test out the introductory examples
==================================================

After you have installed both ``pynq`` and ``alveopynq``, here is what you will need to do to deploy the examples and test them in jupyter

.. code-block:: bash
    source /opt/xilinx/xrt/setup.sh
    pynq examples
    cd pynq-examples
    jupyter notebook

The sourcing of the XRT setup script can be avoided if it was already done in the current shell session. 

.. note:: When deploying the examples using the ``pynq examples`` command, make sure to have a supported Alveo card (and more importantly, a supported shell) or the examples will not be deployed. Overlays are downloaded from the network and are available only for specific cards/shells. You may also synthesize the provided overlays for your target Alveo card manually and use them instead. Also, the ``pynq examples`` command has a few optional parameters that can be used to customize the examples installation. Please run ``pynq examples -h`` to see them. You can find out more detailed info at the `Alveo-PYNQ GitHub repo <https://github.com/Xilinx/Alveo-PYNQ>`_.
