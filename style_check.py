from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".codex"}
DEFAULT_LINE_LENGTH = 88


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    message: str


def iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(current_root) / filename)
    return sorted(files)


def check_file(path: Path, line_length: int = DEFAULT_LINE_LENGTH) -> list[Violation]:
    violations: list[Violation] = []
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Violation(path, 0, "file is not valid UTF-8")]

    lines = content.splitlines(keepends=True)
    if content and not content.endswith("\n"):
        violations.append(
            Violation(path, len(lines) or 1, "file does not end with a newline")
        )

    for line_number, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n")
        if stripped.endswith("\r"):
            stripped = stripped[:-1]
        if "\t" in stripped:
            violations.append(Violation(path, line_number, "tab character found"))
        if stripped.rstrip(" \t") != stripped:
            violations.append(Violation(path, line_number, "trailing whitespace found"))
        if len(stripped) > line_length:
            violations.append(
                Violation(
                    path,
                    line_number,
                    f"line too long ({len(stripped)} > {line_length})",
                )
            )

    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as exc:
        line_number = exc.lineno or 0
        message = exc.msg or "syntax error"
        violations.append(Violation(path, line_number, f"syntax error: {message}"))

    return violations


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight Python style check."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to check. Defaults to the repository root.",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        default=DEFAULT_LINE_LENGTH,
        help="Maximum allowed line length.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    violations: list[Violation] = []
    checked_files: list[Path] = []

    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            checked_files.extend(iter_python_files(path))
        elif path.suffix == ".py" and path.exists():
            checked_files.append(path)

    checked_files = sorted(set(checked_files))

    for path in checked_files:
        violations.extend(check_file(path, line_length=args.line_length))

    if violations:
        for violation in violations:
            location = (
                f"{violation.path}:{violation.line}"
                if violation.line
                else f"{violation.path}"
            )
            print(f"{location}: {violation.message}")
        print(
            f"\nFound {len(violations)} style issue(s) in "
            f"{len(checked_files)} file(s)."
        )
        return 1

    print(f"Style check passed for {len(checked_files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
