import fire
import os
from pathlib import Path
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from .database import RepodocDB
from .models import (
    DocumentedRepository,
    DocumentedFile,
    FunctionDocumentationModel
)
from .utils import (
    list_files_recursively,
    find_file_recursively,
    warn,
    error
)
from .config import (
    REPODOC_DATABASE_PATH,
    DOC_THEME,
    CustomizedDocumentation
)


class RepodocCLI:
    def __init__(self) -> None:
        os.environ["LESS"] = "-R"
        self.console: Console = Console(theme=DOC_THEME)
        self.db: RepodocDB = RepodocDB(REPODOC_DATABASE_PATH)

    def load(self, source_path: str) -> None:
        documented_repository = DocumentedRepository(
            Path(source_path),
            CustomizedDocumentation
        )
        documented_repository.extract_documented_files()
        for documented_file in documented_repository.documented_files:
            for documented_function in documented_file.documented_functions:
                self.db.insert_documented_functions(documented_function)

    def search(self) -> None:
        funcs = self.db.select_functions()
        for _, name, _, short_description, _ in funcs:
            print(f"[bold white]{name}[/bold white]\t- {short_description}")

    def man(self, function_name: str) -> None:
        func = self.db.select_function_by_name(function_name)
        if func is None:
            error(f"No documentation found for function '{function_name}' in the database.")
            exit(1)
        _, _, _, _, doc_content = func
        function_documentation = CustomizedDocumentation.from_raw(doc_content)
        with self.console.pager(styles=True):
            self.console.print(
                Markdown(function_documentation.to_markdown())
            )


def main() -> None:
    fire.Fire(RepodocCLI)


if __name__ == "__main__":
    main()
