from amaranth import *
from amaranth.build import *

from ..boards.icelogicbus import *
from ..core.st7789 import *

BLADE = 3

oled = {"1":("oled_bl","o"),
        "2":("oled_resn","o"),
        "3":("oled_csn","o"),
        "4":("oled_clk","o"),
        "5":("oled_dc","o"),
        "6":("oled_mosi","o")}



class ST7789Test(Elaboratable):
    def elaborate(self, platform):
        # led = [platform.request("led", i) for i in range(4)]

        # LCD/OLED Pmod
        oled = platform.request("oled")
        oled_clk = oled.oled_clk
        oled_mosi = oled.oled_mosi
        oled_dc = oled.oled_dc
        oled_resn = oled.oled_resn
        oled_csn = oled.oled_csn
        oled_bl = oled.oled_bl

        st7789 = ST7789(reset_delay=100000, reset_period=100000)
        m = Module()
        m.submodules.st7789 = st7789

        x = Signal(8)
        y = Signal(8)
        # next_pixel = Signal()

        m.d.comb += [
            oled_clk.eq(st7789.spi_clk),
            oled_mosi.eq(st7789.spi_mosi),
            oled_dc.eq(st7789.spi_dc),
            oled_resn.eq(st7789.spi_resn),
            oled_csn.eq(st7789.spi_csn),
            oled_bl.eq(0), # For 7-pin version that backlight instead of csn
            # next_pixel.eq(st7789.next_pixel),
            x.eq(st7789.x),
            y.eq(st7789.y),
        ]

        # Draw chequered pattern
        with m.If(x[4] ^ y[4]):
            m.d.comb += st7789.color.eq(x[3:8] << 6)
        with m.Else():
            m.d.comb += st7789.color.eq(y[3:8] << 11)

        # m.d.comb += Cat([i.o for i in led]).eq(st7789.x)

        return m


if __name__ == "__main__":
    platform = IceLogicBusPlatform()
    platform.add_blade("oled",BLADE,oled)
    platform.build(ST7789Test(), do_program=True)