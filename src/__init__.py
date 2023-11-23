from whoosh.fields import Schema, TEXT, ID
from pathlib import Path
from annotated_types import Gt, Len
from typing_extensions import Annotated
from pydantic import BaseModel, constr, PositiveInt

ATLEASTZERO = Annotated[int, Gt(-1)]


SCHEMA = Schema(
    url=ID(unique=True, stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=False),
)

REPO_PATH = Path(__file__).parent.parent
INDEXES_DIR = REPO_PATH / "indexes"
DEFAULT_PAGE_SIZE = 5


class QueryParameters(BaseModel):
    query: constr(
        strip_whitespace=True,
        min_length=1,
    )  # ensures a string, and can add more constraints
    page_number: ATLEASTZERO = 0  # ensures an integer that is positive
    page_size: PositiveInt = DEFAULT_PAGE_SIZE  # ensures an integer that is positive


def create_QueryParameters(**kwargs) -> QueryParameters:
    return QueryParameters(**{k: v for k, v in kwargs.items() if v is not None})


def format_pydantic_errors(errors):
    """Format Pydantic validation errors into readable messages."""
    messages = []
    for error in errors:
        field = error["loc"][0]
        error_msg = error["msg"]
        messages.append(f"{field.capitalize().replace('_', ' ')}: {error_msg}.")
    return " ".join(messages)
