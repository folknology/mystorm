from amaranth import *
from amaranth.build import *

from ..boards.icelogicbus import *

BLADE = 1
leds = "leds6"

class LedBlade(Elaboratable):

    def elaborate(self, platform):
        leds6 = Signal(6, reset = 0b1111)
        leds6 = Cat([l for l in platform.request(leds)])
        timer = Signal(23)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        with m.If(timer[-1]):
            m.d.sync += leds6.eq(Cat(leds6[1:6], ~leds6[0]))

        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.add_blade(leds, BLADE, {"1":("sig","o")})
    platform.build(LedBlade(), do_program=True)

if __name__ == "__main__":
    synth()
