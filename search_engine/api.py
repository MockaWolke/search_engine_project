from whoosh.qparser import QueryParser
from flask import Flask, request, render_template
from search_engine.query import get_index_for_query
from search_engine import (
    REPO_PATH,
    create_QueryParameters,
    QueryParameters,
    format_pydantic_errors,
)
import os
import math
from loguru import logger
from pydantic import ValidationError

os.chdir(REPO_PATH)

logger.add("api.log", rotation="5 MB")

app = Flask(__name__)


CURRENT_INDEX = "wikipedia_big"

logger.info(f"Starting API with '{CURRENT_INDEX}' index.")


@app.route("/")
def start():
    return render_template("start.html", current_index=CURRENT_INDEX)


@app.route("/query")
def query_index():
    try:
        args = create_QueryParameters(
            query=request.args.get("q"),
            page_number=request.args.get("p"),
            page_size=request.args.get("s"),
        )
    except ValidationError as e:
        error_message = format_pydantic_errors(e.errors())
        return render_template("validation_error.html", error_message=error_message)

    index = get_index_for_query(CURRENT_INDEX)

    with index.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", index.schema).parse(args.query)
        results = searcher.search(query, limit=1000)

        result_urls = [(r["url"], r["title"]) for r in results]

    results_batched = [
        result_urls[i * args.page_size : (i + 1) * args.page_size]
        for i in range(math.ceil(len(result_urls) / args.page_size))
    ]

    n_results = len(result_urls)

    if args.page_number >= len(results_batched):
        logger.debug(
            f"Not Found! Q: {args.query} - P: {args.page_number} - T: {n_results} - P: {args.page_size} -B: {len(results_batched)}"
        )

        return render_template("no_result.html", q=args.query)  # no_response.html

    logger.debug(
        f"Q: {args.query} - P: {args.page_number} - T: {n_results} - P: {args.page_size} -B: {len(results_batched)}"
    )

    results = results_batched[args.page_number]

    return render_template(
        "response.html",
        q=args.query,
        rev=results,
        page=args.page_number,
        page_size=args.page_size,
        page_before_exists=args.page_number > 0,
        page_after_exists=args.page_number + 1 < len(results_batched),
        n_results=n_results,
    )
