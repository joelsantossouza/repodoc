import re
from dataclasses import dataclass


@dataclass
class DocumentedFileSyntax:
    function_name: re.Pattern
    open_function_declaration: str
    close_function_declaration: str
    open_function_definition: str
    open_documentation: str
    body_documentation: str
    close_documentation: str | None = None

    def __post_init__(self) -> None:
        self.__doc_pattern: str = self._build_documentation_pattern()
        self.__func_pattern: str = self._build_function_declaration_pattern()
        self.__docfunc_pattern: str = self._build_documented_functions_pattern()
        self.__filedoc_pattern: str = self._build_file_documentation_pattern()

        self.documentation = re.compile(self.__doc_pattern, re.DOTALL | re.MULTILINE)
        self.function_declaration = re.compile(self.__func_pattern, re.DOTALL | re.MULTILINE)
        self.documented_functions = re.compile(self.__docfunc_pattern, re.DOTALL | re.MULTILINE)
        self.file_documentation = re.compile(self.__filedoc_pattern, re.DOTALL)

    def _build_documentation_pattern(self) -> str:
        if self.close_documentation in (None, self.open_documentation):
            return rf"(?:{re.escape(self.open_documentation)}[^\n]*\n)+"
        return (
            rf"{re.escape(self.open_documentation)}"
            rf"(?:(?!{re.escape(self.close_documentation)}).)*"
            rf"{re.escape(self.close_documentation)}"
        )

    def _build_function_declaration_pattern(self) -> str:
        return (
            rf"{self.open_function_declaration}"
            rf".*?"
            rf"{self.close_function_declaration}"
        )

    def _build_documented_functions_pattern(self) -> str:
        return (
            rf"({self.__doc_pattern})"
            rf"((?:(?!{re.escape(self.open_documentation)})[\s\S])*)"
        )

    def _build_file_documentation_pattern(self) -> str:
        return rf"^\s*{self.__doc_pattern}"

    def clean_doc(self, raw_doc: str) -> str:
        # Clean Document Start
        clean_doc = re.sub(
            rf"^\s*{re.escape(self.open_documentation)}\s*\n?", "", raw_doc
        )
        # Clean Document End
        if self.close_documentation:
            clean_doc = re.sub(
                rf"\s*{re.escape(self.close_documentation)}\s*$", "", clean_doc
            )
        # Clean Document Body
        clean_doc = re.sub(
            rf"^\s*{re.escape(self.body_documentation)}[ \t]?",
            "",
            clean_doc,
            flags=re.MULTILINE,
        )
        return clean_doc

    def clean_func(self, func: str) -> str:
        func_definition_start = rf"\s*{re.escape(self.open_function_definition)}\s*$"
        return re.sub(func_definition_start, "", func)
