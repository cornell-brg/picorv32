#=========================================================================
# PicoRV32_test.py
#=========================================================================
# PicoRV32 processor tests.
#
# Author : Peitian Pan
# Date   : Dec 30, 2019

from copy import copy

import sys
import pytest

from pymtl3 import *
from pymtl3.passes.backends.sverilog import ImportPass
from pymtl3.stdlib.fl import MemoryFL
from pymtl3.stdlib.rtl.enrdy_queues import PipeQueue1RTL

#***********************
# Import PyH2HP
#***********************

from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis import Phase

# Hypothesis
from proc.test.inst_random import inst_combined as inst_hypothesis

# CRT
from proc.test.inst_randint import multipick as inst_random

# IDT
from proc.test.inst_deepening import inst_deepening_gen

from proc.test.harness import assemble
from proc.test.harness import TestHarness as RefTestHarness
from proc.ProcFLGolden import ProcFL

from .elf import elf_reader
from ..PicoRV32 import PicoRV32

#-------------------------------------------------------------------------
# Global states
#-------------------------------------------------------------------------

# Use this to only perform import on the very first run
imported = False

# Number of tests to reach the result
nTests = 0

# Result falsfying example
resAsm = ""

#-------------------------------------------------------------------------
# Parameters
#-------------------------------------------------------------------------

# Max cycle count
maxT = 20000

# Min instruction count
minInstr = 2

# Max instruction count
maxInstr = 100

# Min number of registers
minReg = 2

# Max number of registers
maxReg = 31

#-------------------------------------------------------------------------
# Errors
#-------------------------------------------------------------------------

class TestFailError( Exception ):
  def __init__( s, msg ):
    return super().__init__( msg )

class InvalidAssemblyError( Exception ):
  def __init__( s, asm ):
    return super().__init__( asm )

#-------------------------------------------------------------------------
# Components
#-------------------------------------------------------------------------

class PicoTestMemoryRTL( Component ):
  def construct( s, mem_nbytes ):
    s.valid = InPort( Bits1 )
    s.ready = OutPort( Bits1 )
    s.instr = InPort( Bits1 )

    s.addr = InPort( Bits32 )
    s.wdata = InPort( Bits32 )
    s.wstrb = InPort( Bits4 )
    s.rdata = OutPort( Bits32 )

    s.memory = MemoryFL( mem_nbytes )

    s.n_fail_msgs = Wire(Bits32)
    s.fail_index = Wire(Bits32)
    s.fail_value = Wire(Bits32)
    s.fail_ref = Wire(Bits32)

    s.n_arch_dump = 0
    s.arch_dump = [ 0 for _ in range(31) ]

    @s.update_ff
    def pico_test_mem_upblk():
      # Once asserted valid, the processor should hold valid
      # until memory responds with ready. The ready signal
      # could combinationally depend on the valid signal, but
      # we use a pipe queue here to decouple the val-rdy ports.

      s.ready <<= Bits1(0)

      if s.valid and not s.ready:
        s.ready <<= Bits1(1)
        if s.addr < mem_nbytes:
          # Memory read
          s.rdata <<= s.memory.read(s.addr, 4)
          # Memory write
          if s.wstrb:
            word = s.memory.read(s.addr, 4)
            if s.wstrb[0]:
              word[ 0: 8] = s.wdata[ 0: 8]
            if s.wstrb[1]:
              word[ 8:16] = s.wdata[ 8:16]
            if s.wstrb[2]:
              word[16:24] = s.wdata[16:24]
            if s.wstrb[3]:
              word[24:32] = s.wdata[24:32]
            s.memory.write(s.addr, 4, word)

        elif s.addr == 0x10000000:
          # Handle PicoRV32 control instructions
          # print(f'DEBUG: n_fail_msgs = {s.n_fail_msgs}')
          if s.n_fail_msgs == 1:
            s.fail_index <<= s.wdata
            s.n_fail_msgs <<= s.n_fail_msgs + 1
            print('PICO_CTRL: received failed test message 2!')
          elif s.n_fail_msgs == 2:
            s.fail_value <<= s.wdata
            s.n_fail_msgs <<= s.n_fail_msgs + 1
            print('PICO_CTRL: received failed test message 3!')
          elif s.n_fail_msgs == 3:
            s.fail_ref <<= s.wdata
            raise TestFailError(f'PICO_CTRL: [FAILED] dest[{s.fail_index}] != ref[{s.fail_index}] ({s.fail_value} != {s.wdata})')
            print('PICO_CTRL: received failed test message 4!')
          elif s.wdata == 0x00020001:
            s.n_fail_msgs <<= b32(1)
            print('PICO_CTRL: received failed test message!')
          elif s.wdata[16:32] == 0x0001:
            print(f'PICO_CTRL: program exits with status {s.wdata[0:16]}')
            sys.exit()
          elif s.wdata == 0x00020000:
            print(f'PICO_CTRL: [PASSED]')
            sys.exit()

        elif s.addr == 0x20000000:
          # Architectural state dump
          s.update_architectural_state( s.wdata )
          if s.n_arch_dump == 31:
            # All architectural states are dumped, exit program
            sys.exit()

        else:
          import pdb;pdb.set_trace()
          raise TestFailError(f'Test memory: invalid address {s.addr}!')

  def update_architectural_state( s, data ):
    s.arch_dump[ s.n_arch_dump ] = data
    s.n_arch_dump += 1

  def line_trace( s ):
    trace = ''
    if s.valid and not s.ready:
      trace = '#'
    elif not s.valid and s.ready:
      trace = ' '
    elif not s.valid and not s.ready:
      trace = '.'
    else:
      if s.instr:
        trace = f'ifetch at {s.addr}: {s.rdata}'
      elif s.wstrb:
        trace = f'write at {s.addr}: {s.wdata}'
      else:
        trace = f'read at {s.addr}: {s.rdata}'
    return f'{trace:>40}'

class TestHarness( Component ):
  def construct( s, mem_nbytes = 1 << 28, pico = 'picorv32_standalone.v' ):
    s.dut = PicoRV32()
    s.dut.setup_import_config( pico )
    s.mem = PicoTestMemoryRTL( mem_nbytes )

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

  def load( s, mem_image ):
    sections = mem_image.get_sections()
    for section in sections:
      start_addr = section.addr
      stop_addr  = section.addr + len(section.data)
      s.mem.memory.mem[start_addr:stop_addr] = section.data

  def fill_memory( s, addr_list ):
    for addr in range(0x200):
      s.mem.memory.mem[addr] = 0xFF
    # for addr in addr_list:
    #   s.mem.memory.mem[addr] = addr

  def line_trace( s ):
    return s.mem.line_trace()

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------

def get_num_regs( tests ):
  all_xs = []
  for test in tests:
    strs = test.split()
    for s in strs:
      if s.startswith('x'):
        try:
          _s = s[:-1] if s[-1] == ',' else s
          int(_s[1:])
          if _s not in all_xs:
            all_xs.append(_s)
        except:
          pass
  return len(all_xs)

def simulate_pico_processor( tests, addr_list, pico ):
  # Add epilogue to the assembly
  tests = copy( tests )
  tests.append( '# END OF PROGRAM' )
  tests.append( '# Epilogue:' )
  tests.append( 'lui x31, 0x20000' )
  for i in range(31):
    tests.append(f'sw x{i}, 0(x31)')

  nInstr = len(tests)
  maxT = 50 * nInstr

  # Test program
  test = '\n'.join( tests )

  # 1MB test memory
  th = TestHarness( 1 << 20, pico )
  th.elaborate()

  mem_image = assemble( test )
  th.load( mem_image )
  th.fill_memory( addr_list )

  # Check import status
  global imported

  # Do not recompile when pico has been imported
  if imported:
    th.dut.config_sverilog_import.recompile = False
  else:
    imported = True

  th.apply( ImportPass() )
  th.apply( SimulationPass() )

  try:
    # print()
    # print('DUT processor')
    T = 0
    th.sim_reset()
    while T < maxT:
      # print(f'{T:>4}: {th.line_trace()}')
      th.tick()
      T += 1

    # Print out in hypothesis tests
    if T == maxT:
      print( '  [FAILED] (time out)' )

    assert T != maxT

  except SystemExit:
    pass

  return th

def simulate_reference_processor( tests, addr_list ):
  # Dump the generated instruction sequence
  print()
  print('/**** Generated Instruction Sequence ****/')
  print(f'Number of instructions = {len(tests)}')
  print(f'Number of registers used = {get_num_regs(tests)}')
  print('\n'.join(map(lambda x: '  '+x, tests)))
  print()
  print('/**** Address List ****/')
  print(addr_list)
  print()

  # Send message to test sink to terminate the test
  tests = copy( tests )
  tests.append('csrw proc2mngr, x0 > 0x00000000')
  test = '\n'.join( tests )

  ref = RefTestHarness( ProcFL )
  ref.elaborate()

  mem_image = assemble( test )
  ref.load( mem_image )
  ref.fill_memory( addr_list )
  ref.apply( SimulationPass() )

  try:
    # print()
    # print('Reference processor')
    T = 0
    ref.sim_reset()
    while not ref.done() and T < maxT:
      # print(f'{T:>4}: {ref.line_trace()}')
      ref.tick()
      T += 1

    assert T != maxT

  except:
    raise InvalidAssemblyError( test )

  return ref

def check_architectural_states( th, ref, addr_list = [] ):
  pico_mem = th.mem

  # Check register x0 ~ x30
  pico_regs = pico_mem.arch_dump
  ref_regs = ref.proc.R
  print()
  print('Comparing architectural states of the processor under test and the ISA simulator...')
  for i in range(31):
    if pico_regs[i] != ref_regs[i]:
      print(f'pico_regs[{i:>2}] ({pico_regs[i]}) != ref_regs[{i:>2}] ({ref_regs[i]})')
      print('  [FAILED]')
      assert pico_regs[i] == ref_regs[i]
    else:
      # print(f'pico_regs[{i:>2}] == ref_regs[{i:>2}] == {pico_regs[i]}')
      pass

  # Check memory content
  print()
  pico_ram = pico_mem.memory.mem
  ref_ram = ref.mem.mem.mem
  for i in addr_list:
    if pico_ram[i] != ref_ram[i]:
      print(f'pico_ram[{i:>8}] (pico_ram[i]) != ref_ram[{i:>8}] ({ref_ram[i]})')
      print('  [FAILED]')
      assert pico_ram[i] == ref_ram[i]
    else:
      # print(f'pico_ram[{i:>8}] == ref_ram[{i:>8}] == {pico_ram[i]}')
      pass

  print('  [PASSED]')

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

def test_simple():
  def fill_mem( mem, data, start ):
    for i, d in enumerate(data):
      mem[start + 4*i    ] =  d & 0xFF
      mem[start + 4*i + 1] = (d & 0xFF00)     >> 8
      mem[start + 4*i + 2] = (d & 0xFF0000)   >> 16
      mem[start + 4*i + 3] = (d & 0xFF000000) >> 24

  th = TestHarness()
  th.elaborate()
  th.apply( ImportPass() )
  th.apply( SimulationPass() )

  # Manually load the simple memory image
  fill_mem( th.mem.memory.mem, [
    0x3fc00093, #       li      x1,1020
    0x0000a023, #       sw      x0,0(x1)
    0x0000a103, # loop: lw      x2,0(x1)
    0x00110113, #       addi    x2,x2,1
    0x0020a023, #       sw      x2,0(x1)
    0xff5ff06f, #       j       <loop>
  ], 0x200 )

  T, maxT = 0, 80

  print()
  th.sim_reset()
  while T < maxT:
    print(f'{T:>4}: {th.line_trace()}')
    th.tick()
    T += 1

@pytest.mark.parametrize(
    'ubmark', [
      '/work/global/pp482/picorv32/app/build-riscv/ubmark-vvadd',
    ]
)
def test_ubmark( ubmark ):
  with open(ubmark, 'rb') as fd:
    mem_image = elf_reader(fd)

  th = TestHarness()
  th.elaborate()
  th.apply( ImportPass() )
  th.apply( SimulationPass() )
  th.load( mem_image )

  T, maxT = 0, 40000

  try:

    print()
    th.sim_reset()
    while T < maxT:
      print(f'{T:>4}: {th.line_trace()}')
      th.tick()
      T += 1

  except SystemExit:
    pass

def test_simple_reference():
  tests = [ 'lui x1, 0x42', ]

  ref = simulate_reference_processor( tests, [] )
  th  = simulate_pico_processor( tests, [], pico )

  check_architectural_states( th, ref )

# IUT: Instructions under test
@settings( deadline = None )
@given( IUT = inst_hypothesis( maxInstr ) )
def test_hypothesis( IUT, pico ):
  tests, addr_list = IUT

  global nTests, resAsm
  nTests += 1
  resAsm = tests

  print()
  print('========== Current Hypothesis Test Case =========')

  ref = simulate_reference_processor( tests, addr_list )
  th  = simulate_pico_processor( tests, addr_list, pico )

  check_architectural_states( th, ref, addr_list )

# Complete random test (CRT)
def test_random( pico ):
  global nTests, resAsm

  # Randomly generate instructions until a falsfying example
  # is found
  while True:
    nTests += 1
    tests, addr_list = inst_random( minReg, maxReg, minInstr, maxInstr )
    resAsm = tests

    print()
    print('========== Current CRT Test Case =========')

    try:
      ref = simulate_reference_processor( tests, addr_list )
      th  = simulate_pico_processor( tests, addr_list, pico )
      check_architectural_states( th, ref, addr_list )
    
    except AssertionError:
      print(f'  CRT tried {nTests} times to find a failing test case!')
      raise

# Iterative deepening test (IDT)
def test_deepening( pico ):
  global nTests, resAsm

  # Incrementally search for a set of instructions
  # until a falsfying example is found. For each set
  # of instructions, thoroughly explore the search space.

  inst_deepening = inst_deepening_gen( maxInstr )

  while True:
    nTests += 1
    tests, addr_list = next( inst_deepening )
    resAsm = tests

    print()
    print('========== Current IDT Test Case =========')

    try:
      ref = simulate_reference_processor( tests, addr_list )
      th  = simulate_pico_processor( tests, addr_list, pico )
      check_architectural_states( th, ref, addr_list )

    except AssertionError:
      print(f'  IDT tried {nTests} times to find a failing test case!')
      raise
