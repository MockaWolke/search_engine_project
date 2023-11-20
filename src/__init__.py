from whoosh.fields import Schema, TEXT, ID
from pathlib import Path

SCHEMA = Schema(
    url=ID(unique=True, stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=False),
)

REPO_PATH = Path(__file__).parent.parent
INDEXES_DIR = REPO_PATH / "indexes"
