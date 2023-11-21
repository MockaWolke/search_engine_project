from whoosh.qparser import QueryParser
from flask import Flask, request, render_template
from src.query import get_index_for_query
from src import REPO_PATH
import os
import math
from loguru import logger


os.chdir(REPO_PATH)

logger.add("api.log", rotation="5 MB")

app = Flask(__name__)


CURRENT_INDEX = "wikipedia_big"
PAGE_SIZE = 5


@app.route("/")
def start():
    return render_template("start.html", current_index=CURRENT_INDEX)


@app.route("/query")
def query_index():
    question = request.args.get("q")
    page = int(request.args.get("p", 0))
    page_size = int(request.args.get("s", PAGE_SIZE))

    index = get_index_for_query(CURRENT_INDEX)

    with index.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", index.schema).parse(question)
        results = searcher.search(query, limit=200)
        print(results)
        result_urls = [(r["url"], r["title"]) for r in results]

    results_batched = [
        result_urls[i * page_size : (i + 1) * page_size]
        for i in range(math.ceil(len(result_urls) / page_size))
    ]

    if page >= len(results_batched):
        logger.debug(
            f"Not Found! Q: {question} - P: {page} - T: {len(result_urls)} - P: {page_size} -B: {len(results_batched)}"
        )

        return render_template("no_result.html", q=question)  # no_response.html

    logger.debug(
        f"Q: {question} - P: {page} - T: {len(result_urls)} - P: {page_size} -B: {len(results_batched)}"
    )

    results = results_batched[page]

    return render_template(
        "response.html",
        q=question,
        rev=results,
        page_size=page_size,
        page_before_exists=page > 0,
        page_after_exists=page + 1 < len(results_batched),
        page=page,
    )
