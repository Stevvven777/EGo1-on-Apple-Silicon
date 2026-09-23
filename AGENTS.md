# Project instructions for coding agents

This repository contains the CS207 / EGo1 open source FPGA toolchain. Labs are separate subprojects. Use the language requested by the user; student-facing documentation has separate English and Chinese files.

For a new Mac installation, follow `ego1-toolchain/INSTALL_AI.md`. For routine commands and configuration, use `TECHNICAL.md`. Point students to `USER_GUIDE.md` or `USER_GUIDE_cn.md` for direct tool use and `USER_GUIDE_AI.md` or `USER_GUIDE_AI_cn.md` for examples of requests they can give an AI assistant.

## Start with the project configuration

1. Read `TECHNICAL.md`, `open-fpga/projects.json`, optional `open-fpga/projects.local.json`, and the target subproject's `config.json`. For board work, also read `open-fpga/board-config.json` and that subproject's XDC.
2. Check registration first. If a student's lab is missing, put it under ignored `labs/`, create its `config.json`, and register an alias in ignored `open-fpga/projects.local.json` before running it. Keep `projects.json` for public examples. Reuse existing configurations rather than creating duplicates.
3. Match `top`, `sources`, `testbench`, and `sim_top` to the actual modules. Keep synthesizable sources separate from the testbench. Simulation-only projects may omit constraints; do not invent board pins.
4. Search only the relevant subproject and toolchain entry points. Avoid broad scans of the large `ego1-toolchain/src/`, `build/`, and `.venv/` trees.

## Use vmake

- Run `./vmake <alias> <target>` from the project root. Prefer it for simulation, lint, synthesis, bitstream generation, detection, and programming. Call lower-level tools only for unsupported operations or focused diagnosis, and explain why.
- Choose an explicit target such as `sim`, `wave`, `lint`, `synth`, `all`, or `bit`. Omitting the target runs `all`.
- `program` runs `all` and then loads FPGA SRAM. A request to compile, inspect, or detect does not authorize programming. Do not write Flash for an SRAM programming request.
- Keep source files in their subproject and generated files in its `build/` directory. Do not edit generated files or confuse an old `top.bit` from `ego1-build` with the current vmake artifact.

## USB/JTAG and execution environment

- Run hardware detection and programming from an authorized shell with access to the user's Mac USB devices. When the execution tool supports it, request `sandbox_permissions: "require_escalated"` for hardware commands and follow the review result.
- Detect the current device with `./vmake <alias> detect` before programming. For USB enumeration, `openFPGALoader --scan-usb` is an appropriate lower-level diagnostic because vmake has no scan target.
- On this Mac, a sandboxed openFPGALoader call once reported `device not found` while an allowed host call found FTDI2232 (`0403:6010`, Xilinx TUL) and Artix-7 35T. This is historical evidence, not proof of the current connection. Recheck outside the sandbox before advising cable or power changes.
- An inaccessible Terminal.app window does not imply that all local hardware access is unavailable. State precisely where commands ran.
- If the user requests programming, verify the target and proceed without asking again for authorization already given. If the user has programmed the board independently, a later status question does not trigger another download.

## Verification and communication

- Report compilation, simulation completion, functional validation, bitstream generation, JTAG download, and physical behavior as separate results. Each claim needs its own evidence.
- `$finish` means the simulation ended; it does not prove correctness. Validate against the assignment, a truth table, or an independent expected result. Avoid using the implementation expression as the sole test oracle.
- Confirm that the current run created the configured waveform. If a UI tool only queues an open request, do not claim the waveform is visibly open.
- Verify board revision, physical labels, the manufacturer's pin map, and existing XDC before mapping pins. A successful build does not prove the physical mapping is correct.
- Reread files before editing when the user may be changing them. A failed patch should lead to inspection, not overwriting user changes.
- Use context to distinguish an action request from an informational question, and follow the user's clarification. Give evidence and the next useful step when reporting failures.

## Documentation ownership

- `README.md` and `README_cn.md`: concise English and Chinese project overviews and documentation entry points.
- `TECHNICAL.md`: English commands, configuration, artifacts, and troubleshooting entry points.
- `ego1-toolchain/INSTALL_AI.md`: English fresh-install procedure for an AI assistant.
- `USER_GUIDE.md` and `USER_GUIDE_cn.md`: English and Chinese guides for students using commands directly.
- `USER_GUIDE_AI.md` and `USER_GUIDE_AI_cn.md`: English and Chinese guides for students asking an AI assistant to help.
- Each lab directory: circuit details, pin mapping, truth table, waveform, and board observations for that lab. Keep lab status lists out of the toolchain README.
- `open-fpga/projects.json`, optional `open-fpga/projects.local.json`, and each `config.json` are the sources of truth for registration and build settings. Update existing documentation rather than duplicating lists or treating a one-time connection result as permanent.
