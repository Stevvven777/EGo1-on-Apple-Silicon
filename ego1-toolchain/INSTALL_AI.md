# EGo1 toolchain: AI installation guide for Apple Silicon Macs

This guide is for an AI assistant installing the public project on a student's Mac. The supported example targets an EGo1 v2.2 board with `xc7a35tcsg324-1` and an FT2232 cable. Other boards, macOS releases, and course projects need their own validation. Read the root [README](../README.md), [technical guide](../TECHNICAL.md), and [AGENTS.md](../AGENTS.md) first.

## 1. Confirm where commands run

Install Homebrew and run the script on the student's **actual Apple Silicon Mac**. A local Codex sandbox and an authorized host shell run on the same Mac, though the sandbox may restrict writes or USB access. A cloud task, remote host, container, or disposable VM installs software in its own environment. If the target machine is unclear, establish it before installing.

From the project root, check:

```sh
uname -s
uname -m
xcode-select -p
command -v brew
brew --prefix
```

Expect `Darwin`, `arm64`, Apple Command Line Tools, and Homebrew. If Command Line Tools are absent, start `xcode-select --install` on the student's Mac and let them complete the OS prompt. If Homebrew is absent, install it on that Mac using the [official Homebrew instructions](https://docs.brew.sh/Installation), then reopen the terminal. Do not use another person's `.venv`, compiled binaries, or system Python as a shortcut.

## 2. Run the project installer

In the folder containing `install.sh` and `vmake`, run:

```sh
./install.sh
```

The script checks the host, installs required Homebrew packages, creates a local Python 3.11 environment, clones the exact upstream revisions from `versions.json`, applies the tracked nextpnr patch through `rebuild.sh`, builds nextpnr and Project X-Ray tools, runs `ego1-doctor`, and builds the public `blink` example with `vmake`. It never programs the board or writes Flash.

The script is safe to rerun after a completed install. It does not reset existing source directories or replace an incomplete virtual environment. If it stops, preserve the error and inspect the named path or log. For source version changes, use a fresh checkout instead of forcing an existing modified directory to a new revision.

Expected software result: `ego1-doctor` prints `PASS: software and database checks`, the blink testbench prints `PASS`, and `vmake` prints `SUCCESS` for `ego1-toolchain/examples/blink/build/blink.bit`. These are software checks; a `.bit` file alone does not prove board programming or physical behavior.

## 3. Check hardware only when requested

After the student connects a data-capable USB cable to the EGo1 UART/JTAG port and powers on the board, use a shell with host USB access:

```sh
./vmake blink detect
```

Confirm the current JTAG result identifies the expected Xilinx Artix-7 35T. `openFPGALoader --scan-usb` can help diagnose USB enumeration. A sandboxed `device not found` does not establish that the board is disconnected; retry with authorized host access before diagnosing cables or power.

Only if the student requests programming, run `./vmake blink program`. It rebuilds the project and loads its bitstream into volatile FPGA SRAM. Report detection, download, and the student's LED observation separately.

## Failure guide

| Symptom | Next check |
| --- | --- |
| Missing `brew` or Command Line Tools | Finish host installation, reopen the terminal, and rerun the installer |
| Existing `.venv` fails the Python check | Inspect it; recreate only after confirming it contains no needed work |
| Source revision or submodule mismatch | Compare with `versions.json`; use a fresh project copy if needed |
| Patch or native build fails | Read the terminal output and `ego1-toolchain/build/` logs; check Homebrew and source versions |
| `ego1-doctor` fails | Check the missing command or database path before trying `vmake` |
| Blink build fails | Read `simulation.log` and the relevant `vmake-*.log` in `examples/blink/build/` |
| JTAG fails only inside a sandbox | Retry detection from an authorized host shell |

At handoff, state the Mac architecture and macOS version, installed tool versions, upstream revisions, `ego1-doctor` and blink build results, and whether hardware was checked. Mark unrun stages as unverified.
