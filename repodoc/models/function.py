import re
from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr
from ..utils import warn


class FunctionDocumentationModel(BaseModel):
    _raw: str = PrivateAttr(default="")

    @classmethod
    def from_raw(cls, raw_doc: str) -> "FunctionDocumentationModel":
        documentation: dict[str, str] = {}
        for field in cls.model_fields:
            documentation[field] = cls.extract_section(
                raw_doc, field.replace('_', ' ')
            )
        obj = cls(**documentation)
        obj._raw = raw_doc
        return obj

    @staticmethod
    def extract_section(raw_doc: str, section: str) -> str:
        section_pattern = re.compile(
            rf"^{re.escape(section)}[ \t]*\n"
            rf"((?:(?!^\S)[\s\S])*)",
            re.MULTILINE,
        )
        sections_extracted: list[str] = section_pattern.findall(raw_doc)
        if len(sections_extracted) > 1:
            raise ValueError(
                f"duplicate section '{section}' found in documentation"
            )
        return sections_extracted[0] if sections_extracted else ""

    def to_markdown(self) -> str:
        markdown: str = ""
        for field in self.model_fields:
            section = field.replace("_", " ")
            value = getattr(self, field)
            if not value:
                continue
            markdown += f"## {section}\n{value}"
        return markdown.strip()


@dataclass
class DocumentedFunctions:
    documentation: FunctionDocumentationModel
    declarations: dict[str, str]

    def validate(self) -> None:
        has_get_functions_name: bool = callable(
            getattr(self.documentation, 'get_functions_name', None)
        )
        if not has_get_functions_name:
            warn(
                f"{type(self.documentation).__name__} does not implement 'get_functions_name', "
                "skipping documentation validation."
            )
            return
        doc_functions_name: list[str] = self.documentation.get_functions_name()
        def_functions_name: list[str] = list(self.declarations.keys())
        missing_functions_def: list[str] = []

        if len(doc_functions_name) != len(set(doc_functions_name)):
            duplicates = [f for f in doc_functions_name if doc_functions_name.count(f) > 1]
            raise ValueError(f"duplicate documented functions: {set(duplicates)}")

        for doc_function_name in doc_functions_name:
            if doc_function_name not in def_functions_name:
                missing_functions_def.append(doc_function_name)
            else:
                def_functions_name.remove(doc_function_name)

        if def_functions_name:
            raise ValueError(f"declared functions missing documentation: {def_functions_name}")

        if missing_functions_def:
            raise ValueError(f"documented functions missing declaration: {missing_functions_def}")
