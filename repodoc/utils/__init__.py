import sys
from pathlib import Path
from rich import print


def list_files_recursively(path: str) -> list[Path]:
    file_path: Path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No such file or directory: {str(file_path)}")
    if file_path.is_file():
        return [file_path]
    return list(file_path.rglob("*"))


def find_file_recursively(source_directory: str, find_file_name: str) -> Path | None:
    directory_path: Path = Path(source_directory)
    if not directory_path.exists():
        raise FileNotFoundError(
            f"No such file or directory: {str(directory_path)}"
        )
    for file in directory_path.rglob("*"):
        if not file.is_file():
            continue
        if file.name == find_file_name:
            return file
    return None


ERROR_COLOR: str = "bold red"
WARN_COLOR: str = "bold blue"


def error(msg: str) -> None:
    print(f"[{ERROR_COLOR}][Error][/{ERROR_COLOR}] {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"[{WARN_COLOR}][Warning][/{WARN_COLOR}] {msg}")
