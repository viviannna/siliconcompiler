#!/bin/bash
mkdir -p ./build/gcd

sc ./examples/gcd/gcd.v \
  -design gcd \
  -target freepdk45 \
  -asic_diesize "0 0 100.13 100.8" \
  -asic_coresize "10.07 11.2 90.25 91" \
  -constraint examples/gcd/constraint.sdc

if [ -f "./build/gcd/job1/export/outputs/gcd.gds" ]; then
  echo "Success!"
  exit 0
fi
echo "Fail :("
exit 1
