# EGo1 on Apple Silicon

面向数字逻辑课程的开源 FPGA 工具链，让使用 Apple Silicon Mac 的同学在本机完成 EGo1 实验。

[简体中文](README_cn.md) | [English](README.md)

## 项目简介

本项目以 `vmake` 作为实验入口，串起 Verilog 仿真、波形查看、代码检查、综合、生成 bitstream 和开发板下载。每个实验是独立子项目，源码与构建结果分别存放。

工具链使用 Icarus Verilog、Verilator、Yosys、nextpnr、Project X-Ray 和 openFPGALoader。它适用于本项目配置的 EGo1 / Artix-7 教学实验；新板卡或更复杂的设计需要单独验证。

## 能做什么

- **仿真与看波形**：运行 testbench，查看信号变化。
- **检查与构建**：检查 RTL，生成可供 FPGA 下载的 bitstream。
- **上板实验**：检测 USB/JTAG 设备，将当前实验下载到 FPGA SRAM。
- **借助 AI 工作**：项目说明指导 AI 登记实验、使用 `vmake`、排查日志，并分别报告软件与实物验证结果。

## 从这里开始

| 你的情况 | 阅读 |
| --- | --- |
| 想自己运行实验 | [同学使用手册](USER_GUIDE_cn.md)（[English](USER_GUIDE.md)） |
| 想让 AI 帮忙做实验 | [如何使用 AI 的手册](USER_GUIDE_AI_cn.md)（[English](USER_GUIDE_AI.md)） |
| 想在新 Mac 上安装 | [AI 安装文档](ego1-toolchain/INSTALL_AI.md)（英文） |
| 想了解命令、配置和构建产物 | [技术文档](TECHNICAL.md)（英文） |

AI 助手还应阅读 [AGENTS.md](AGENTS.md)。工具链的本机维护记录见 [维护笔记](ego1-toolchain/TOOLCHAIN_NOTES.md)。

公开版本附带 `blink` 示例。同学可以在本机登记课程实验，不必把实验加入公开项目列表。

## 贡献者

- [Stevvven777](https://github.com/Stevvven777)：维护并优化了工具链在 Mac 上的表现。
- [szdytom](https://github.com/szdytom)：开发了工具链的初始泛用版本。

项目采用 [MIT 许可证](LICENSE)。

## 项目范围

本仓库提供课程实验所需的开源工作流，不包含 Vivado GUI、IP Catalog 或专有 IP 的替代实现。板卡下载和 LED 等实物现象须在连接的开发板上确认。
