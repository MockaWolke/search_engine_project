from dataclasses import dataclass
from search_engine import DEFAULT_PAGE_SIZE


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
