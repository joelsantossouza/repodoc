from . import DocumentationModel
from dataclasses import dataclass


@dataclass
class DocumentedFunctions:
    documentation: DocumentationModel
    declarations: dict[str, str]
