import re
from typing import Type
from pydantic import ValidationError
from pathlib import Path
from . import FunctionDocumentationModel, DocumentedFunctions
from ..syntax import DocumentedFileSyntax
from ..utils import error


class DocumentedFile:
    def __init__(self,
                 path: Path,
                 syntax: DocumentedFileSyntax,
                 documentation_model: Type[FunctionDocumentationModel]) -> None:
        self.path: Path = path
        self.syntax: DocumentedFileSyntax = syntax
        self.documentation_model: Type[FunctionDocumentationModel] = documentation_model
        self.documented_functions: list[DocumentedFunctions] = []
        self.function_declarations: list[str] = []

    def extract_documented_functions(self) -> list[DocumentedFunctions]:
        SYNTAX: DocumentedFileSyntax = self.syntax
        DOCUMENTATION_MODEL: FunctionDocumentationModel = self.documentation_model

        file_data: str = self.path.read_text()
        file_header = SYNTAX.file_documentation.match(file_data)
        start_offset: int = file_header.group().count('\n') if file_header else 0
        file_data = SYNTAX.file_documentation.sub('', file_data)
        for doc_funcs in SYNTAX.documented_functions.finditer(file_data):
            line_number = file_data[:doc_funcs.start()].count('\n') + start_offset + 1
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
                for err in e.errors():
                    field = err['loc'][0].replace('_', ' ')
                    error(
                        f"{self.path}:{line_number}: "
                        f"missing required section '{field}' in documentation",
                    )
                continue
            try:
                documented_functions.validate()
            except ValueError as e:
                error(f"{self.path}:{line_number}: {e}")
                continue
            self.documented_functions.append(documented_functions)
        return self.documented_functions

    def extract_function_declarations(self, raw_data: str) -> list[str]:
        SYNTAX: DocumentedFileSyntax = self.syntax

        return [
            SYNTAX.clean_func(func)
            for func in re.findall(SYNTAX.function_declaration, raw_data)
        ]
