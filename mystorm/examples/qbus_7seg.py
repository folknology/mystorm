from amaranth import *
from amaranth.build import *

from ..boards.icelogicbus import *

from ..tiles.seven_seg_tile import Pins
from ..core.pll import PLL

from ..core.qspimem import QspiMem
from ..tiles.seven_seg_tile import SevenSegmentTile

BLADE = 1
TILE = 3
PMOD = 5
leds = "leds6"
segtile = "seven_seg_tile"

class Qbus7Seg(Elaboratable):
    def elaborate(self, platform):
        # Get pins
        qspi = platform.request("qspi")
        leds6 = platform.request("leds6")
        led = platform.request("led")

        m = Module()

        # Clock generator.
        clk_freq = 1e8
        clk_in = platform.request(platform.default_clk)
        # Create a Pll for 100Mhz clock
        m.submodules.pll = pll = PLL(freq_in_mhz=int(platform.default_clk_frequency / 1e6),
                                     freq_out_mhz=int(clk_freq / 1e6),
                                     domain_name="sync")
        # Set the sync domain to the pll domain
        m.domains.sync = cd_sync = pll.domain
        m.d.comb += pll.clk_pin.eq(clk_in)
        platform.add_clock_constraint(cd_sync.clk, clk_freq)

        # Add QspiMem submodule
        m.submodules.qspimem = qspimem = QspiMem()

        # Connect pins
        m.d.comb += [
            qspimem.qss.eq(qspi.cs),
            qspimem.qck.eq(qspi.clk),
            qspimem.qd_i.eq(qspi.data.i),
            qspi.data.o.eq(qspimem.qd_o),
            qspi.data.oe.eq(qspimem.qd_oe)
        ]

        # Add 7-segment display tile controller
        m.submodules.seven = seven = SevenSegmentTile()
        display = Signal(12)

        # Get pins
        seg_pins = platform.request(segtile)
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d,
                     seg_pins.e, seg_pins.f, seg_pins.g])

        # Connect pins and display value
        m.d.comb += [
            leds7.eq(seven.leds),
            seg_pins.ca.eq(seven.ca),
            seven.val.eq(display)
        ]

        # Write to peripherals

        # 7-segment lower byte
        with m.If(qspimem.wr & (qspimem.addr == 0)):
            m.d.sync += display.eq(qspimem.dout)

        # 7-segment top nibble
        with m.If(qspimem.wr & (qspimem.addr == 1)):
            m.d.sync += display[8:].eq(qspimem.dout[:4])

        # Led blade and led
        with m.If(qspimem.wr & (qspimem.addr == 2)):
            m.d.sync += [
                leds6.eq(qspimem.dout[:6]),
                led.eq(qspimem.dout[7])
            ]

        return m


def synth():
    platform = IceLogicBusPlatform()
    platform.add_tile(segtile, TILE, Pins, invert=True)
    platform.add_blade(leds, BLADE, {"1":("sig","o")})
    platform.build(Qbus7Seg(), nextpnr_opts="--timing-allow-fail", do_program=True)
    # Send bus command
    addr = 0
    data = b'\x42\x06\x38' #0011,1000
    command = b'\x03' + addr.to_bytes(4, 'big') + len(data).to_bytes(4, 'big') + data
    print("Sending command: ", command)
    platform.bus_send(command)


if __name__ == "__main__":
    synth()