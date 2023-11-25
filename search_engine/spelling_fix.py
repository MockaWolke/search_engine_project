from search_engine import REPO_PATH, USE_MODEL, SPELL_PORT, SPELL_TIMEOUT
from typing import Tuple
import requests
from loguru import logger
import string
import re

PUNCTUATION = set(string.punctuation)


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
    if not USE_MODEL:
        return query, False

    try:
        has_punctioation = any(i in PUNCTUATION for i in query)

        corrected = query_model(query)

        if not has_punctioation:
            corrected = re.sub(r"[^\w\s?]", "", corrected)

        changed = query.lower() != corrected.lower()
        return corrected, changed

    except Exception as e:
        logger.exception(f"Request failed for {query}")
        return query, False
