from pynq import register_ip_driver
from pynq import UnknownIP


class AxiGPIO(UnknownIP):

    class Input:

        def __init__(self, parent, start, stop):
            self._parent = parent
            self._start = start
            self._stop = stop
            self._mask = (1 << (stop - start)) - 1

        def read(self):
            return (self._parent.read() >> self._start) & self._mask

    class Output:

        def __init__(self, parent, start, stop):
            self._parent = parent
            self._start = start
            self._stop = stop
            self._mask = (1 << (stop - start)) - 1

        def write(self, val):
            if val > self._mask:
                raise ValueError(
                    f"{val} to large for {self._stop - self._start} bits")
            self._parent.write(val << self._start, self._mask << self._start)

        def on(self):
            self.write(self._mask)

        def off(self):
            self.write(0)

        def toggle(self):
            self.write((~self._parent.val >> self._start) & self._mask)

    class InOut(Input, Output):

        def __init__(self, parent, start, stop):
            self._parent = parent
            self._start = start
            self._stop = stop
            self._mask = (1 << (stop - start)) - 1

    class Channel:

        def __init__(self, parent, channel):
            self._parent = parent
            self._channel = channel
            self.slicetype = AxiGPIO.InOut
            self.length = 32
            self.val = 0
            self.tri_mask = 0

        def __getitem__(self, idx):
            if isinstance(idx, slice):
                if idx.step is not None and idx.step != 1:
                    raise IndexError("Steps other than 1 not supported")
                return self.slicetype(self, idx.start, idx.stop)
            elif isinstance(idx, int):
                if idx >= self.length:
                    raise IndexError()
                return self.slicetype(self, idx, idx + 1)

        def __len__(self):
            return self.length

        def write(self, val, mask):
            self.val = (self.val & ~mask) | val
            self._parent.write(self._channel * 8, self.val)

        def read(self):
            return self._parent.read(self._channel * 8)

        def setlength(self, length):
            self.length = length

        def setdirection(self, direction):
            if direction not in [AxiGPIO.Input, AxiGPIO.Output, AxiGPIO.InOut]:
                raise ValueError(
                    "direction should be one of AxiGPIO.{Input,Output,InOut}")
            self.slicetype = direction

    def __init__(self, description):
        super().__init__(description)
        self._channels = [AxiGPIO.Channel(self, i) for i in range(2)]
        self.channel1 = self._channels[0]
        self.channel2 = self._channels[1]

    def setlength(self, length, channel=1):
        self._channels[channel - 1].length = length

    def setdirection(self, direction, channel=1):
        if direction not in [AxiGPIO.Input, AxiGPIO.Output, AxiGPIO.InOut]:
            raise ValueError(
                "direction should be one of AxiGPIO.{Input,Output,InOut}")
        self._channels[channel - 1].slicetype = direction

    def __getitem__(self, idx):
        return self.channel1[idx]


register_ip_driver('xilinx.com:ip:axi_gpio:2.0', AxiGPIO)
