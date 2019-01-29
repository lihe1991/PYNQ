SUMMARY = "Xilinx PYNQ Computer Vision package"
HOMEPAGE = "https://github.com/Xilinx/PYNQ-ComputerVision"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=159123dc9f55c16eb1efb4566954a3bb"
RDEPENDS_${PN} += "\
	python3-pynq \
	python3-opencv \
	"
SRC_URI = "git://github.com/Xilinx/PYNQ-ComputerVision.git;protocol=https"
SRCREV = "c7e842b4a065d29be0aeff25da7e3cc057639ec0"
S = "${WORKDIR}/git"


inherit setuptools3 pynq-package

do_compile_prepend() {
install -d "${D}/home/root/notebooks"
}

do_install_prepend() {
install -d "${D}/home/root/notebooks"
}
