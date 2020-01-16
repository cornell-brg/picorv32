import pytest
import json
from pluggy import HookspecMarker
from math import log2

# from .tests.PicoRV32_test import testIndex, testSessionName, \
#     resAsm, nTests
from .tests import PicoRV32_test

testIndex = 0
testSessionName = ""
testSessionKind = ""

hookspec = HookspecMarker("pytest")

def pytest_addoption( parser ):
  parser.addoption( '--pico', action = 'store', default = 'correct')
  parser.addoption( '--test-index', action = 'store', default = '1')

@pytest.fixture()
def pico( pytestconfig ):
  valid_pico_options = {
    'correct'        : 'picorv32_standalone.v',
    'mul_carrychain' : 'bug_picorv32_mul_carrychain.v',
    'auipc_decode'   : 'bug_picorv32_auipc_decode.v',
    'lt_signed'      : 'bug_picorv32_lt_signed.v',
    'br_fsm'         : 'bug_picorv32_br_fsm.v',
    'mem_state'      : 'bug_picorv32_mem_state.v',
  }
  opt = pytestconfig.getoption( 'pico' )
  assert opt in valid_pico_options
  return valid_pico_options[ opt ]

@pytest.hookimpl()
@hookspec(firstresult=True)
def pytest_cmdline_main(config):
  global testIndex, testSessionName, testSessionKind
  testIndex = int(config.option.test_index)
  testSessionName = config.option.pico
  testSessionKind = config.option.keyword

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):

  def get_imm_comlexity( asm ):
    val = 0
    asm_string = ' '.join(asm).replace(',', ' ').replace('(', ' ').replace(')', ' ')
    asm_string = asm_string.split()
    for s in asm_string:
      try:
        val += int(s)
      except:
        pass
    return 0 if val == 0 else log2(val)

  def get_complexity( asm ):
    nInstr = len(asm)
    nRegs  = PicoRV32_test.get_num_regs(asm)
    vImm   = get_imm_comlexity(asm)
    return float(nInstr + nRegs + vImm)

  name_map = {
      'random' : 'complete_random',
      'deepening' : 'iterative_deepening',
      'hypothesis' : 'hypothesis',
  }
  ds_field = name_map[testSessionKind]

  nTests = PicoRV32_test.nTests
  resAsm = PicoRV32_test.resAsm
  resAddrList = PicoRV32_test.resAddrList

  # Print result to stdout
  PicoRV32_test.dump_asm( resAsm, resAddrList )

  # Number of instructions
  nTrans = len(resAsm)

  # Form file name
  filename = f'{testSessionName}.json'

  # If test index is 1 in CRT then create a new json file
  if testIndex == 1 and testSessionKind == 'random':
    ds = {
        'complete_random'     : {'ntests':[], 'ntrans':[], 'avg_v':[]},
        'iterative_deepening' : {'ntests':[], 'ntrans':[], 'avg_v':[]},
        'hypothesis'          : {'ntests':[], 'ntrans':[], 'avg_v':[]},
    }

  # Otherwise update the result in the json result file
  else:
    with open(filename, 'r') as fd:
      ds = json.load(fd)

  ds[ds_field]['ntests'].append(nTests)
  ds[ds_field]['ntrans'].append(nTrans)
  ds[ds_field]['avg_v' ].append(get_complexity(resAsm))

  with open(filename, 'w') as fd:
    json.dump(ds, fd, indent = 4)
