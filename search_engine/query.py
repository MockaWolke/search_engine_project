"""Handles querying"""
import os
from whoosh import index
from search_engine import INDEXES_DIR
from typing import List, Tuple
from whoosh.qparser import QueryParser


def get_index_for_query(index_dir):
    index_dir = INDEXES_DIR / index_dir

    if not (os.path.isdir(index_dir) and os.listdir(index_dir)):
        raise ValueError(f"index_dir {index_dir} must exist and contain items.")

    # set index and writer
    return index.open_dir(index_dir)


def get_results(query: str, index: str) -> List[Tuple[str]]:
    index = get_index_for_query(index)

    with index.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", index.schema).parse(query)
        results = searcher.search(query, limit=1000)

        result_urls = [(r["url"], r["title"]) for r in results]
    return result_urls
