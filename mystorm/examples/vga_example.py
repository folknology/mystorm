from amaranth import *

from ..boards.icelogicbus import *
from ..tiles.vga_tile import Pins
from ..core.vga import VGADriver, VGATestPattern, VGATiming, vga_timings
from ..core.pll import PLL


TILE = 1
vga_tile = "vga_tile"


class VGAExample(Elaboratable):
    def __init__(self,
                 timing: VGATiming,  # VGATiming class
                 xadjustf=0,  # adjust -3..3 if no picture
                 yadjustf=0):  # or to fine-tune f
        # Configuration
        self.timing = timing
        self.xadjustf = xadjustf
        self.yadjustf = yadjustf

    def elaborate(self, platform):
        m = Module()
        clk_in = platform.request(platform.default_clk, dir='-')[0]
        # Clock generator.
        m.domains.sync = cd_sync = ClockDomain("sync")
        m.d.comb += ClockSignal().eq(clk_in)
        # Create a Pll to generate the pixel clock
        m.submodules.pll = pll = PLL(freq_in_mhz=int(platform.default_clk_frequency / 1000000),
                                     freq_out_mhz=int(self.timing.pixel_freq / 1000000),
                                     domain_name="pixel")
        # Add the pixel clock domain to the module, and connect input clock
        m.domains.pixel = cd_pixel = pll.domain
        m.d.comb += pll.clk_pin.eq(clk_in)
        platform.add_clock_constraint(cd_pixel.clk, self.timing.pixel_freq)
        # Create VGA instance with chosen timings
        m.submodules.vga = vga = VGADriver(
            self.timing,
            bits_x=16,  # Play around with the sizes because sometimes
            bits_y=16  # a smaller/larger value will make it pass timing.
        )
        # Create test pattern
        m.submodules.pattern = pattern = VGATestPattern(vga)
        # enable the clock and test signal
        m.d.comb += vga.i_clk_en.eq(1)
        # Grab our VGA Tile resource
        av_tile = platform.request(vga_tile)
        # Hook it up to the VGA instance
        m.d.comb += [
            av_tile.red.eq(vga.o_vga_r[5:]),
            av_tile.green.eq(vga.o_vga_g[4:]),
            av_tile.blue.eq(vga.o_vga_b[5:]),
            av_tile.hs.eq(vga.o_vga_hsync),
            av_tile.vs.eq(vga.o_vga_vsync)
        ]

        return m


def synth():
    platform = IceLogicBusPlatform()
    platform.add_tile(vga_tile, TILE, Pins)
    platform.build(VGAExample(timing=vga_timings['1024x768@60Hz']), do_program=True)



if __name__ == "__main__":
    synth()

