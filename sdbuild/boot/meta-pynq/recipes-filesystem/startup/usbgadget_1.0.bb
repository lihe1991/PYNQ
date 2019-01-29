SUMMARY = "USB Gadget for Ethernet"

SRC_URI = "file://usbgadget.sh \
	file://udhcpd.conf \
	file://usbgadget-setup.sh \
	"

LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://usbgadget.sh;beginline=2;endline=2;md5=9427d9ad24b0e285db0d3517c01e6ae7"

RDEPENDS_${PN} += " \
	busybox \
	"

inherit update-rc.d
INITSCRIPT_PACKAGES = "${PN}"
INITSCRIPT_NAME = "usbgadget-setup.sh"
INITSCRIPT_PARAMS = "start 98 S ."

FILES_${PN} += "${datadir}/usbgadget"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${datadir}/usbgadget
    install -d ${D}${INIT_D_DIR}

    install -m 0755 ${WORKDIR}/usbgadget-setup.sh ${D}${INIT_D_DIR}/usbgadget-setup.sh
    install -m 0644 ${WORKDIR}/udhcpd.conf  ${D}${datadir}/usbgadget/udhcpd.conf
    install -m 0755 ${WORKDIR}/usbgadget.sh    ${D}${datadir}/usbgadget/usbgadget.sh

}
