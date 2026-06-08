import sqlite3
import hashlib
from pathlib import Path
from ..models import FunctionDocumentationModel, DocumentedFunctions

DB_TABLE_DOCUMENTATIONS_INIT: str = """
CREATE TABLE IF NOT EXISTS documentations (
    id TEXT PRIMARY KEY,
    short_description TEXT,
    content TEXT NOT NULL
);
"""

DB_TABLE_DOCUMENTATIONS_INSERT: str = """
INSERT INTO documentations (id, short_description, content)
VALUES (?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    short_description = excluded.short_description,
    content = excluded.content;
"""

DOC_ID: str = "documentations.id"
DOC_SHORT_DESC: str = "documentations.short_description"
DOC_CONTENT: str = "documentations.content"


DB_TABLE_FUNCTIONS_INIT: str = """
CREATE TABLE IF NOT EXISTS functions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    doc_id TEXT NOT NULL,
    FOREIGN KEY(doc_id) REFERENCES documentations(id)
);
"""

DB_TABLE_FUNCTIONS_INSERT: str = """
INSERT INTO functions (id, name, doc_id)
VALUES (?, ?, ?)
ON CONFLICT(name) DO UPDATE SET
    doc_id = excluded.doc_id;
"""

FUNC_ID: str = "functions.id"
FUNC_NAME: str = "functions.name"
DB_TABLE_FUNCTIONS_SELECT: str = f"""
SELECT
    {FUNC_ID},
    {FUNC_NAME},
    {DOC_ID},
    {DOC_SHORT_DESC},
    {DOC_CONTENT}
FROM functions
JOIN documentations ON
    functions.doc_id = documentations.id
"""


class RepodocDB:
    def __init__(self, db_path: Path) -> None:
        self.path: Path = db_path
        self.init()

    @staticmethod
    def _hash(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(DB_TABLE_DOCUMENTATIONS_INIT)
            cur.execute(DB_TABLE_FUNCTIONS_INIT)

    def insert_documentation(self, documentation: FunctionDocumentationModel) -> str:
        has_get_short_description: bool = callable(
            getattr(documentation, 'get_short_description', None)
        )
        short_description: str = (
            documentation.get_short_description() if has_get_short_description
            else ""
        )
        with self._connect() as conn:
            cur = conn.cursor()
            doc_id: str = self._hash(documentation._raw)
            cur.execute(
                DB_TABLE_DOCUMENTATIONS_INSERT,
                (doc_id, short_description, documentation._raw)
            )
        return doc_id

    def insert_function(self, name: str, doc_id: str) -> str:
        with self._connect() as conn:
            cur = conn.cursor()
            func_id: str = self._hash(name)
            cur.execute(
                DB_TABLE_FUNCTIONS_INSERT,
                (func_id, name, doc_id)
            )
        return func_id

    def insert_documented_functions(self, functions: DocumentedFunctions) -> None:
        doc_id: str = self.insert_documentation(functions.documentation)
        for func_name in functions.declarations.keys():
            self.insert_function(func_name, doc_id)

    def select_functions(self) -> list[tuple]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(DB_TABLE_FUNCTIONS_SELECT)
            return cur.fetchall()

    def select_function_by_name(self, name: str) -> tuple | None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                f"{DB_TABLE_FUNCTIONS_SELECT} WHERE {FUNC_NAME} == ?",
                (name,)
            )
            rows = cur.fetchall()
            return rows[0] if rows else None
