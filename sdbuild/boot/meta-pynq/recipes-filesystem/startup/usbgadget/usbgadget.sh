#!/bin/sh
# Script Adapted from http://irq5.io/2016/12/22/raspberry-pi-zero-as-multiple-usb-gadgets/

cd /sys/kernel/config/usb_gadget/
mkdir g && cd g
 
echo 0x1d6b > idVendor  # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB    # USB 2.0

echo 0xEF > bDeviceClass
echo 0x02 > bDeviceSubClass
echo 0x01 > bDeviceProtocol

mkdir -p strings/0x409
echo "0000" > strings/0x409/serialnumber
echo "Xilinx Inc."   > strings/0x409/manufacturer
echo "PYNQ-USB"   > strings/0x409/product

echo 1       > os_desc/use
echo 0xcd    > os_desc/b_vendor_code
echo MSFT100 > os_desc/qw_sign
 
mkdir -p functions/rndis.usb0  # network
 
echo RNDIS   > functions/rndis.usb0/os_desc/interface.rndis/compatible_id
echo 5162001 > functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id

mkdir -p configs/c.1
echo 250 > configs/c.1/MaxPower
ln -s configs/c.1 os_desc/
ln -s functions/rndis.usb0 configs/c.1/

udevadm settle -t 5 || :
ls /sys/class/udc/ > UDC

udhcpd /usr/share/usbgadget/udhcpd.conf
ifconfig usb0 192.168.3.1
