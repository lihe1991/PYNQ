from .constants import PYNQ_PATH
from .constants import PL_SERVER_FILE
from .constants import PL_SERVER_URI
from .constants import get_tcl_name
from .constants import get_hwh_name
from .parse_hwh import HWH
from .parse_tcl import TCL

def _connect_to_server():
    import Pyro4
    return Pyro4.Proxy(PL_SERVER_URI)

try:
    PL = _connect_to_server()

except:
    warnings.warn("Failed to connect to PL server, PL will be None")
    PL = None
