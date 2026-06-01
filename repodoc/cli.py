import fire
import os
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from .models import DocumentedFile
from .utils import (
    list_files_recursively,
    find_file_recursively,
    warn,
    error
)
from .config import (
    REPODOC_DATABASE_DIR,
    SUPPORTED_SYNTAXES_TABLE,
    DOC_THEME,
    CustomizedDocumentation
)


class RepoDocCLI:
    def __init__(self) -> None:
        os.environ["LESS"] = "-R"
        self.console: Console = Console(theme=DOC_THEME)

    def load(self, source_path: str) -> None:
        REPODOC_DATABASE_DIR_PATH: Path = Path(REPODOC_DATABASE_DIR)
        documented_files: list[DocumentedFile] = []

        try:
            source_files: list[Path] = list_files_recursively(source_path)
        except FileNotFoundError as e:
            error(e)
            exit(1)

        for source_file in source_files:
            syntax = SUPPORTED_SYNTAXES_TABLE.get(source_file.suffix)
            if syntax is None:
                ext = source_file.suffix or "no extension"
                warn(f"skipping '{source_file.name}': no syntax defined for '{ext}' files")
                continue
            documented_file = DocumentedFile(
                source_file,
                REPODOC_DATABASE_DIR_PATH,
                syntax,
                CustomizedDocumentation
            )
            documented_files.append(documented_file)
        for documented_file in documented_files:
            documented_file.extract_documented_functions()
            documented_file.save()

    def search(self, function_name: str) -> None:
        if not Path(REPODOC_DATABASE_DIR).exists():
            error("No database found. Run 'repodoc load <source_path>' first to index your files.")
            exit(1)
        doc_file: Path | None = find_file_recursively(REPODOC_DATABASE_DIR, function_name)
        if doc_file is None:
            error(f"No documentation found for function '{function_name}' in the database.")
            exit(1)
        with self.console.pager(styles=True):
            self.console.print(
                Markdown(doc_file.read_text())
            )


def main() -> None:
    fire.Fire(RepoDocCLI)


if __name__ == "__main__":
    main()
