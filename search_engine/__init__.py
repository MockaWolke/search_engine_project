from whoosh.fields import Schema, TEXT, ID
from pathlib import Path
from dotenv import load_dotenv
import os
from loguru import logger
import requests

REPO_PATH = Path(__file__).parent.parent
os.chdir(REPO_PATH)


assert load_dotenv(REPO_PATH / ".env"), "Could not find a dont env"


CURRENT_INDEX = os.environ.get("CURRENT_INDEX")
if CURRENT_INDEX is None:
    raise ValueError("Dot env needs a CURRENT_INDEX to be set")

SEARCH_LIMIT = int(os.environ.get("SEARCH_LIMIT", 0))
if SEARCH_LIMIT <= 0:
    raise ValueError("Dot env needs a SEARCH_LIMIT to be set")

USE_MODEL = int(os.environ.get("USE_MODEL", 0))
SPELL_PORT = int(os.environ.get("SPELL_PORT", 8008))
SPELL_TIMEOUT = int(os.environ.get("SPELL_TIMEOUT", 3))
RELOAD_TIMEOUT = int(os.environ.get("RELOAD_TIMEOUT", 1))
WORD_WINDOW_LENGTH = int(os.environ.get("WORD_WINDOW_LENGTH", 10))

SCHEMA = Schema(
    url=ID(unique=True, stored=True),
    title=TEXT(stored=True),
    content=TEXT(stored=False),
)

INDEXES_DIR = REPO_PATH / "indexes"
DEFAULT_PAGE_SIZE = 10


def check_helper_api():
    try:
        logger.info(
            f"Checking healt of http://localhost:{SPELL_PORT} with timeout {SPELL_TIMEOUT}"
        )
        endpoint = f"http://localhost:{SPELL_PORT}/health/"

        response = requests.get(endpoint, timeout=SPELL_TIMEOUT)

        # Raise an HTTPError for bad requests
        response.raise_for_status()
        logger.success(f"Received {response.status_code}")
        return True
    except Exception as e:
        logger.exception("Helper api not available")
        return False
