import os
import subprocess
import serial
import serial.tools.list_ports as lp

from amaranth.build import *
from amaranth_boards.resources import *
from amaranth.vendor.lattice_ice40 import LatticeICE40Platform

__all__ = ["IceLogicBusPlatform"]

#            Tile 1                    Tile 3
#         *-------------------------------------*
#         |                                     |
#         |                                     |
# Blade 1 |                                     | Blade 2
#         |                                     |
#         |                                     |
# USB     |            BlackiceNxt              | Blade 2
#         |                                     |
#         |                                     |
# SD/MMC  |                                     | Blade 3
#         |                                     |
#         |                                     |
#         *-------------------------------------*
#            Tile 2                    Tile 4

class PortNotFound(Exception):
    pass


# Pinout definitions
INT =" J11" #also ILB Blue LED pin
RX = " K7"
TX = " L7"
SPI = " K9 J9 L10 L7" #si,so, sck,ss

QSPIDATA = " J9 K9 K6 L5"
QSPICK = " L10"
QSPICS = " K10"
QSPIDR = " J11"

HYPERBUSDATA = " K3 K4 L1 K5 J3 L3 L4 J5"
HYPERBUSCLK = " L2"
HYPERBUSRD = " J4"
HYPERBUSCS = " J2 K2" # HyperRam,Flash
HYPERFLASHINT = " H9"

TILE1 = " F1 F2 F4 F3 G1 G2 G3 H3 H1 H2 J1 K1" #C
TILE2 = " K11 H10 J10 G8 H11 G10 D9 E11 G9 G11 F10 F9" #G
TILE3 = " B1 B2 C4 C3 C2 C1 E1 D1 D2 D3 E2 E3" #B
TILE4 = " A9 C8 A8 C7 A6 A5 A2 A3 F11 E9 E10 E8" #F

BLADE1 = " K7 L7 J7 H7 L8 J8"
BLADE2 = " B3 A1 A4 B4 B5 D5"
BLADE3 = " D7 B6 A7 B8 B9 C9"
BLADE4 = " D10 D11 C11 B11 A11 A10"

PMOD1A = " F1 F4 G1 G3 - -"
PMOD1B = " F2 F3 G2 H3 - -"
PMOD2A = " H1 J1 B1 C4 - -"
PMOD2B = " H2 K1 B2 C3 - -"
PMOD3A = " C2 E1 D2 E2 - -"
PMOD3B = " C1 D1 D3 E3 - -"

PMOD4A = " A9 A8 A6 A2 - -"
PMOD4B = " C8 C7 A5 A3 - -"
PMOD5A = " F11 E10 K11 J10 - -"
PMOD5B = " E9 E8 H10 G8 - -"
PMOD6A = " H11 D9 G9 F10 - -"
PMOD6B = " G10 E11 G11 F9 - -"

# USER = " J11 B6 D7 B7"
# SUPER = " B4 A4 A1 B3 _ _ _ _"
GENPINS = " - - - - - - - -"
# QSPIE = " J8 H7 K7 L8 H9 L7 J7" # qdo,qd1,qd2,qd3,qck,qss,qdr
# TILE2 = " D10 D11 B11 C11 A10 A11 C9 B9 A7 B8 D5 B5"

MEZZA = " L1 J3 L2 K3 L3 J4 K4 L4 J5 K5 K6 - - - - - - - - - - -" # Rx,Tx, DQ2,DQ4,DQK,DQ0,DQ5,DQR,DQ1,DQ6,DQ7,DQ3,DS0
MEZZB = " L10 - J9 K9 - - - - - - - - - - - - - - - - -"

# IceLogicDeck : https://github.com/folknology/IceLogicDeck
class IceLogicBusPlatform(LatticeICE40Platform):
    upload_port = None
    device = "iCE40HX4K"
    package = "BG121"
    default_clk = "clk25"
    resources = [
        Resource("clk25", 0, Pins("B7", dir="i"),
                 Clock(25e6), Attrs(GLOBAL=True, IO_STANDARD="SB_LVCMOS")
                 ),
        # led
        Resource("led", 0, Pins(INT, dir="o", invert=True),
                 Attrs(IO_STANDARD="SB_LVCMOS")
                 ),
        Resource("int", 0, Pins(INT, dir="o", invert=True),
                 Attrs(IO_STANDARD="SB_LVCMOS")
                 ),
        Resource("tx", 0, Pins(TX, dir="o"),
                 Attrs(IO_STANDARD="SB_LVCMOS")
                 ),
        Resource("rx", 0, Pins(RX, dir="o"),
                 Attrs(IO_STANDARD="SB_LVCMOS")
                 ),
        # SPI
        # Resource("sck", 0, Pins("L10", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # Resource("copi", 0, Pins("J9", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # Resource("cs_n", 0, Pins("L7", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # Resource("cipo", 0, Pins("K9", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # QSPIE
        Resource("qspi", 0,
                 Subsignal("data", Pins(QSPIDATA, dir="io")),
                 Subsignal("clk", Pins(QSPICK, dir="i")),
                 Subsignal("cs", Pins(QSPICS, dir="i")),
                 Attrs(IO_STANDARD="3.3-V LVTTL")),
        # Old QSPI resource depreciated
        Resource("qd0", 0, Pins("J9", dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd1", 0, Pins("K9", dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd2", 0, Pins("K6",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd3", 0, Pins("L5",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qck", 0, Pins("L10", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qss", 0, Pins("K10", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # Hyperbus
        Resource("hyperbus", 0,
                 Subsignal("data", Pins(HYPERBUSDATA, dir="io")),
                 Subsignal("clk", Pins(HYPERBUSCLK, dir="o")),
                 Subsignal("rd", Pins(HYPERBUSRD, dir="io")),
                 Subsignal("cs", Pins(HYPERBUSCS, dir="o")),
                 Subsignal("int", Pins(HYPERFLASHINT, dir="i")),
                 Attrs(IO_STANDARD="3.3-V LVTTL")),
        # Uart
        UARTResource(0,
                     rx="K7", tx="L7",
                     attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1),
                     role="dce"
                     ),
        # *SPIFlashResources(0,
        #                    cs_n="L7", clk="L10", copi="J9", cipo="K9",
        #                    attrs=Attrs(IO_STANDARD="SB_LVCMOS")
        #                    )
        #Hyperram ?
    ]
    connectors  = [
        # Tile connectors
        Connector("tile", 1, TILE1 + GENPINS),  #
        Connector("tile", 2, TILE2 + GENPINS),  #
        Connector("tile", 3, TILE3 + GENPINS),  #
        Connector("tile", 4, TILE4 + GENPINS),  #
        # Micro Blade connectores
        Connector("blade", 1, BLADE1),
        Connector("blade", 2, BLADE2),
        Connector("blade", 3, BLADE3),
        Connector("blade", 4, BLADE4),
        # Mezzanine Connectors
        Connector("mez", 0, MEZZA),  #
        Connector("mez", 1, MEZZB),  #

        Connector("pmod", 0, PMOD1A + PMOD1B),  # PMOD1/2
        Connector("pmod", 1, PMOD2A + PMOD2B),  # PMOD3/4
        Connector("pmod", 2, PMOD3A + PMOD3B),  # PMOD5/6
        Connector("pmod", 3, PMOD4A + PMOD4B),  # PMOD7/8
        Connector("pmod", 4, PMOD5A + PMOD5B),  # PMOD9/10
        Connector("pmod", 5, PMOD6A + PMOD6B),  # PMOD11/12
    ]

    def add_blade(self, name, blade, pins, invert=False):
        if len(pins) > 1:
            signals = [
            Subsignal(signal,
                    Pins(pin, dir=dir, conn=("blade", blade), invert=invert),
                    Attrs(IO_STANDARD="SB_LVCMOS")
                    ) for pin,(signal,dir) in pins.items()
            ]
            resources = [Resource(name, 0, *signals)]
        else :
            (_pin, (signal,dir)) = pins.popitem()
            resources =  [Resource(name, 0,
                Subsignal(signal,
                          Pins("1 2 3 4 5 6", dir=dir, conn=("blade", blade), invert=invert),
                          Attrs(IO_STANDARD="SB_LVCMOS")
                          )
            )]

        self.add_resources(resources)

    def add_tile(self, name, tile, pins, invert=False):
        if len(pins) > 1:
            signals = [
            Subsignal(signal,
                    Pins(pin, dir=dir, conn=("tile", tile), invert=invert),
                    Attrs(IO_STANDARD="SB_LVCMOS")
                    ) for pin,(signal,dir) in pins.items()
            ]
            resources = [Resource(name, 0, *signals)]
        else :
            (_pin, (signal,dir)) = pins.popitem()
            resources =  [Resource(name, 0,
                Subsignal(signal,
                          Pins("1 2 3 4 5 6 7 8 9 10 11 12", dir=dir, conn=("tile", tile), invert=invert),
                          Attrs(IO_STANDARD="SB_LVCMOS")
                          )
            )]

        self.add_resources(resources)
    
    def add_pmod(self, name, pmod, pins, invert=False):
        if len(pins) > 1:
            signals = [
            Subsignal(signal,
                    Pins(pin, dir=dir, conn=("pmod", pmod), invert=invert),
                    Attrs(IO_STANDARD="SB_LVCMOS")
                    ) for pin,(signal,dir) in pins.items()
            ]
            resources = [Resource(name, 0, *signals)]
        else :
            (_pin, (signal,dir)) = pins.popitem()
            resources =  [Resource(name, 0,
                Subsignal(signal,
                          Pins("1 2 3 4 7 8 9 10", dir=dir, conn=("pmod", pmod), invert=invert),
                          Attrs(IO_STANDARD="SB_LVCMOS")
                          )
            )]

        self.add_resources(resources)
        

    def get_port(self):
        for p in lp.comports():
            if p.vid == 5824:
                self.upload_port = p

    def toolchain_program(self, products, name, **kwargs):
        if self.upload_port is None:
            self.get_port()
            if self.upload_port is None:
                raise PortNotFound("'{}' could not find a suitable device for upload port, cannot upload"
                                          .format(type(self).__name__))
                # print("could not find a suitable device for upload port, cannot upload")
                # return
            else:
                print("Found device for uploading: ", self.upload_port.product + ' as device ' + self.upload_port.device)

        print("Uploading ", self.upload_port.product + ' as device ' + self.upload_port.device)
        with serial.Serial(self.upload_port.device) as ser:
            with products.extract("{}.bin".format(name)) as bitstream_filename:
                with open(bitstream_filename, 'rb') as f:
                    ser.write(f.read())
        # device = os.environ.get("DEVICE", p.device) # "/dev/ttyACM2"
        # with products.extract("{}.bin".format(name)) as bitstream_filename:
        #     subprocess.check_call(["cp", bitstream_filename, device])

    # def upload(self port=None):
    # if port is None:
    #     for p in lp():
    #         if p.vid is 5824:
    #             ser = serial.Serial(p.device)
    #             with open(products.extract("{}.bin".format(name))) as f:
    #                 ser.write(f.read())

    def get_upload_port(self):
        if self.upload_port is None:
            self.get_port()
            if self.upload_port is None:
                print("could not find a suitable device for upload port, cannot upload")
                return
            else:
                print("Found device for uploading: ", self.upload_port.product + ' as device ' + self.upload_port.device)

    def bus_send(self, bytes2send):
        self.get_upload_port()
        with serial.Serial(self.upload_port.device) as ser:
            ser.write(bytes2send)

    def bus_fetch(self, comad, count):
        self.get_upload_port()
        with serial.Serial(self.upload_port.device) as ser:
            ser.write(comad + count.to_bytes(4, "big"))
            return ser.read(count)

#bus_send(bytearray(b'\x00\xff'))

if __name__ == "__main__":
    #from .test.blinky import *
    from amaranth_boards.test.blinky import *
    IceLogicBusPlatform().build(Blinky(), do_program=True)
