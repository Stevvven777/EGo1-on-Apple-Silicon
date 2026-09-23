#!/bin/bash
# Rebuild from the existing, pinned source checkouts (no network or updates).
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/opt/homebrew/bin:$PATH"
if git -C "$ROOT/src/nextpnr" apply --reverse --check "$ROOT/patches/nextpnr-package-pin.patch" 2>/dev/null; then
  : # Patch already present.
else
  git -C "$ROOT/src/nextpnr" apply --check "$ROOT/patches/nextpnr-package-pin.patch"
  git -C "$ROOT/src/nextpnr" apply "$ROOT/patches/nextpnr-package-pin.patch"
fi
cmake -S "$ROOT/src/nextpnr" -B "$ROOT/build/nextpnr" -G Ninja   -DARCH=himbaechel -DHIMBAECHEL_UARCH=xilinx   -DHIMBAECHEL_XILINX_DEVICES=xc7a50t   -DHIMBAECHEL_PRJXRAY_DB="$ROOT/src/prjxray-db"   -DBUILD_GUI=OFF -DBUILD_PYTHON=OFF -DCMAKE_BUILD_TYPE=Release   -DCMAKE_INSTALL_PREFIX="$ROOT"   -DPython3_EXECUTABLE="$ROOT/.venv/bin/python"   -DXilinxChipdb_Python3_EXECUTABLE="$ROOT/.venv/bin/python"
cmake --build "$ROOT/build/nextpnr" -j 4
cmake --install "$ROOT/build/nextpnr"
cmake -S "$ROOT/src/prjxray" -B "$ROOT/build/prjxray" -G Ninja   -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5   -DCMAKE_CXX_FLAGS='-include cstdint' -DCMAKE_INSTALL_PREFIX="$ROOT"
cmake --build "$ROOT/build/prjxray" --target xc7frames2bit bitread -j 4
cp "$ROOT/build/prjxray/tools/xc7frames2bit" "$ROOT/build/prjxray/tools/bitread" "$ROOT/bin/"
