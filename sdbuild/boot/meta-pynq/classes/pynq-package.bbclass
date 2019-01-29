PYNQ_NOTEBOOK_DIR ?= "/home/root/notebooks"

do_compile_prepend() {
export PYNQ_JUPYTER_NOTEBOOKS="${D}${PYNQ_NOTEBOOK_DIR}"
export BOARD=Ultra96
}

do_install_prepend() {
export PYNQ_JUPYTER_NOTEBOOKS="${D}${PYNQ_NOTEBOOK_DIR}"
export BOARD=Ultra96
}

FILES_${PN}-notebooks = "${PYNQ_NOTEBOOK_DIR}"
PACKAGES += "${PN}-notebooks"
