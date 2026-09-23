# EGo1 on Apple Silicon

An open source FPGA toolchain for digital logic courses, built to help students run EGo1 labs locally on Apple Silicon Macs.

[简体中文](README_cn.md) | [English](README.md)

## About

`vmake` is the entry point for Verilog simulation, waveform viewing, code checks, synthesis, bitstream generation, and board programming. Each lab is a separate subproject with its own sources and build outputs.

The workflow uses Icarus Verilog, Verilator, Yosys, nextpnr, Project X-Ray, and openFPGALoader. It targets the configured EGo1 / Artix-7 course projects; other boards and more complex designs need their own validation.

## Features

- **Simulate and inspect waveforms:** Run a testbench and examine signal transitions.
- **Check and build:** Check RTL and generate a bitstream for the FPGA.
- **Program a board:** Detect the USB/JTAG device and load the current project into FPGA SRAM.
- **Work with an AI assistant:** Project instructions help an assistant register labs, use `vmake`, diagnose logs, and distinguish software results from physical board observations.

## Get started

| If you want to… | Read |
| --- | --- |
| Run a lab yourself | [Student user guide](USER_GUIDE.md) ([简体中文](USER_GUIDE_cn.md)) |
| Ask AI to help with a lab | [Student AI guide](USER_GUIDE_AI.md) ([简体中文](USER_GUIDE_AI_cn.md)) |
| Set up a new Mac | [AI installation guide](ego1-toolchain/INSTALL_AI.md) (English) |
| Explore commands, configuration, and build outputs | [Technical documentation](TECHNICAL.md) (English) |

AI assistants should also read [AGENTS.md](AGENTS.md). Local setup and maintenance history is in the [maintenance notes](ego1-toolchain/TOOLCHAIN_NOTES.md).

The public checkout includes the `blink` example. Student labs can be registered locally without adding them to the public project list.

## Contributors

- [Stevvven777](https://github.com/Stevvven777): Maintained and refined the toolchain on macOS.
- [szdytom](https://github.com/szdytom): Gathered and configured components for the initial toolchain setup.

The project is released under the [MIT License](LICENSE).

## Acknowledgements

We would like to thank the [F4PGA developers](https://github.com/f4pga) for their work on the Xilinx 7-series FPGA toolchain. Their tools and device data are essential to this project.

We also thank the following open source projects that make this workflow possible:

- [Project X-Ray](https://github.com/f4pga/prjxray): Tools for understanding and generating Xilinx 7-series bitstreams.
- [Project X-Ray database](https://github.com/f4pga/prjxray-db): Device configuration data used to build Artix-7 bitstreams.
- [Yosys](https://github.com/YosysHQ/yosys): Synthesis of Verilog designs.
- [nextpnr](https://github.com/YosysHQ/nextpnr): FPGA placement and routing.
- [Icarus Verilog](https://github.com/steveicarus/iverilog): Running Verilog testbenches.
- [Verilator](https://github.com/verilator/verilator): Checking RTL before a build.
- [openFPGALoader](https://github.com/trabucayre/openFPGALoader): Detecting and programming the FPGA over USB/JTAG.

## Scope

This repository provides an open source workflow for course labs. It does not replace the Vivado GUI, IP Catalog, or proprietary IP. Board programming and physical behavior, such as LED output, must be checked on a connected board.
