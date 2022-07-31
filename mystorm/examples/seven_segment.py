from amaranth import *
from amaranth.hdl.ast import Rose

from mystorm.boards.icelogicbus import *
from mystorm.tiles.seven_seg_tile import Pins
from mystorm.core.sevensegdecoder import SevenSegDecoder

TILE = 3
segtile = "seven_seg_tile"

class SevenSegExample(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.seven = seven = SevenSegDecoder()

        seg_pins = platform.request("seven_seg_tile")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d, seg_pins.e, seg_pins.f, seg_pins.g])
        timer = Signal(40)
        m.d.sync += timer.eq(timer + 1)

        m.d.comb += [
            leds7.eq(seven.leds)
        ]
        for i in range(3):
            m.d.comb += seg_pins.ca[i].eq(timer[17:19] == i)
            with m.If(seg_pins.ca[i]):
                m.d.comb += seven.val.eq(timer[((i - 3) * 4) - 5:((i - 3) * 4) - 1])

        return m


def synth():
    platform = IceLogicBusPlatform()
    platform.add_tile(segtile, TILE, Pins)
    platform.build(SevenSegExample(), do_program=True)

if __name__ == "__main__":
    synth()
