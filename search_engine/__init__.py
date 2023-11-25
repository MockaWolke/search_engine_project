from whoosh.fields import Schema, TEXT, ID
from pathlib import Path
from annotated_types import Gt, Len
from typing_extensions import Annotated
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
import os

REPO_PATH = Path(__file__).parent.parent

load_dotenv(REPO_PATH / ".env")


CURRENT_INDEX = os.environ.get("CURRENT_INDEX")
if CURRENT_INDEX is None:
    raise ValueError("Dot env needs a CURRENT_INDEX to be set")

SEARCH_LIMIT = int(os.environ.get("SEARCH_LIMIT", 0))
if SEARCH_LIMIT <= 0:
    raise ValueError("Dot env needs a SEARCH_LIMIT to be set")

USE_MODEL = int(os.environ.get("USE_MODEL", 0))


ATLEASTZERO = Annotated[int, Gt(-1)]


SCHEMA = Schema(
    url=ID(unique=True, stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=False),
)

INDEXES_DIR = REPO_PATH / "indexes"
DEFAULT_PAGE_SIZE = 5


@dataclass
class QueryParameters:
    query: str
    page_number: int = 0
    page_size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self):
        if not self.query or not self.query.strip():
            raise ValueError("Query must be a non-empty string.")
        # Type conversion and validation for 'page_number'
        try:
            self.page_number = int(self.page_number)
        except ValueError:
            raise ValueError("Page number must be an integer.")

        if self.page_number < 0:
            raise ValueError("Page number must be at least zero.")

        # Type conversion and validation for 'page_size'
        try:
            self.page_size = int(self.page_size)
        except ValueError:
            raise ValueError("Page size must be an integer.")

        if self.page_size <= 0:
            raise ValueError("Page size must be a positive integer.")


def create_QueryParameters(**kwargs) -> QueryParameters:
    # Filter out None values
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return QueryParameters(**filtered_kwargs)


def format_dataclass_errors(exception) -> str:
    """Format dataclass validation errors into readable messages."""
    return str(exception)
