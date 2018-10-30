import os

from pynq.ps import CPU_ARCH_IS_SUPPORTED, CPU_ARCH, ZYNQ_ARCH, ZU_ARCH


# Overlay constants
PYNQ_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PL_SERVER_FILE = os.path.join(PYNQ_PATH, '.log')
PL_SERVER_URI = "PYRO:pl.server@./u:" + PL_SERVER_FILE

def get_tcl_name(bitfile_name):
    """This method returns the name of the tcl file.

    For example, the input "/home/xilinx/pynq/overlays/base/base.bit" will
    lead to the result "/home/xilinx/pynq/overlays/base/base.tcl".

    Parameters
    ----------
    bitfile_name : str
        The absolute path of the .bit file.

    Returns
    -------
    str
        The absolute path of the .tcl file.

    """
    return os.path.splitext(bitfile_name)[0] + '.tcl'


def get_hwh_name(bitfile_name):
    """This method returns the name of the hwh file.

    For example, the input "/home/xilinx/pynq/overlays/base/base.bit" will
    lead to the result "/home/xilinx/pynq/overlays/base/base.hwh".

    Parameters
    ----------
    bitfile_name : str
        The absolute path of the .bit file.

    Returns
    -------
    str
        The absolute path of the .hwh file.

    """
    return os.path.splitext(bitfile_name)[0] + '.hwh'


def locate_overlay():
    """Locate an overlay in the overlays folder.

    Return the base overlay by default; if not found, return the first overlay
    found.

    Returns
    -------
    str
        The name of the first overlay found.

    """
    if os.path.isdir(os.path.join(PYNQ_PATH, 'overlays', 'base')):
        return 'base'
    for i in os.listdir(os.path.join(PYNQ_PATH, 'overlays')):
        if os.path.isdir(os.path.join(PYNQ_PATH, 'overlays', i)) and \
                not i.startswith('_'):
            return i
    return ''


OVERLAY_BOOT = locate_overlay()
BS_BOOT = os.path.join(PYNQ_PATH, 'overlays',
                       OVERLAY_BOOT, OVERLAY_BOOT + '.bit')
TCL_BOOT = get_tcl_name(BS_BOOT)
HWH_BOOT = get_hwh_name(BS_BOOT)

