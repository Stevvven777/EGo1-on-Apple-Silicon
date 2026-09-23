# source this file from zsh or bash.
if [ -n "${ZSH_VERSION:-}" ]; then
  export EGO1_ROOT="$(cd -- "$(dirname -- "${(%):-%x}")" && pwd)"
elif [ -n "${BASH_VERSION:-}" ]; then
  export EGO1_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
else
  echo 'Please source env.sh from zsh or bash.' >&2
  return 1
fi
export PATH="$EGO1_ROOT/bin:$EGO1_ROOT/.venv/bin:/opt/homebrew/bin:$PATH"
export FPGA_PART=xc7a35tcsg324-1
export XRAY_DATABASE="$EGO1_ROOT/src/prjxray-db/artix7"
