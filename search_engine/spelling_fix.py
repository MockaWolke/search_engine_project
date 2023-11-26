from search_engine import REPO_PATH, USE_MODEL, SPELL_PORT, SPELL_TIMEOUT
from typing import Tuple
import requests
from loguru import logger
import string
import re

PUNCTUATION = set(string.punctuation)
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)


def query_model(query: str) -> str:
    response = requests.post(
        f"http://localhost:{SPELL_PORT}/fix_spelling/",
        json={"text": query},
        timeout=SPELL_TIMEOUT,
    )

    response.raise_for_status()  # Raise an HTTPError for bad requests
    corrected_text = response.json()

    return corrected_text


def fix_spelling(query: str) -> Tuple[str, bool]:
    query = emoji_pattern.sub(r"", query)

    if not USE_MODEL:
        return query, False

    try:
        has_punctioation = any(i in PUNCTUATION for i in query)

        corrected = query_model(query)

        if not has_punctioation:
            corrected = re.sub(r"[^\w\s?]", "", corrected)

        changed = (
            query.lower() != corrected.lower()
            and query.lower() + "?" != corrected.lower()
        )
        return corrected, changed

    except Exception as e:
        logger.exception(f"Request failed for {query}")
        return query, False
