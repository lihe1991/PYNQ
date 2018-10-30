import re
import warnings
import abc
from xml.etree import ElementTree
from copy import deepcopy
from pynq.ps import CPU_ARCH_IS_SUPPORTED, CPU_ARCH, ZYNQ_ARCH, ZU_ARCH


class _HWHABC(metaclass=abc.ABCMeta):
    """Helper Class to extract information from a HWH configuration file

    Note
    ----
    This class requires the absolute path of the '.hwh' file.

    Attributes
    ----------
    ip_dict : dict
        All the addressable IPs from PS7. Key is the name of the IP; value is
        a dictionary mapping the physical address, address range, IP type,
        configuration dictionary, the state associated with that IP, any
        interrupts and GPIO pins attached to the IP and the full path to the
        IP in the block design:
        {str: {'phys_addr' : int, 'addr_range' : int,\
               'type' : str, 'config' : dict, 'state' : str,\
               'interrupts' : dict, 'gpio' : dict, 'fullpath' : str}}.
    gpio_dict : dict
        All the GPIO pins controlled by PS7. Key is the name of the GPIO pin;
        value is a dictionary mapping user index (starting from 0),
        the state associated with that GPIO pin and the pins in block diagram
        attached to the GPIO:
        {str: {'index' : int, 'state' : str, 'pins' : [str]}}.
    interrupt_controllers : dict
        All AXI interrupt controllers in the system attached to
        a PS7 interrupt line. Key is the name of the controller;
        value is a dictionary mapping parent interrupt controller and the
        line index of this interrupt:
        {str: {'parent': str, 'index' : int}}.
        The PS7 is the root of the hierarchy and is unnamed.
    interrupt_pins : dict
        All pins in the design attached to an interrupt controller.
        Key is the name of the pin; value is a dictionary
        mapping the interrupt controller and the line index used:
        {str: {'controller' : str, 'index' : int}}.
    hierarchy_dict : dict
        All of the hierarchies in the block design containing addressable IP.
        The keys are the hiearachies and the values are dictionaries
        containing the IP and sub-hierarchies contained in the hierarchy and
        and GPIO and interrupts attached to the hierarchy. The keys in
        dictionaries are relative to the hierarchy and the ip dict only
        contains immediately contained IP - not those in sub-hierarchies.
        {str: {'ip': dict, 'hierarchies': dict, 'interrupts': dict,\
               'gpio': dict, 'fullpath': str}}
    clock_dict : dict
        All the PL clocks that can be controlled by the PS. Key is the index
        of the clock (e.g., 0 for `fclk0`); value is a dictionary mapping the
        divisor values and the enable flag (1 for enabled, and
        0 for disabled):
        {index: {'divisor0' : int, 'divisor1' : int, 'enable' : int}}

    """
    family_ps = ""
    family_irq = ""
    family_gpio = ""

    def __init__(self, hwh_name):
        """Returns a map built from the supplied hwh file

        Parameters
        ---------
        hwh_name : str
            The hwh filename to parse.

        Note
        ----
        If this method is called on an unsupported architecture it will warn
        and return without initialization

        """
        tree = ElementTree.parse(hwh_name)
        self.root = tree.getroot()
        self.intc_names = []
        self.interrupt_controllers = {}
        self.concat_cells = {}
        self.nets = {}
        self.pins = {}
        self.hierarchy_dict = {}
        self.interrupt_pins = {}
        self.ps_name = ""
        self.ip_dict = {}
        self.gpio_dict = {}
        self.clock_dict = {}
        self.instance2attr = {i.get('INSTANCE'): (
            i.get('FULLNAME').lstrip('/'),
            i.get('VLNV')) for i in self.root.iter("MODULE")}

        for mod in self.root.iter("MODULE"):
            mod_type = mod.get('MODTYPE')
            full_path = mod.get('FULLNAME').lstrip('/')
            if mod_type == self.family_ps:
                self.ps_name = mod.get('INSTANCE')
                self.init_clk_dict(mod)
                self.init_ip_dict(mod)
            elif mod_type == 'xlconcat':
                self.concat_cells[full_path] = mod.find(
                    ".//*[@NAME='NUM_PORTS']").get('VALUE')
            elif mod_type == 'axi_intc':
                self.intc_names.append(full_path)

            self.match_nets(mod, full_path)

        self.match_pins()
        self.add_gpio()
        self.init_interrupts()
        self.init_hierachy_dict()
        self.assign_interrupts_gpio()

    def init_ip_dict(self, mod):
        """Get the IP address blocks exposed at the top level block design.

        This method will only work on those addressable IPs.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.

        """
        for i in mod.iter("MEMRANGE"):
            if i.get('INSTANCE') in self.instance2attr:
                full_name, vlnv = self.instance2attr[i.get('INSTANCE')]
                self.ip_dict[full_name] = {}
                self.ip_dict[full_name]['fullpath'] = full_name
                self.ip_dict[full_name]['type'] = vlnv
                self.ip_dict[full_name]['state'] = None
                high_addr = int(i.get('HIGHVALUE'), 16)
                base_addr = int(i.get('BASEVALUE'), 16)
                addr_range = high_addr - base_addr + 1
                self.ip_dict[full_name]['addr_range'] = addr_range
                self.ip_dict[full_name]['phys_addr'] = base_addr

                self.ip_dict[full_name]['gpio'] = {}
                self.ip_dict[full_name]['interrupts'] = {}

    def match_nets(self, mod, full_path):
        """Matching all the nets from the HWH file.

        This method will arrange all the nets. Note that since we
        have a signal name for each net, we will use that as the key to index
        the nets dictionary.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.
        full_path : str
            The full path of the given module.

        """
        for blk in mod.iter("PORT"):
            ports = [full_path + '/' + blk.get('NAME')]
            signame = blk.get('SIGNAME')
            if signame in self.nets:
                self.nets[signame] |= set(ports)
            else:
                self.nets[signame] = set(ports)

    def match_pins(self):
        """Matching all the pins from the HWH file.

        This method will arrange all the pins. The pins dictionary stores
        the reverse mapping, which maps each pin to the name of the
        connected signal.

        """
        for signame, pin_set in self.nets.items():
            for p in pin_set:
                self.pins[p] = signame

    def init_interrupts(self):
        """Prepare the interrupt dictionaries.

        This method will prepare both the interrupt controller dictionary
        and the interrupt pins dictionary.

        """
        if self.ps_name + "/" + self.family_irq in self.pins:
            ps_irq_net = self.pins[
                self.ps_name + "/" + self.family_irq]
            self._add_interrupt_pins(ps_irq_net, "", 0)

    def _add_interrupt_pins(self, net, parent, offset):
        net_pins = self.nets[net]
        for p in net_pins:
            m = re.match('(.*)/dout', p)
            if m is not None:
                name = m.group(1)
                if name in self.concat_cells:
                    return self._add_concat_pins(name, parent, offset)
            m = re.match('(.*)/irq', p)
            if m is not None:
                name = m.group(1)
                if name in self.intc_names:
                    self._add_interrupt_pins(
                        self.pins[name + "/intr"], name, 0)
                    self.interrupt_controllers[name] = {'parent': parent,
                                                        'index': offset}
                    return offset + 1
        for p in net_pins:
            self.interrupt_pins[p] = {'controller': parent,
                                      'index': offset,
                                      'fullpath': p}
        return offset + 1

    def _add_concat_pins(self, name, parent, offset):
        num_ports = int(self.concat_cells[name])
        for i in range(num_ports):
            net = self.pins[name + "/In" + str(i)]
            offset = self._add_interrupt_pins(net, parent, offset)
        return offset

    def add_gpio(self):
        """Get the PS GPIO blocks exposed at the top level block design.

        """
        for it in self.root.iter('MODULE'):
            mod = it.find(
                ".//PORTS//*[@DIR='I']"
                "//*[@INSTANCE='{0}'][@PORT='{1}']../../../..".format(
                    self.ps_name, self.family_gpio))
            if mod is not None:
                din = int(mod.find(".//*[@NAME='DIN_FROM']").get('VALUE'))
                for p in mod.iter("PORT"):
                    if p.get('DIR') == 'O':
                        signame = p.get('SIGNAME')
                        net_set = self.nets[signame]
                        gpio_name = ''
                        for i in net_set:
                            m = re.match('(.*)/Dout', i)
                            if m is not None:
                                gpio_name = m.group(1)
                                break
                        if gpio_name == '':
                            raise ValueError("Cannot get GPIO name */Dout.")
                        self.gpio_dict[gpio_name] = {}
                        self.gpio_dict[gpio_name]['state'] = None
                        self.gpio_dict[gpio_name]['pins'] = net_set
                        self.gpio_dict[gpio_name]['index'] = din

    def init_hierachy_dict(self):
        """Initialize the hierachical dictionary.

        """
        hierarchies = {k.rpartition('/')[0] for k in self.ip_dict.keys()
                       if k.count('/') > 0}
        for hier in hierarchies:
            self.hierarchy_dict[hier] = {
                'ip': dict(),
                'hierarchies': dict(),
                'interrupts': dict(),
                'gpio': dict(),
                'fullpath': hier,
            }
        for name, val in self.ip_dict.items():
            hier, _, ip = name.rpartition('/')
            if hier:
                self.hierarchy_dict[hier]['ip'][ip] = val

        for name, val in self.hierarchy_dict.items():
            hier, _, subhier = name.rpartition('/')
            if hier:
                self.hierarchy_dict[hier]['hierarchies'][subhier] = val

    def assign_interrupts_gpio(self):
        """Assign interrupts and gpio entries to the dictionaries.

        """
        for interrupt, val in self.interrupt_pins.items():
            block, _, pin = interrupt.rpartition('/')
            if block in self.ip_dict:
                self.ip_dict[block]['interrupts'][pin] = val
            if block in self.hierarchy_dict:
                self.hierarchy_dict[block]['interrupts'][pin] = val

        for gpio in self.gpio_dict.values():
            for connection in gpio['pins']:
                ip, _, pin = connection.rpartition('/')
                if ip in self.ip_dict:
                    self.ip_dict[ip]['gpio'][pin] = gpio
                elif ip in self.hierarchy_dict:
                    self.hierarchy_dict[ip]['gpio'][pin] = gpio

    def init_clk_dict(self, mod):
        """Initialize the clock dictionary.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.

        """
        for i in range(4):
            self.clock_dict[i] = dict()
            self.clock_dict[i]['enable'] = self.find_clock_enable(mod, i)
            for j in range(2):
                self.clock_dict[i]['divisor{}'.format(j)] = \
                    self.find_clock_divisor(mod, i, j)

    def find_clock_divisor(self, mod, clk_id, div_id):
        """Return the clock divisor for the given clock ID.

        Place holder for child class to implement.

        """
        pass

    def find_clock_enable(self, mod, clk_id):
        """Return the clock enable for the given clock ID.

        Place holder for child class to implement.

        """
        pass


class _HWHZynq(_HWHABC):
    """Helper Class to extract information from a HWH configuration file

    This class works for the Zynq devices.

    """
    family_ps = "processing_system7"
    family_irq = "IRQ_F2P"
    family_gpio = "GPIO_O"

    def find_clock_divisor(self, mod, clk_id, div_id):
        """Return the clock divisor for the given clock ID.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.
        clk_id : int
            The ID of the PL clock, can be 0 - 3.
        div_id : int
            The ID of the clock divisor, can be 0 - 1.

        Returns
        -------
        int
            The clock divisor value in decimal.

        """
        clk_odiv = 'PCW_FCLK{0}_PERIPHERAL_DIVISOR{1}'.format(clk_id, div_id)
        return int(mod.find(
            "./PARAMETERS/*[@NAME='{0}']".format(clk_odiv)).get('VALUE'))

    def find_clock_enable(self, mod, clk_id):
        """Return the clock enable for the given clock ID.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.
        clk_id : int
            The ID of the PL clock, can be 0 - 3.

        Returns
        -------
        int
            The clock enable value in decimal (1 means enabled).

        """
        clk_enable = 'PCW_FPGA_FCLK{0}_ENABLE'.format(clk_id)
        return int(mod.find(
            "./PARAMETERS/*[@NAME='{0}']".format(clk_enable)).get('VALUE'))


class _HWHUltrascale(_HWHABC):
    """Helper Class to extract information from a HWH configuration file

    This class works for the Zynq Ultrascale devices.

    """
    family_ps = "zynq_ultra_ps_e"
    family_irq = "pl_ps_irq0"
    family_gpio = "emio_gpio_o"

    def find_clock_divisor(self, mod, clk_id, div_id):
        """Return the clock divisor for the given clock ID.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.
        clk_id : int
            The ID of the PL clock, can be 0 - 3.
        div_id : int
            The ID of the clock divisor, can be 0 - 1.

        Returns
        -------
        int
            The clock divisor value in decimal.

        """
        clk_odiv = 'PSU__CRL_APB__PL{0}_REF_CTRL__DIVISOR{1}'.format(
            clk_id, div_id)
        return int(mod.find(
            "./PARAMETERS/*[@NAME='{0}']".format(clk_odiv)).get('VALUE'))

    def find_clock_enable(self, mod, clk_id):
        """Return the clock enable for the given clock ID.

        Parameters
        ----------
        mod : Element
            The current XML element under parsing.
        clk_id : int
            The ID of the PL clock, can be 0 - 3.

        Returns
        -------
        int
            The clock enable value in decimal (1 means enabled).

        """
        clk_enable = 'PSU__FPGA_PL{0}_ENABLE'.format(clk_id)
        return int(mod.find(
            "./PARAMETERS/*[@NAME='{0}']".format(clk_enable)).get('VALUE'))


if CPU_ARCH == ZU_ARCH:
    HWH = _HWHUltrascale
elif CPU_ARCH == ZYNQ_ARCH:
    HWH = _HWHZynq
else:
    HWH = _HWHABC
    warnings.warn("PYNQ does not support the CPU Architecture: {}"
                  .format(CPU_ARCH), ResourceWarning)

