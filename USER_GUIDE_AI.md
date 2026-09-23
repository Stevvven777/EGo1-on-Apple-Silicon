# How to ask AI for help with a digital logic lab

[简体中文](USER_GUIDE_AI_cn.md) | [English](USER_GUIDE_AI.md)

This guide is for **students using an AI assistant**. Open this project's `program` folder in Codex or another AI coding tool that can access your files and local terminal. Tell it the **project name** and **what you want done**; you do not need to memorize the toolchain commands. An AI assistant without file or terminal access can advise you, but it cannot run the project for you.

For your first message, you can say:

> Please read the project instructions first. Check whether my lab is registered, use vmake when possible, and tell me the result and output file locations.

## Requests you can copy

Replace `lab3` with your project name:

| Goal | What to say to AI |
| --- | --- |
| Start a new lab | “This is a new lab4. Please register it with vmake, then run its simulation.” |
| Simulate | “Run the lab3 simulation and check its outputs against the assignment.” |
| Inspect a waveform | “Generate and inspect the lab3 waveform. Show me which inputs or outputs look wrong.” |
| Add pin constraints | “Write an EGo1 constraints file for lab3. I will tell you which switches and LEDs to use; verify the pins against the board manual.” |
| Build a bitstream | “Build lab3 fully and tell me where to find the synthesis result and bitstream.” |
| Program the board | “My EGo1 is connected and powered on. Detect the FPGA first, then load lab3 into FPGA SRAM.” |
| Fix a failure | “Lab3 failed. Read the logs, find the cause, fix it, and rerun the failed step.” |

If you **only want an explanation**, say: “Please explain this first. Do not edit files or program the board.” If you **already programmed the board yourself**, say: “I have programmed it. Do not download again; help me interpret the LEDs I see.”

## Check the AI's answer

Ask it to state what it ran, what passed, where the output files are, and what remains unverified. A finished simulation is not automatically a correct design. A `.bit` file is not proof that the board was programmed. After a successful download, you still need to observe the real switches and LEDs.

Tell the AI how the board is connected, where the switches are set, and what the LEDs do. It cannot see the physical board from command output alone. If it reports `device not found`, ask it to check whether its shell is restricted and to retry JTAG detection with authorized access to your Mac's USB devices.

If the toolchain is not installed, ask the AI to follow the [AI installation guide](ego1-toolchain/INSTALL_AI.md). If you prefer to run commands yourself, see the [direct-use guide](USER_GUIDE.md).
