#!/bin/bash
set -euo pipefail
EXAMPLE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$EXAMPLE/../../env.sh"
mkdir -p "$EXAMPLE/build"
cd "$EXAMPLE/build"
iverilog -g2012 -Wall -s top_tb -o top.vvp ../top.v ../top_tb.v
vvp top.vvp | tee simulation.log
