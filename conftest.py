import pytest

def pytest_addoption( parser ):
  parser.addoption( '--pico', action = 'store', default = 'correct')

@pytest.fixture()
def pico( pytestconfig ):
  valid_pico_options = {
    'correct'        : 'picorv32_standalone.v',
    'mul_carrychain' : 'bug_picorv32_mul_carrychain.v',
  }
  opt = pytestconfig.getoption( 'pico' )
  assert opt in valid_pico_options
  return valid_pico_options[ opt ]
