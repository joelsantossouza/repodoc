import sys
from pathlib import Path
from rich import print


def list_files_recursively(path: str) -> list[str]:
    file_path: Path = Path(path)
    if file_path.is_file():
        return [file_path]
    return list(file_path.rglob("*"))


ERROR_COLOR: str = "bold red"
WARN_COLOR: str = "bold blue"


def error(msg: str) -> None:
    print(f"[{ERROR_COLOR}][Error][/{ERROR_COLOR}] {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"[{WARN_COLOR}][Warning][/{WARN_COLOR}] {msg}")
