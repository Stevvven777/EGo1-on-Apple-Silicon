# EGo1 toolchain technical guide

This guide covers the commands, configuration, and build artifacts for the open source EGo1 FPGA workflow on Apple Silicon Macs. `vmake` is the common entry point. Labs are independent subprojects. For the project overview, see the [English](README.md) or [Chinese](README_cn.md) README.

- [Student command guide](USER_GUIDE.md) ([Chinese](USER_GUIDE_cn.md)): simulation, waveforms, builds, and board programming.
- [Student AI guide](USER_GUIDE_AI.md) ([Chinese](USER_GUIDE_AI_cn.md)): examples of what to ask an AI assistant.
- [AI installation guide](ego1-toolchain/INSTALL_AI.md): first-time setup from source on another Mac.
- [AGENTS.md](AGENTS.md): project instructions for coding agents.
- [Toolchain maintenance notes](ego1-toolchain/TOOLCHAIN_NOTES.md): implementation details and validation history.

## Quick start

Run commands in the directory containing `vmake`. Replace `blink` with a registered project alias:

```sh
cd "/path/to/program"
./vmake blink sim       # compile and run the testbench
./vmake blink wave      # rerun simulation and open the waveform
./vmake blink all       # simulate, lint, and build; do not program the board
```

The root `./vmake` script locates this project's toolchain, so sourcing `env.sh` is unnecessary for these commands. To use `vmake` from another directory, source `ego1-toolchain/env.sh` in each new terminal session.

## Commands

| Goal | Command | Result |
| --- | --- | --- |
| Simulate | `./vmake blink sim` | Runs the testbench every time; a failure returns a nonzero status |
| Open waveform | `./vmake blink wave` | Reruns simulation and opens the configured waveform in VS Code |
| Lint | `./vmake blink lint` | Runs Verilator; errors and warnings block this target |
| Full software build | `./vmake blink all` | Simulates when a testbench exists, lints, then builds a bitstream when constraints exist |
| Bitstream only | `./vmake blink bit` | Runs synthesis, place and route, and conversion without simulation or lint |
| Synthesis only | `./vmake blink synth` | Produces a Yosys JSON netlist |
| Force rebuild | `./vmake blink all -f` | Rebuilds after tool or database changes |
| Detect board | `./vmake blink detect` | Reads the current JTAG device identity |
| Program SRAM | `./vmake blink program` | Runs `all`, then loads the current project's bitstream into FPGA SRAM |
| Clean | `./vmake blink clean` | Removes this project's `build/`, including logs and waveforms |

The default target is `all`. `place` and `frames` are available for focused build stages. Before programming, connect the data-capable USB cable, power on the board, and use `detect` to confirm the expected EGo1 device. Wait for programming to finish; power the board off before unplugging USB.

USB/JTAG access requires a shell that can reach the host Mac's USB devices. A sandboxed `device not found` result does not establish that the board is disconnected. Retry detection from an authorized host shell before diagnosing the cable or board.

## Subprojects and artifacts

[open-fpga/projects.json](open-fpga/projects.json) maps public aliases to subproject directories. A student's ignored `open-fpga/projects.local.json` adds private course projects; local aliases take precedence. Each subproject has its own `config.json` and keeps generated files under its own `build/` directory. The artifact base name comes from `config.json`'s `name`, which need not match the alias or top module.

| Artifact | Location within that project's `build/` | Purpose |
| --- | --- | --- |
| Simulation executable | `<name>.vvp` | Icarus Verilog output |
| Waveform | `wave_file` from `config.json` | Signal transitions |
| Synthesis netlist | `<name>.json` | Yosys output |
| Synthesis script and log | `vmake-synth.ys`, `vmake-synthesis.log` | Commands and diagnostics |
| Placed design | `<name>.fasm` | FPGA configuration description |
| Configuration frames | `<name>.frames` | Intermediate bitstream input |
| Bitstream | `<name>.bit` | File loaded into FPGA SRAM |

`ego1-build` from the older workflow writes `top.bit`; vmake does not update that file. Use `./vmake <alias> program` to avoid choosing an outdated bitstream. A project without a testbench skips simulation under `all` and cannot run `sim` or `wave`. A project without constraints stops after synthesis under `all` and cannot run `bit` or `program`.

## Waveform viewer

`wave` requires the VS Code `code` command on `PATH` and a viewer for the generated waveform format, such as VaporView for VCD. If `code` is missing, run **Shell Command: Install 'code' command in PATH** from VS Code's command palette and open a new terminal.

Expand the testbench module named by `sim_top` and add the signals you want to inspect. If VS Code opens the VCD as text, use **Reopen Editor With… → VaporView**. Use the terminal output and `build/simulation.log` to determine whether simulation ran; use expected behavior or testbench checks to determine whether the logic is correct. `$finish` alone is not a functional test.

## Configuration

- `open-fpga/board-config.json`: FPGA part, download cable, and X-Ray database path. The database path is relative to this JSON file.
- `open-fpga/projects.json`: public example aliases and directories relative to this repository root.
- `open-fpga/projects.local.json`: optional, ignored local aliases for a student's labs; it has the same JSON object format.
- `<project>/config.json`: top module, design sources, optional testbench, optional XDC, and waveform path.

Put a student's new lab under the ignored `labs/` directory and register it in `open-fpga/projects.local.json` before using its alias. Keep `projects.json` for examples intended for everyone. For example, `{"labN": "labs/labN"}` maps the alias to `labs/labN/`. A typical `labs/labN/config.json` is:

```json
{
  "name": "labN",
  "top": "design_top",
  "sources": ["design_top.v", "decoder.v"],
  "testbench": "design_top_tb.v",
  "sim_top": "design_top_tb",
  "constraints": "pins.xdc",
  "wave_file": "build/labN.vcd"
}
```

List only synthesizable design files in `sources`; list the testbench separately. Simulation runs from `build/`, so `$dumpfile("labN.vcd")` matches `"wave_file": "build/labN.vcd"`. Omit `constraints` for a simulation-only project; do not invent pin mappings. A clocked project may set `"freq": 100` in MHz, which changes the timing target, not the board oscillator. This wrapper supports explicit source lists; complex include paths, macros, proprietary IP, and arbitrary Vivado Tcl require additional work.

## Cache and logs

The build cache checks content and effective configuration, not just file timestamps. Simulation runs on every `sim`, `wave`, and `all`. Use `-f` after changing the toolchain or database. `.cache.json` files are generated records, not source files. A failed build invalidates this project's vmake bitstream to reduce the risk of downloading stale output.

Relevant logs under each `build/` include `simulation.log`, `vmake-sim-compile.log`, `vmake-lint.log`, `vmake-synthesis.log`, `vmake-nextpnr.log`, `vmake-fasm2frames.log`, and `vmake-bitstream.log`.

For toolchain regression checks, run `python3 tests/test_vmake.py`. Local course projects and their artifacts are excluded from the public repository.
