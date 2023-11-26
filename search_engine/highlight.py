import requests
from bs4 import BeautifulSoup
from typing import List, Set, Tuple
from loguru import logger
from search_engine.crawl import extract_text
from search_engine.query import get_tokens
from search_engine import WORD_WINDOW_LENGTH, RELOAD_TIMEOUT, SPELL_PORT
import time
from loguru import logger

to_utf8 = lambda x: x.encode("utf-8").decode("utf-8")


def request_page_and_get_text(url: str, timeout: int) -> dict:
    # Define the endpoint URL. Adjust the path as needed.
    endpoint = f"http://localhost:{SPELL_PORT}/reload_text/"

    # Send the POST request
    try:
        response = requests.post(
            endpoint, json={"url": url, "timeout": timeout}, timeout=timeout
        )

        # Raise an HTTPError for bad requests
        response.raise_for_status()

        # Get the response data
        response_data = response.json()

        return response_data["text"], response_data["success"]

    except requests.RequestException as e:
        # Handle any request-related errors
        logger.exception(f"Reload Request failed: {url}")
        return "", False


def get_matches(splitted: List[str], matched_tokens: Set[str]) -> List[bool]:
    is_a_match = []

    for word in splitted:
        token = get_tokens(word)

        inquery = matched_tokens.intersection(token)

        if len(inquery) == 1:
            token = tuple(inquery)[0]
            is_a_match.append(True)
        else:
            is_a_match.append(False)

    return is_a_match


def highlight(text: str, matched_tokens: Set[str]) -> List[Tuple[str, str]]:
    splitted = text.split()

    is_a_match = get_matches(splitted, matched_tokens)

    max_val, position = 0, 0

    if len(text) < WORD_WINDOW_LENGTH:
        return list(zip(splitted, is_a_match))

    for i in range(0, len(splitted) - WORD_WINDOW_LENGTH):
        matches = sum(is_a_match[i : i + WORD_WINDOW_LENGTH])

        if matches > max_val:
            max_val = matches
            position = i

    token_window = splitted[position : position + WORD_WINDOW_LENGTH]
    do_highlighting = is_a_match[position : position + WORD_WINDOW_LENGTH]

    return list(zip(token_window, do_highlighting))


def highlight_result_page(results: list[Tuple[str, str, List[str], Set[str]]]):
    highlighted_results = []

    for url, title, missing, matches in results:
        start_time = time.time()

        text, successs = request_page_and_get_text(url, timeout=RELOAD_TIMEOUT)

        if successs == False:
            continue

        highlighting_info = highlight(text, matches)

        highlighted_results.append((url, title, missing, highlighting_info))

        logger.debug(f"Total Highlighting {url} took {time.time()- start_time}")

    return highlighted_results
