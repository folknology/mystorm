from amaranth import *
from amaranth.build import *
from amaranth.hdl.ast import Rose

from mystorm.boards.icelogicbus import *

PMOD = 5

qspi_pmod = [
    Resource("qspi_test", 0,
             Subsignal("qss", Pins("10", dir="o", conn=("pmod", PMOD))),
             Subsignal("qck", Pins("9", dir="o", conn=("pmod", PMOD))),
             Subsignal("gnd", Pins("8", dir="o", conn=("pmod", PMOD))),
             Subsignal("qd", Pins("1 2 3 4", dir="o", conn=("pmod", PMOD))),
             Attrs(IO_STANDARD="SB_LVCMOS"))
]

class LogicPmodTest(Elaboratable):
    def elaborate(self, platform):

        m = Module()
        qspi = platform.request("qspi")
        qss = qspi.cs
        qck = qspi.clk
        qd_i = qspi.data.i
        qd_o = qspi.data.o
        qd_oe = qspi.data.oe
        qspi_test = platform.request("qspi_test")

        m.d.comb += [
            qspi_test.qss.eq(qss),
            qspi_test.qck.eq(qck),
            qspi_test.qd.eq(qd_i),
            qspi_test.gnd.eq(0)
        ]
        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.add_resources(qspi_pmod)
    platform.build(LogicPmodTest(), do_program=True)
    platform.bus_send(bytearray(b'\x03\x00\x01\x00\xFF\x00\x00\x00\x04\x42\x56\x21\x17'))

if __name__ == "__main__":
    platform = IceLogicBusPlatform()
    platform.add_resources(qspi_pmod)
    platform.build(LogicPmodTest(), do_program=True)
    platform.bus_send(bytearray(
        b'\x03\x00\x01\x00\xFF\x00\x00\x00\x10\x42\x21\x17\x42\x56\x21\x17\x42\x56\x21\x17\x42\x21\x17\x42\x21'))
    # result = platform.bus_fetch(bytearray(b'\x04\x00\x01\x00\xFF'), 10)
    # print(result)

