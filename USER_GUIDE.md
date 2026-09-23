# EGo1 toolchain user guide

[简体中文](USER_GUIDE_cn.md) | [English](USER_GUIDE.md)

This guide is for students who already have the toolchain installed on an Apple Silicon Mac. The everyday command is `./vmake project action`. The examples use `blink`; replace it with your project's alias from the [project list](open-fpga/projects.json).

## Start an experiment

Open a terminal in the folder that contains `vmake`. Quote a path if it contains spaces:

```sh
cd "/path/where/you/saved/program"
./vmake blink sim
```

`sim` compiles and runs the testbench. A `PASS` message with no command error means that testbench's checks passed. `$finish` alone only means the simulation stopped; compare outputs with the assignment's expected behavior.

Choose the next command according to your goal:

| Goal | Command | What to inspect |
| --- | --- | --- |
| Run simulation again | `./vmake blink sim` | Terminal result and `simulation.log` |
| View signals | `./vmake blink wave` | The waveform opened in VS Code |
| Check and build the design | `./vmake blink all` | Final `SUCCESS` and the `.bit` file |
| See synthesis output only | `./vmake blink synth` | `.json` and `vmake-synthesis.log` in `build/` |

`wave` needs the VS Code `code` command and a compatible waveform extension. If `code` is missing, use **Shell Command: Install 'code' command in PATH** in VS Code's command palette, then open a new terminal. You can also find the waveform in the project's `build/` directory.

`all` runs any configured testbench, checks the design, and builds a downloadable file. It does **not** program the board. Projects without a testbench skip simulation. Projects without pin constraints cannot produce a board bitstream.

## Program the board

Connect a data-capable USB cable to the board's UART/JTAG port, then turn on the board. From the same project directory run:

```sh
./vmake blink detect
./vmake blink program
```

Check that `detect` identifies the expected **Xilinx Artix-7 35T** before running `program`. `program` rebuilds the current project and loads its `.bit` into the FPGA. After the command finishes, operate the switches and inspect the LEDs as required by your lab to verify physical behavior.

Programming writes volatile FPGA SRAM, not board Flash. The configuration disappears when power is removed. After programming finishes, turn the board off before unplugging USB.

## Find the results

Each project keeps its sources, configuration, and `build/` under its own directory. `build/simulation.log` contains simulation output, `build/vmake-synthesis.log` contains synthesis diagnostics, and `build/<name>.bit` is the programming file. `<name>` comes from the project's `config.json`; its `wave_file` field gives the waveform path. Use artifacts from the current project so you do not accidentally select an old `.bit`.

## If something fails

- Unknown project: check the [public project list](open-fpga/projects.json) and your local `open-fpga/projects.local.json`, or ask an AI assistant to add a `config.json` and register a local alias.
- Simulation or build failure: share the terminal error and the relevant file in that project's `build/` directory with your AI assistant.
- `detect` reports `device not found`: if an AI ran it in a restricted Codex shell, ask it to retry with authorized host USB access. In your own terminal, also check board power, the UART/JTAG port, and the data cable.
- The software build succeeds but the board behaves unexpectedly: check the project alias, board revision, pin constraints, and switch positions. `SUCCESS` alone means a bitstream was built.

For installation or reinstallation, use the [AI installation guide](ego1-toolchain/INSTALL_AI.md). For toolchain configuration and all commands, see the [technical guide](TECHNICAL.md).
