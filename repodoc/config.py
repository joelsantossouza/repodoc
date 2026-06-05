import re
from .models import FunctionDocumentationModel
from .syntax import DocumentedFileSyntax
from rich.theme import Theme

REPODOC_DATABASE_DIR: str = ".repodoc"


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


DOC_THEME = Theme({
    "markdown.h2": "bold white",
})


class CustomizedDocumentation(FunctionDocumentationModel):
    NAME: str
    DESCRIPTION: str
    RETURN_VALUE: str

    def get_functions_name(self) -> list[str]:
        return [
            name.strip() for name in self.NAME.split("-")[0].split(",")
        ]
