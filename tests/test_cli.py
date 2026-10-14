"""CLI regression tests: running files, package subcommand, bytecode builtins."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "reaper_main.py"


def run(*args, cwd):
    return subprocess.run(
        [sys.executable, str(MAIN), *args],
        cwd=cwd, capture_output=True, text=True, timeout=60,
    )


def test_runs_file_argument(tmp_path):
    script = tmp_path / "hello.reaper"
    script.write_text('harvest "risen";\n')
    result = run(str(script), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "risen"


def test_package_subcommand_still_works(tmp_path):
    result = run("package", "list", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "No packages installed" in result.stdout


def test_bytecode_builtin_argument_order(tmp_path):
    script = tmp_path / "builtins.reaper"
    script.write_text(
        'harvest lesser(3, 9);\n'
        'harvest join_paths("a", "b");\n'
        'bury("out.txt", "grave contents");\n'
        'harvest excavate("out.txt");\n'
    )
    result = run("--bytecode", str(script), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.split("\n")[:3] == ["3", "a/b", "grave contents"]
    assert (tmp_path / "out.txt").read_text() == "grave contents"


def test_bytecode_runs_user_functions(tmp_path):
    script = tmp_path / "fn.reaper"
    script.write_text(
        'infect Greet(soul name) {\n'
        '    harvest "Hello, " + name;\n'
        '}\n'
        'raise Greet("mortal");\n'
    )
    result = run("--bytecode", str(script), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Hello, mortal"
