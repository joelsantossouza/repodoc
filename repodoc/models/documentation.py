import re
from pydantic import BaseModel


class DocumentationModel(BaseModel):
    @classmethod
    def from_raw(cls, raw_doc: str) -> "DocumentationModel":
        documentation: dict[str, str] = {}
        for field in cls.model_fields:
            documentation[field] = cls.extract_section(
                raw_doc, field.replace('_', ' ')
            )
        return cls(**documentation)

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
