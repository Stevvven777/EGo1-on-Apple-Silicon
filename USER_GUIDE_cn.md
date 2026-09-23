# EGO1 工具链使用手册

[简体中文](USER_GUIDE_cn.md) | [English](USER_GUIDE.md)

这份手册给已经在 M 芯片 Mac 上装好工具链的同学使用。日常只需记住一个命令：`./vmake 实验名 操作`。下面用 `blink` 举例；做其他实验时，把 `blink` 换成对应名称。可用名称见 [项目列表](open-fpga/projects.json)。

## 开始一次实验

打开终端，进入包含 `vmake` 文件的项目目录。路径因人而异，若路径有空格，保留双引号：

```sh
cd "/你保存项目的位置/program"
./vmake blink sim
```

`sim` 会编译并运行仿真。终端显示 `PASS` 且命令没有报错，表示该实验的 testbench 检查通过。如果只看到 `$finish`，只能说明仿真结束，还要确认输出是否符合实验要求。

接下来按需要选择：

| 我想做什么 | 命令 | 完成后看什么 |
| --- | --- | --- |
| 再跑一次仿真 | `./vmake blink sim` | 终端的检查结果和 `simulation.log` |
| 看信号波形 | `./vmake blink wave` | VS Code 中的波形文件 |
| 检查代码并生成下载文件 | `./vmake blink all` | 最后的 `SUCCESS` 和 `.bit` 文件 |
| 只看综合结果 | `./vmake blink synth` | `build/` 中的 `.json` 和 `vmake-synthesis.log` |

`wave` 需要 VS Code 的 `code` 命令可用，并安装兼容 VCD 的波形查看扩展。若终端提示找不到 `code`，在 VS Code 命令面板运行 **Shell Command: Install 'code' command in PATH**，再打开新终端重试。波形文件也可以在该实验的 `build/` 目录中找到。

`all` 会运行已有的 testbench、检查设计代码，再构建可下载文件；它**不会自动下载到开发板**。没有 testbench 的实验会跳过仿真；没有引脚约束的实验只能完成软件侧构建，不能生成板卡下载文件。

## 下载到开发板

先用可传数据的 USB 线连接板卡的 UART/JTAG 接口，再打开板卡电源。在同一项目目录运行：

```sh
./vmake blink detect
./vmake blink program
```

先看 `detect` 是否识别出预期的 **Xilinx Artix-7 35T**，确认后再运行 `program`。`program` 会重新运行仿真和构建，再把当前实验的 `.bit` 下载到 FPGA。看到下载命令正常结束后，按实验要求操作开关、观察 LED 等实物行为，才能判断上板效果。

下载写入的是 FPGA 的易失配置 SRAM，断电后本次程序会消失；它不会写入板载 Flash。结束时等待下载命令退出，先关闭板卡电源，再拔 USB 线。

## 结果在哪里

每个实验的源码、配置和 `build/` 都在自己的子项目目录。`build/simulation.log` 是仿真输出，`build/vmake-synthesis.log` 是综合日志，`build/<name>.bit` 是下载文件；`<name>` 来自该实验的 `config.json`。波形路径也由 `config.json` 的 `wave_file` 指定。只需查看当前实验的 `build/`，避免误用其他实验或旧流程生成的 `.bit`。

## 遇到问题

- 提示实验不存在：检查 [公开项目列表](open-fpga/projects.json) 和本机的 `open-fpga/projects.local.json`；请 AI 帮你为新实验补 `config.json` 并登记本机名称。
- 仿真或构建失败：把终端报错和当前实验 `build/` 中对应的日志交给 AI，不要只发送最后一行。
- `detect` 报 `device not found`：如果命令是 AI 在 Codex 受限环境里运行的，先让它在获准的本机沙箱外环境重试；如果你在自己的终端运行，也检查板卡电源、UART/JTAG 接口和数据线。
- 软件构建成功但板上现象不对：核对使用的实验名、板卡版本、引脚约束和开关位置；`SUCCESS` 只说明生成了 bitstream。

安装或重装请看 [AI 安装手册](ego1-toolchain/INSTALL_AI.md)；工具链配置和全部命令见 [技术文档](TECHNICAL.md)。
