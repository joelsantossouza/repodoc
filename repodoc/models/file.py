import re
from typing import Type
from pydantic import ValidationError
from pathlib import Path
from rich import print
from . import DocumentationModel
from . import DocumentedFunctions
from ..syntax import DocumentedFileSyntax
from ..utils import error


class DocumentedFile:
    def __init__(self,
                 path: Path,
                 save_directory: Path,
                 syntax: DocumentedFileSyntax,
                 documentation_model: Type[DocumentationModel]) -> None:
        self.path: Path = path
        self.save_directory: Path = save_directory / path.parent / path.stem
        self.syntax: DocumentedFileSyntax = syntax
        self.documentation_model: Type[DocumentationModel] = documentation_model
        self.documented_functions: list[DocumentedFunctions] = []
        self.function_declarations: list[str] = []

    def extract_documented_functions(self) -> list[DocumentedFunctions]:
        SYNTAX: DocumentedFileSyntax = self.syntax
        DOCUMENTATION_MODEL: DocumentationModel = self.documentation_model

        file_data: str = self.path.read_text()
        file_header = SYNTAX.file_documentation.match(file_data)
        start_offset: int = file_header.group().count('\n') if file_header else 0
        file_data = SYNTAX.file_documentation.sub('', file_data)
        for doc_funcs in SYNTAX.documented_functions.finditer(file_data):
            doc, funcs = doc_funcs.group(1), doc_funcs.group(2)
            clean_doc: str = SYNTAX.clean_doc(doc)
            clean_funcs: list[str] = self.extract_function_declarations(funcs)
            try:
                documented_functions = DocumentedFunctions(
                    DOCUMENTATION_MODEL.from_raw(clean_doc),
                    {
                        func_name.group(): func
                        for func in clean_funcs
                        if (func_name := SYNTAX.function_name.search(func))
                    }
                )
            except ValidationError as e:
                line_number = file_data[:doc_funcs.start()].count('\n') + start_offset + 1
                for err in e.errors():
                    field = err['loc'][0].replace('_', ' ')
                    error(
                        f"{str(self.path)}:{line_number}: "
                        f"missing required section '{field}' in documentation",
                    )
                continue
            self.documented_functions.append(documented_functions)
        return self.documented_functions

    def extract_function_declarations(self, raw_data: str) -> list[str]:
        SYNTAX: DocumentedFileSyntax = self.syntax

        return [
            SYNTAX.clean_func(func)
            for func in re.findall(SYNTAX.function_declaration, raw_data)
        ]

    def save(self) -> None:
        self.save_directory.mkdir(parents=True, exist_ok=True)
        print(self.save_directory)
        for documented_functions in self.documented_functions:
            for func_name in documented_functions.declarations.keys():
                doc_file = self.save_directory / f"{func_name}.md"
                doc_file.write_text(documented_functions.documentation.to_markdown())
                print(f"saved '{str(doc_file)}'")
