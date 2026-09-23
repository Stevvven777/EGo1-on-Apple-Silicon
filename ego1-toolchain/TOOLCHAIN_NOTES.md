# EGo1 open FPGA toolchain: maintenance notes

This file records the original installation and its validation on one Apple Silicon Mac. It is not a fresh-install procedure; use [INSTALL_AI.md](INSTALL_AI.md) for that. The current project workflow is `vmake` from the repository root. The `ego1-build` commands below describe the older wrapper and its historical artifacts.

The original setup was completed on 2026-09-09 on an M5 Mac running macOS 27.0. The target FPGA is `xc7a35tcsg324-1`. The `xc7a50t` option used to build the shared nextpnr architecture database does not change the target part to a 50T.

## Components

| Component | Role | Installation |
| --- | --- | --- |
| Icarus Verilog 13.0 | Testbench simulation | Homebrew |
| Verilator 5.052 | RTL lint | Homebrew |
| Yosys 0.68 | Xilinx 7-series synthesis | Homebrew |
| nextpnr-himbaechel | Xilinx place and route | Native ARM64 source build in `bin/` |
| Project X-Ray tools | FASM to configuration frames and bitstream | Local source, Python environment, and `bin/` |
| Artix-7 database and chipdb | FPGA architecture data | `src/prjxray-db/` and `share/` |
| openFPGALoader 1.1.1 | USB/JTAG detection and SRAM programming | Homebrew |

The setup did not change system Python or shell startup files. Moving the toolchain directory can invalidate virtual-environment scripts and build-cache paths; recreate those local artifacts rather than copying them to another Mac.

## Environment and diagnostics

From the repository root, `./vmake <alias> <target>` locates the bundled toolchain. To call the older standalone tools from a terminal session:

```sh
source "/path/to/program/ego1-toolchain/env.sh"
ego1-doctor
```

`PASS: software and database checks` means commands and database files were found. It is not a JTAG or board test. The environment script supports zsh and bash.

## Historical blink example using ego1-build

```sh
cd "$EGO1_ROOT/examples/blink"
./run-sim.sh
ego1-build --xdc top.xdc --out build top.v
```

The testbench should print `PASS`. The wrapper runs Verilator, Yosys, nextpnr, and Project X-Ray, then writes `build/top.bit` and prints `SUCCESS`. `top.v` has a 26-bit counter driven by the 100 MHz board clock; LED1_0 toggles about every 0.67 seconds. `top.xdc` assigns the clock to P17 and LED1_0 to K3 with LVCMOS33. `top_tb.v` shortens the counter for simulation. Pin and active-high LED behavior should be checked against the [manufacturer's EGo1 v2.2 manual](https://e-elements.readthedocs.io/zh/ego1_v2.2/EGo1.html).

The original board check found FTDI2232 and an Artix-7 35T, loaded a bitstream into SRAM, and reported `done=1`. The user confirmed LED1_0 blinked as expected. The original local hardware log is not distributed with the public source. This is historical evidence for that machine, not proof of a current connection or of another student's board.

For another simple RTL project, the older wrapper accepts an explicit design file list:

```sh
ego1-build --top top --xdc top.xdc --out build top.v
ego1-build --top lab_top --xdc pins.xdc --out build lab_top.sv counter.v decoder.v
```

Do not include a testbench in the synthesis source list. This wrapper does not provide general handling for complex include paths, macros, proprietary IP, or arbitrary synthesis options. Its default timing target is 100 MHz; `--freq 50` changes the target, not the physical oscillator. The Xilinx backend accepts only a subset of XDC/Tcl. Use simple one-port-per-line constraints and verify every pin against the board manual:

```tcl
set_property PACKAGE_PIN P17 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property PACKAGE_PIN K3 [get_ports led]
set_property IOSTANDARD LVCMOS33 [get_ports led]
```

The older wrapper names outputs `top.*` regardless of `--top`. It removes a stale `top.bit` when a rebuild fails. Vmake uses project-specific artifact names; do not select an older `top.bit` when programming with vmake.

## Legacy output and troubleshooting

| File in `build/` | Meaning |
| --- | --- |
| `lint.log` | Verilator diagnostics; warnings stop the wrapper |
| `synthesis.log`, `top.json` | Yosys log and logic netlist |
| `nextpnr.log`, `top.fasm` | Placement, routing, estimated timing, and FPGA configuration description |
| `fasm2frames.log`, `top.frames` | Project X-Ray conversion log and configuration frames |
| `bitstream.log`, `top.bit` | Final conversion log and downloadable bitstream |

- If a command is missing, source `env.sh` again and run `ego1-doctor`.
- If `fasm2frames` cannot import a module, use the wrapper in this toolchain instead of invoking X-Ray with system Python.
- The warning `Unable to import fast Antlr4 parser` indicates the verified pure-Python textX fallback from the pinned FASM source. It is slower but did not block the original example.
- Missing part or chipdb data usually means `src/` or `share/` is absent or moved.
- For I/O errors, compare top-level port names, part, board revision, and XDC pins, then read `nextpnr.log`.
- For timing failures, inspect the target and critical path. Do not lower the required frequency merely to pass a check.

## Original validation record

1. Native ARM64 nextpnr and X-Ray tools, Python dependencies, and architecture databases passed software checks.
2. Blink RTL passed Verilator; the Icarus testbench passed 32 clock cycles.
3. The full Verilog-to-bitstream flow produced a 2,192,113-byte `top.bit` from `PACKAGE_PIN` constraints.
4. nextpnr estimated that the 100 MHz target passed. This is not Vivado timing signoff.
5. `bitread` decoded 4,974 input frames consistently after excluding the 13 ECC bits at frame word index 50; 434 extra padding frames were zero.
6. FTDI2232 / Artix-7 35T was detected and SRAM programming reported `isc_done=1`, `init=1`, `done=1`; the user observed the expected blink.

The local conversion check can be repeated with:

```sh
"$EGO1_ROOT/.venv/bin/python" "$EGO1_ROOT/verify_bitstream.py" "$EGO1_ROOT/examples/blink/build"
```

See `examples/blink/build/verification.json` and the stage logs for details. Reverse decoding checks software conversion consistency; it does not replace a physical board check.

## Versions and maintenance

- `versions.json` records the three upstream Git commits and recursive submodule versions.
- `homebrew-versions.txt` records the original machine's Homebrew package versions.
- `requirements.lock.txt` records Python package versions for the local virtual environment.
- `patches/nextpnr-package-pin.patch` fixes a local `PACKAGE_PIN` property lifetime issue by copying a value before inserting `LOC` into the attribute table.
- `rebuild.sh` rebuilds from source directories already present. It checks the patch and does not fetch or update repositories.

After sourcing `env.sh`, use `"$EGO1_ROOT/rebuild.sh"` to rebuild these pinned sources. Recheck simulation, the full build, and reverse conversion after upgrading tools or databases. The nextpnr Xilinx backend is experimental; this flow does not include Vivado GUI, IP Catalog, or proprietary IP replacements. PLLs, complex RAM/DSP use, and multiple clock domains require design-specific validation.

Upstream projects: [nextpnr](https://github.com/YosysHQ/nextpnr), [Project X-Ray](https://github.com/f4pga/prjxray), [database](https://github.com/f4pga/prjxray-db), [openFPGALoader](https://trabucayre.github.io/openFPGALoader/guide/first-steps.html).

## Disconnecting after board use

Wait for the programming command to exit. openFPGALoader releases its USB/JTAG connection when it exits; a separate Vivado `disconnect_hw_server` is relevant only if Vivado was used. Turn the EGo1 power switch off before unplugging the USB data cable, and disconnect any external supply first. Handle the powered board by its edges and return it to its protective bag or box after use. Software disconnection does not remove power; an LED may keep blinking after the programming command exits.
