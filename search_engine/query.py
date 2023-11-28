"""Handles querying"""
import os
from whoosh import index
from search_engine import INDEXES_DIR, SEARCH_LIMIT
from typing import List, Tuple, Set
from whoosh.qparser import QueryParser
from whoosh import qparser
from whoosh.analysis import StandardAnalyzer
from loguru import logger


def get_tokens(text: str) -> Set[str]:
    anaylzer = StandardAnalyzer()
    tokens = anaylzer(text)

    return set(t.text for t in tokens)


class INDEX_LOADER:
    _instance: "INDEX_LOADER" = None

    def __init__(self, index_dir):
        index_dir = INDEXES_DIR / index_dir

        self.index_dir = index_dir

        if not (os.path.isdir(index_dir) and os.listdir(index_dir)):
            raise ValueError(f"index_dir {index_dir} must exist and contain items.")

        self.index = index.open_dir(index_dir)

    @classmethod
    def load_index(cls, index_dir):
        if cls._instance is None:
            cls._instance = INDEX_LOADER(index_dir)

        elif cls._instance.index_dir != index_dir:
            cls._instance = INDEX_LOADER(index_dir)

        return cls._instance.index


def search_and(
    query: str, index_dir: str
) -> List[Tuple[str, str, List[str], Set[str]]]:
    tokens = get_tokens(query)

    current_index = INDEX_LOADER.load_index(index_dir)

    parser = QueryParser("content", current_index.schema)
    query = parser.parse(query)

    with current_index.searcher() as searcher:
        results = searcher.search(
            query,
            limit=SEARCH_LIMIT,
        )

        result_urls = [(r["url"], r["title"], [], tokens) for r in results]

    return result_urls


def convert_matched_terms(matched_term: List, query_tokens: List[str]) -> List[str]:
    current_tokens = set(term[-1].decode("utf-8") for term in matched_term)

    differnce = query_tokens.difference(current_tokens)

    return list(differnce)


def search_or(query: str, index_dir: str) -> List[Tuple[str, str, List[str], Set[str]]]:
    tokens = get_tokens(query)

    current_index = INDEX_LOADER.load_index(index_dir)

    parser = QueryParser("content", current_index.schema, group=qparser.OrGroup)
    query = parser.parse(query)

    with current_index.searcher() as searcher:
        results = searcher.search(query, limit=SEARCH_LIMIT, terms=True)

        result_urls = [
            (
                r["url"],
                r["title"],
                convert_matched_terms(r.matched_terms(), tokens),
                tokens,
            )
            for r in results
        ]

    result_urls = sorted(result_urls, key=lambda res: len(res[2]))

    return result_urls


def get_results(
    query: str, index_dir: str, n_min_results: int
) -> List[Tuple[str, str, List[str], Set[str]]]:
    tokens = get_tokens(query)

    if len(tokens) == 0:
        logger.debug("Tokens empty for query {query}")
        return []

    logger.debug(f"The search tokens: {tokens}")

    result_urls = search_and(query, index_dir)

    if len(result_urls) >= n_min_results:
        return result_urls

    logger.debug(f"Could not {n_min_results} with and, only {len(result_urls) }found.")

    logger.debug(f"Could not find and for {tokens}. Trying or.")

    or_results = search_or(query, index_dir)

    logger.debug(f"Found {len(or_results) } or results.")

    return result_urls + or_results
