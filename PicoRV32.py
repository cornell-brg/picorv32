#=========================================================================
# PicoRV32.py
#=========================================================================
# PyMTL3 component backed by the Verilog PicoRV32 processor.
#
# Author : Peitian Pan
# Date   : Dec 30, 2019

from pymtl3 import *
from pymtl3.passes.backends.sverilog import ImportConfigs
from pymtl3.passes.backends.sverilog.util.utility import get_dir

class PicoRV32( Component, Placeholder ):
  def construct( s ):
    s.resetn = InPort( Bits1 )
    s.trap = OutPort( Bits1 )

    # Native memory interface

    s.mem_valid = OutPort( Bits1 )
    s.mem_instr = OutPort( Bits1 )
    s.mem_ready = InPort( Bits1 )

    s.mem_addr  = OutPort( Bits32 )
    s.mem_wdata = OutPort( Bits32 )
    s.mem_wstrb = OutPort( Bits4 )
    s.mem_rdata = InPort( Bits32 )

    # Look-ahead interface

    s.mem_la_read  = OutPort( Bits1 )
    s.mem_la_write = OutPort( Bits1 )
    s.mem_la_addr  = OutPort( Bits32 )
    s.mem_la_wdata = OutPort( Bits32 )
    s.mem_la_wstrb = OutPort( Bits4 )

    # Pico co-processor interface (PCPI)

    s.pcpi_valid = OutPort( Bits1 )
    s.pcpi_insn  = OutPort( Bits32 )
    s.pcpi_rs1   = OutPort( Bits32 )
    s.pcpi_rs2   = OutPort( Bits32 )
    s.pcpi_wr    = InPort( Bits1 )
    s.pcpi_rd    = InPort( Bits32 )
    s.pcpi_wait  = InPort( Bits1 )
    s.pcpi_ready = InPort( Bits1 )

    # IRQ interface

    s.irq = InPort( Bits32 )
    s.eoi = OutPort( Bits32 )

    # Trace interface

    s.trace_valid = OutPort( Bits1 )
    s.trace_data  = OutPort( Bits36 )

    # Import config

    s.config_sverilog_import = ImportConfigs(
        vl_src = get_dir(__file__)+'picorv32_standalone.v',
        top_module = 'picorv32',
        vl_trace = True,
        vl_W_lint = False,
        has_reset = False,
    )
