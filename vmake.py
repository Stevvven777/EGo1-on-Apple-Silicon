#!/usr/bin/env python3
"""Configuration-driven CS207 FPGA workflow using the bundled EGO1 toolchain."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
BOARD_CONFIG_PATH = ROOT / "open-fpga/board-config.json"
PROJECTS_PATH = ROOT / "open-fpga/projects.json"
LOCAL_PROJECTS_PATH = ROOT / "open-fpga/projects.local.json"
TOOLCHAIN = ROOT / "ego1-toolchain"

class BuildError(RuntimeError):
    pass

def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError(f"无法读取 JSON 配置 {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"配置顶层必须是对象: {path}")
    return value

def contained(base: Path, name: str) -> Path:
    if not isinstance(name, str) or not name:
        raise BuildError("文件或目录路径必须是非空字符串")
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise BuildError(f"路径必须位于 {base} 内: {name}")
    return path

def load_config(project: str) -> tuple[Path, dict[str, Any]]:
    aliases = read_json(PROJECTS_PATH) if PROJECTS_PATH.exists() else {}
    if LOCAL_PROJECTS_PATH.exists():
        aliases.update(read_json(LOCAL_PROJECTS_PATH))
    project_dir = contained(ROOT, aliases.get(project, project))
    if project_dir == ROOT:
        raise BuildError("请选择实验子目录")
    config = read_json(project_dir / "config.json")
    board = read_json(BOARD_CONFIG_PATH)
    for key in ("part", "cable", "xray_db"):
        if not isinstance(board.get(key), str) or not board[key]:
            raise BuildError(f"board-config.json 缺少字符串字段: {key}")
    # Database path is relative to the board configuration, never the invoking cwd.
    board["xray_db"] = str((BOARD_CONFIG_PATH.parent / board["xray_db"]).resolve())
    config.update(board)
    for key in ("name", "top"):
        if not isinstance(config.get(key), str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", config[key]):
            raise BuildError(f"config.json 的 {key} 必须是简单英文标识符")
    if not isinstance(config.get("sources"), list) or not config["sources"]:
        raise BuildError("sources 必须是非空文件名数组")
    for name in config["sources"]:
        contained(project_dir, name)
    if config.get("testbench") and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(config.get("sim_top", ""))):
        raise BuildError("配置 testbench 时必须提供 sim_top")
    return project_dir, config

def configure_environment() -> None:
    os.environ["PATH"] = os.pathsep.join([str(TOOLCHAIN / "bin"), str(TOOLCHAIN / ".venv/bin"),
                                        "/opt/homebrew/bin", os.environ.get("PATH", "")])

def run(command: list[str], cwd: Path, log: Path | None = None) -> None:
    print("+", shlex.join(command), flush=True)
    try:
        if log is None:
            subprocess.run(command, cwd=cwd, check=True)
        else:
            with log.open("w") as stream:
                result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                print(log.read_text(errors="replace")[-7000:], file=sys.stderr)
                raise BuildError(f"命令失败（{result.returncode}），日志: {log}")
    except FileNotFoundError as exc:
        raise BuildError(f"找不到命令: {command[0]}，请检查工具链安装") from exc

def file_hash(path: Path) -> str:
    if not path.is_file():
        raise BuildError(f"找不到文件: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Project:
    def __init__(self, path: Path, config: dict[str, Any], force: bool = False):
        self.path, self.config, self.force = path, config, force
        self.build = contained(path, "build")
        self.build.mkdir(exist_ok=True)
        self.sources = [contained(path, name) for name in config["sources"]]
        self.base_inputs = [path / "config.json", BOARD_CONFIG_PATH, Path(__file__).resolve()]
        self.synth_done = False

    def artifact(self, suffix: str) -> Path:
        return self.build / (self.config["name"] + suffix)

    def invalidate_bit(self) -> None:
        self.artifact(".bit").unlink(missing_ok=True)
        self.artifact(".bit.cache.json").unlink(missing_ok=True)

    def cached(self, suffix: str, inputs: list[Path], action: Callable[[], None]) -> None:
        output = self.artifact(suffix)
        stamp = self.artifact(suffix + ".cache.json")
        # Hash contents and effective configuration, including command-line overrides.
        data = {"config": self.config, "inputs": {str(p): file_hash(p) for p in self.base_inputs + inputs}}
        fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        if not self.force and output.is_file() and stamp.is_file():
            try:
                saved = json.loads(stamp.read_text())
                if saved == {"fingerprint": fingerprint, "output": file_hash(output)}:
                    print(f"[cached] {output.name}")
                    return
            except (OSError, ValueError):
                pass
        # A failed rebuild must not leave an old downloadable bitstream behind.
        if suffix != ".vvp":
            self.invalidate_bit()
        output.unlink(missing_ok=True)
        stamp.unlink(missing_ok=True)
        try:
            action()
            digest = file_hash(output)
            if output.stat().st_size == 0:
                raise BuildError(f"工具生成了空文件: {output}")
        except BaseException:
            output.unlink(missing_ok=True)
            raise
        stamp.write_text(json.dumps({"fingerprint": fingerprint, "output": digest}) + "\n")

    def sim(self) -> None:
        if not self.config.get("testbench"):
            raise BuildError("此实验没有 testbench，不能执行 sim/wave")
        sources = self.sources + [contained(self.path, self.config["testbench"])]
        self.cached(".vvp", sources, lambda: run(
            ["iverilog", "-g2012", "-Wall", "-s", self.config["sim_top"], "-o", str(self.artifact(".vvp")),
             *map(str, sources)], self.build, self.build / "vmake-sim-compile.log"))
        # Run in build so testbench $dumpfile paths resolve under this project.
        wave = contained(self.path, self.config.get("wave_file", f"build/{self.config['name']}.vcd"))
        if wave.suffix.lower() not in (".vcd", ".fst", ".ghw"):
            raise BuildError("wave_file 必须为 VCD/FST/GHW 文件")
        wave.unlink(missing_ok=True)
        run(["vvp", str(self.artifact(".vvp"))], self.build, self.build / "simulation.log")
        print((self.build / "simulation.log").read_text(), end="")

    def lint(self) -> None:
        for p in self.sources:
            file_hash(p)
        run(["verilator", "--lint-only", "-Wall", "--top-module", self.config["top"], *map(str, self.sources)],
            self.build, self.build / "vmake-lint.log")

    def synth(self) -> None:
        if self.synth_done:
            return
        # These quotes are for the Yosys language, not for the shell.
        def quote(path: Path) -> str:
            return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"') + '"'
        def action() -> None:
            script = self.build / "vmake-synth.ys"
            script.write_text("read_verilog -sv " + " ".join(quote(p) for p in self.sources) +
                              f"\nsynth_xilinx -family xc7 -top {self.config['top']}\ncheck -assert\n" +
                              "write_json " + quote(self.artifact(".json")) + "\n")
            run(["yosys", "-Q", "-T", "-s", str(script)], self.build, self.build / "vmake-synthesis.log")
        self.cached(".json", self.sources, action)
        self.synth_done = True

    def require_hardware(self) -> Path:
        if not self.config.get("constraints"):
            raise BuildError("此实验没有 constraints，不能生成或下载 bitstream")
        xdc = contained(self.path, self.config["constraints"])
        file_hash(xdc)
        file_hash(Path(self.config["xray_db"]) / self.config["part"] / "part.yaml")
        return xdc

    def place(self) -> None:
        xdc = self.require_hardware()
        self.synth()
        cmd = ["nextpnr-himbaechel", "--device", self.config["part"]]
        if self.config.get("freq") is not None:
            cmd += ["--freq", str(self.config["freq"])]
        cmd += ["--json", str(self.artifact(".json")), "-o", f"xdc={xdc}", "-o", f"fasm={self.artifact('.fasm')}"]
        self.cached(".fasm", [self.artifact(".json"), xdc], lambda: run(cmd, self.build, self.build / "vmake-nextpnr.log"))

    def frames(self) -> None:
        self.place()
        cmd = ["fasm2frames", "--db-root", self.config["xray_db"], "--part", self.config["part"],
               str(self.artifact(".fasm")), str(self.artifact(".frames"))]
        self.cached(".frames", [self.artifact(".fasm")], lambda: run(cmd, self.build, self.build / "vmake-fasm2frames.log"))

    def bit(self) -> None:
        self.frames()
        partfile = Path(self.config["xray_db"]) / self.config["part"] / "part.yaml"
        def action() -> None:
            run(["xc7frames2bit", "--part_file", str(partfile), "--part_name", self.config["part"],
                 "--frm_file", str(self.artifact(".frames")), "--output_file", str(self.artifact(".bit"))],
                self.build, self.build / "vmake-bitstream.log")
            data = self.artifact(".bit").read_bytes()
            if len(data) < 1024 or bytes.fromhex("aa995566") not in data:
                raise BuildError("生成的 bitstream 缺少配置同步字或大小异常")
        self.cached(".bit", [self.artifact(".frames"), partfile], action)
        print(f"SUCCESS: {self.artifact('.bit')}")

    def all(self) -> None:
        if self.config.get("testbench"):
            self.sim()
        else:
            print("[sim skipped] 此实验未配置 testbench")
        self.lint()
        if self.config.get("constraints"):
            self.bit()
        else:
            self.synth()

    def wave(self) -> None:
        code = shutil.which("code")
        if code is None:
            raise BuildError("找不到 code；在 VS Code 中执行 Shell Command: Install 'code' command in PATH")
        self.sim()
        wave = contained(self.path, self.config.get("wave_file", f"build/{self.config['name']}.vcd"))
        if not wave.is_file():
            raise BuildError(f"testbench 未生成配置指定的波形: {wave}")
        run([code, "--reuse-window", str(ROOT), str(wave)], self.path)

    def detect(self) -> None:
        run(["openFPGALoader", "-c", self.config["cable"], "--detect"], self.path)

    def program(self) -> None:
        self.require_hardware()
        self.all()
        run(["openFPGALoader", "-c", self.config["cable"], "-m", str(self.artifact(".bit"))], self.path)

    def clean(self) -> None:
        shutil.rmtree(self.build)
        print(f"removed {self.build}")

def main() -> int:
    parser = argparse.ArgumentParser(description="CS207 FPGA workflow · Vaporview waveform viewer")
    parser.add_argument("project", help="实验别名（例如 blink），或 program 下的实验目录")
    parser.add_argument("target", nargs="?", default="all",
                        choices=("all", "sim", "lint", "synth", "place", "frames", "bit", "detect", "program", "wave", "clean"))
    parser.add_argument("-f", "--force", action="store_true", help="强制重建；升级工具或数据库后使用")
    parser.add_argument("--part", help="临时覆盖器件型号（仍需匹配的数据库和约束）")
    parser.add_argument("--cable", help="临时覆盖下载器类型")
    args = parser.parse_args()
    project = None
    try:
        configure_environment()
        path, config = load_config(args.project)
        if args.part:
            config["part"] = args.part
        if args.cable:
            config["cable"] = args.cable
        project = Project(path, config, args.force)
        getattr(project, args.target)()
    except (BuildError, OSError, subprocess.CalledProcessError) as exc:
        if project is not None and args.target not in ("clean", "detect"):
            project.invalidate_bit()
        print(f"vmake: error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
