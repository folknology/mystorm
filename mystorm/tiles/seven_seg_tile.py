from typing import List

from amaranth import *
from amaranth.build import *

from ..core.sevensegdecoder import SevenSegDecoder

Pins = {"3 2 1":("ca","o"),
        "4":("g","o"),
        "5":("f","o"),
        "6":("a","o"),
        "7":("e","o"),
        "8":("b","o"),
        "9":("dp","o"),
        "10":("d","o"),
        "12":("c","o")}


class SevenSegmentTile(Elaboratable):
    def __init__(self):
        self.leds = Signal(7)
        self.ca   = Signal(3)
        self.val  = Signal(12)

    def elaborate(self, platform):
        m = Module()

        m.submodules.seven = seven = SevenSegDecoder()

        m.d.comb += self.leds.eq(seven.leds)

        timer = Signal(19)
        m.d.sync += timer.eq(timer + 1)

        for i in range(3):
            m.d.comb += self.ca[i].eq(timer[17:19] == i)

        with m.If(self.ca[2]):
            m.d.comb += seven.val.eq(self.val[8:])
        with m.If(self.ca[1]):
            m.d.comb += seven.val.eq(self.val[4:8])
        with m.If(self.ca[0]):
            m.d.comb += seven.val.eq(self.val[:4])

        return m

