#!/bin/bash

nTests=50
testSessionNames=(mul_carrychain auipc_decode lt_signed br_fsm mem_state)
testSessionKinds=(random deepening hypothesis)

cd build

for testName in ${testSessionNames[@]}
do
  for testKind in ${testSessionKinds[@]}
  do
    for testIndex in $(seq $nTests)
    do
      rm -rf .hypothesis
      echo "command: pytest ../PicoRV32_test.py -xvs --tb=short --pico $testName -k $testKind --test-index $testIndex"
      pytest ../PicoRV32_test.py --tb=short --pico $testName -k $testKind --test-index $testIndex
    done
  done
done

cd ..
