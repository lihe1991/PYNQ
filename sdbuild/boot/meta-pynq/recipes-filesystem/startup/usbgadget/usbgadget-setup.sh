#! /bin/sh

### BEGIN INIT INFO
# Provides: Networking via USB gadgets
# Required-Start:
# Required-Stop:
# Default-Start:S
# Default-Stop:
# Short-Description: Starts a network over USB gadgets
# Description:       This script runs a utility which will create a managed interface and runs
#                       a USB-gadget based network to a host
### END INIT INFO

DESC="usbgadet-setup.sh will start a network interface over USB gadgets"
USBGADGET="/usr/share/usbgadget/usbgadget.sh"
USBGADGET_PID_NAME="usbgadget-setup"

test -x "$USBGADGET" || exit 0

case "$1" in
  start)
    echo -n "Starting USB gadget"
    start-stop-daemon --start --quiet --background --make-pidfile --pidfile /var/run/$USBGADGET_PID_NAME.pid --exec $USBGADGET
    echo "."
    ;;
  stop)
    echo -n "Stopping USB gadget"
    start-stop-daemon --stop --quiet --pidfile /var/run/$USBGADGET_PID_NAME.pid
    ;;
  *)
    echo "Usage: /etc/init.d/usbgadget-setup.sh {start|stop}"
    exit 1
esac

exit 0

