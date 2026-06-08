from pathlib import Path
from typing import Type
from . import FunctionDocumentationModel, DocumentedFile
from ..utils import list_files_recursively, warn
from ..config import SUPPORTED_SYNTAXES_TABLE


class DocumentedRepository:
    def __init__(self, path: Path,
                 documentation_model: Type[FunctionDocumentationModel]) -> None:
        self.path: Path = path
        self.documentation_model: Type[FunctionDocumentationModel] = documentation_model
        self.documented_files: list[DocumentedFile] = []

    def extract_documented_files(self) -> list[DocumentedFile]:
        DOCUMENTATION_MODEL: FunctionDocumentationModel = self.documentation_model

        source_files: list[Path] = list_files_recursively(self.path)
        for source_file in source_files:
            if not source_file.is_file():
                continue
            syntax = SUPPORTED_SYNTAXES_TABLE.get(source_file.suffix, None)
            if syntax is None:
                ext = source_file.suffix or "no extension"
                warn(f"skipping '{source_file.name}': no syntax defined for '{ext}' files")
                continue
            documented_file = DocumentedFile(
                source_file,
                syntax,
                DOCUMENTATION_MODEL
            )
            documented_file.extract_documented_functions()
            self.documented_files.append(documented_file)
        return self.documented_files
