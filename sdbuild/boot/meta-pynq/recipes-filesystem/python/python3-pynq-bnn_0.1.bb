SUMMARY = "Classification using a hardware accelerated neural network with different precision for weights and activation"
HOMEPAGE = "http://www.pynq.io/ml"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=8f625d3c898c18035639b6d6943b6a9c"
RDEPENDS_${PN} += "\
	python3-pynq \
	python3-pillow \
	libstdc++ \
	"

SRC_URI = "git://github.com/Xilinx/BNN-PYNQ.git;protocol=https \
	file://0001-Hardcode-version-to-avoid-import-bnn.patch \
	file://0002-Fix-notebook-install-path.patch \
	"

SRCREV = "2b502ddb57aa4010fb34e4e36c7e1fb95902684c"
S = "${WORKDIR}/git"

inherit setuptools3 pynq-package

do_compile_prepend() {
rm -rf ${S}/bnn/src
install -d "${D}/home/root/notebooks"
}

do_install_prepend() {
install -d "${D}/home/root/notebooks"
}

do_install_append() {
rm -rf ${D}/usr/lib/python3.5/site-packages/bnn/libraries/pynqZ1-Z2
}

