import fire
import re
from pathlib import Path
from .utils import list_files_recursively, warn
from .models import DocumentedFile, DocumentationModel
from .syntax import DocumentedFileSyntax

SYNTAX_C = DocumentedFileSyntax(
    open_documentation="/*",
    body_documentation="*",
    close_documentation="*/",
    open_function_declaration=r"^[a-zA-Z_]",
    close_function_declaration=r"\)\s*\{",
    open_function_definition="{",
    function_name=re.compile(r"[a-zA-Z_]\w*(?=\s*\()")
)

SUPPORTED_SYNTAXES_TABLE: dict[str, str] = {
    ".c": SYNTAX_C,
    ".h": SYNTAX_C,
}


class UnixDocumentation(DocumentationModel):
    NAME: str
    DESCRIPTION: str
    RETURN_VALUE: str


class RepoDocCLI:

    def load(self, source_path: str, save_directory: str) -> None:
        documented_files: list[DocumentedFile] = []
        source_files: list[Path] = list_files_recursively(source_path)
        for source_file in source_files:
            syntax = SUPPORTED_SYNTAXES_TABLE.get(source_file.suffix)
            if syntax is None:
                ext = source_file.suffix or "no extension"
                warn(f"skipping '{source_file.name}': no syntax defined for '{ext}' files")
                continue
            save_path = Path(save_directory) / source_file.stem
            documented_file = DocumentedFile(
                source_file,
                save_path,
                syntax,
                UnixDocumentation
            )
            documented_files.append(documented_file)
        for documented_file in documented_files:
            documented_file.extract_documented_functions()
            documented_file.save()


def main() -> None:
    fire.Fire(RepoDocCLI)


if __name__ == "__main__":
    main()
