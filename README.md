![alt tag](./logo.png)

PYNQ is an open-source project from Xilinx that makes it easy to design embedded systems with Zynq All Programmable Systems on Chips (APSoCs), and make use of accelerators on Alveo data center cards. Using the Python language and libraries, designers can exploit the benefits of programmable logic and microprocessors in Zynq to build more capable and exciting embedded systems, as well as tap into the potential of hardware acceleration in the data center space.
PYNQ users can now create high performance embedded applications with
-	parallel hardware execution
-	high frame-rate video processing
-	hardware accelerated algorithms
-	real-time signal processing
-	high bandwidth IO
-	low latency control
And easily accelerate a range of data center workloads including
-   high performance computing
-   data analytics
-   networking
-   video processing

See the <a href="http://www.pynq.io/" target="_blank">PYNQ webpage</a> for an overview of the project, and find <a href="http://pynq.readthedocs.io" target="_blank">documentation on ReadTheDocs</a> to get started. 

## Precompiled Image for Zynq

The project currently supports <a href="http://www.pynq.io/board.html" target="_blank">multiple Zynq and Zynq Ultrascale+ boards</a>. 

You can download a precompiled image, write the image to a micro SD card, and boot the board from the micro SD card.

## Alveo support

For Alveo cards, PYNQ currently requires a <a href="https://github.com/Xilinx/XRT" target="_blank">Xilinx Runtime (XRT)</a> version above or equal to 2.3 to be installed in the system. In terms of Operating System, any XRT-supported version of either RedHat/CentOS or Ubuntu can be used. Previous versions of XRT might still work, but are not supported. Moreover, the functionalities offered by the Embedded Runtime Library (ERT) will not work with versions of XRT below 2.3.

## Quick Start

See the <a href="http://pynq.readthedocs.io/en/latest/getting_started.html" target="_blank">Quickstart guide</a> for details on writing the PYNQ image to an SD card, and getting started with a PYNQ-enabled Zynq board.

Similarly, a <a href="https://pynq.readthedocs.io/en/latest/getting_started/alveo.htmll" target="_blank">getting started guide</a> is also available for Alveo cards.

## Python Source Code

All Python code for the `pynq` package can be found in the `/pynq` folder. This folder can be found on a Zynq board after the board boots with the precompiled image.

To update your PYNQ SD card to the latest ``pynq`` package, you can run the following command from a terminal connected to your board:

```console
sudo pip3 install --upgrade pynq
```

The same command will also work to upgrade PYNQ on your system mounting an Alveo card.

SDK software projects and Python-C source codes are also stored along with the Python source code. After installing the `pynq` package, the compiled target files will be saved automatically into the `pynq` package.

## Board Files and Overlays

All board related files including Vivado projects, bitstreams, and example notebooks, can be found in the `/boards` folder.

In Linux, you can rebuild the overlay by running *make* in the corresponding overlay folder (e.g. `/boards/Pynq-Z1/base`). In Windows, you need to source the appropriate tcl files in the corresponding overlay folder.

## Contribute

Contributions to this repository are welcomed. Please refer to <a href="https://github.com/Xilinx/PYNQ/blob/master/CONTRIBUTING.md" target="_blank">CONTRIBUTING.md</a> 
for how to improve PYNQ.

## Support

Please ask questions on the <a href="https://discuss.pynq.io" target="_blank">PYNQ support forum</a>.

## Licenses

**PYNQ** License: [BSD 3-Clause License](https://github.com/Xilinx/PYNQ/blob/master/LICENSE)

**Xilinx Embedded SW** License: [Multiple License File](https://github.com/Xilinx/embeddedsw/blob/master/license.txt)

**Digilent IP** License: [MIT License](https://github.com/Xilinx/PYNQ/blob/master/THIRD_PARTY_LIC)

**Xilinx Runtime (XRT)** License: [Apache 2.0 License](https://github.com/Xilinx/PYNQ/blob/master/THIRD_PARTY_LIC)

## SDBuild Open Source Components

**License and Copyrights Info** [TAR/GZIP](http://bit.ly/2Os4h03)

**Open Components Source Code** [TAR/GZIP](http://bit.ly/2AUmcUY)
