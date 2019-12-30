#=========================================================================
# PicoRV32_test.py
#=========================================================================
# PicoRV32 processor tests.
#
# Author : Peitian Pan
# Date   : Dec 30, 2019

from pymtl3 import *
from pymtl3.passes.backends.sverilog import ImportPass

from ..PicoRV32 import PicoRV32

class SimplePicoRV32Memory( Component ):
  def construct( s ):
    s.valid = InPort( Bits1 )
    s.ready = OutPort( Bits1 )
    s.instr = InPort( Bits1 )

    s.addr = InPort( Bits32 )
    s.wdata = InPort( Bits32 )
    s.rdata = OutPort( Bits32 )
    s.wstrb = InPort( Bits4 )

    s.memory = [ Bits32(0) for _ in range(256) ]

    s.memory[0] = Bits32(0x3fc00093); #       li      x1,1020
    s.memory[1] = Bits32(0x0000a023); #       sw      x0,0(x1)
    s.memory[2] = Bits32(0x0000a103); # loop: lw      x2,0(x1)
    s.memory[3] = Bits32(0x00110113); #       addi    x2,x2,1
    s.memory[4] = Bits32(0x0020a023); #       sw      x2,0(x1)
    s.memory[5] = Bits32(0xff5ff06f); #       j       <loop>

    @s.update_ff
    def upblk_mem():
      s.ready <<= Bits1(0)
      if s.addr < Bits32(1024):
        s.ready <<= Bits1(1)
        s.rdata <<= s.memory[s.addr >> 2]
        if s.wstrb[0]:
          # s.memory[s.addr >> 2][ 0: 8] <<= s.wdata[ 0: 8]
          s.memory[s.addr >> 2][ 0: 8] = s.wdata[ 0: 8]
        if s.wstrb[1]:
          # s.memory[s.addr >> 2][ 8:16] <<= s.wdata[ 8:16]
          s.memory[s.addr >> 2][ 8:16] = s.wdata[ 8:16]
        if s.wstrb[2]:
          # s.memory[s.addr >> 2][16:24] <<= s.wdata[16:24]
          s.memory[s.addr >> 2][16:24] = s.wdata[16:24]
        if s.wstrb[3]:
          # s.memory[s.addr >> 2][24:32] <<= s.wdata[24:32]
          s.memory[s.addr >> 2][24:32] = s.wdata[24:32]

    @s.update_ff
    def upblk_print():
      if s.valid and s.ready:
        if s.instr:
          print('ifetch at {}: {}'.format(s.addr, s.rdata))
        elif s.wstrb:
          print('write at {}: {} (wstrb={})'.format(s.addr, s.wdata, s.wstrb))
        else:
          print('read at {}: {}'.format(s.addr, s.rdata))

class TestHarness( Component ):
  def construct( s, MemoryComponent ):
    s.dut = PicoRV32()
    s.mem = MemoryComponent()

    s.dut.resetn //= lambda: not s.reset
    s.dut.mem_valid //= s.mem.valid
    s.dut.mem_ready //= s.mem.ready
    s.dut.mem_instr //= s.mem.instr
    s.dut.mem_addr //= s.mem.addr
    s.dut.mem_wdata //= s.mem.wdata
    s.dut.mem_rdata //= s.mem.rdata
    s.dut.mem_wstrb //= s.mem.wstrb

    # Unused ports
    s.dut.pcpi_wr //= Bits1(0)
    s.dut.pcpi_rd //= Bits32(0)
    s.dut.pcpi_wait //= Bits1(0)
    s.dut.pcpi_ready //= Bits1(0)
    s.dut.irq //= Bits32(0)

# def test_import():
#   m = PicoRV32()
#   m.elaborate()
#   m = ImportPass()( m )

def test_simple():
  th = TestHarness( SimplePicoRV32Memory )
  th.elaborate()
  th.apply( ImportPass() )
  th.apply( SimulationPass() )

  T, maxT = 0, 200

  th.sim_reset()
  while T < maxT:
    th.tick()
