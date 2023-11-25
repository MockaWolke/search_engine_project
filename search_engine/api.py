from flask import Flask, request, render_template
from search_engine.query import get_results, INDEX_LOADER
from search_engine import (
    REPO_PATH,
    create_QueryParameters,
    QueryParameters,
    format_dataclass_errors,
    CURRENT_INDEX,
)
import os
import math
from loguru import logger
from search_engine.spelling_fix import fix_spelling


app = Flask(__name__)


# --------------- Check for correct index ---------------


INDEX_LOADER.load_index(CURRENT_INDEX)
# --------------------------------------------------------


logger.info(f"Starting API with '{CURRENT_INDEX}' index.")


@app.route("/")
def start():
    return render_template("start.html", current_index=CURRENT_INDEX)


@app.route("/query")
def query_index():
    # validate args with pydantic model

    try:
        args = create_QueryParameters(
            query=request.args.get("q"),
            page_number=request.args.get("p"),
            page_size=request.args.get("s"),
        )

    # if fails -> retrn no results.html
    except ValueError as e:
        error_message = format_dataclass_errors(e)
        return render_template("validation_error.html", error_message=error_message)

    original_query = args.query
    query, query_corrected = fix_spelling(original_query)

    if query_corrected:
        logger.debug(f"Corrected '{original_query}' to '{query}''")

    # get results for query
    result_urls = get_results(query, CURRENT_INDEX)
    n_results = len(result_urls)

    # batch them given page_size
    results_batched = [
        result_urls[i * args.page_size : (i + 1) * args.page_size]
        for i in range(math.ceil(len(result_urls) / args.page_size))
    ]

    # if to high page size or no results return no results page
    if args.page_number >= len(results_batched):
        logger.debug(
            f"Not Found! Q: {original_query} - P: {args.page_number} - T: {n_results} - P: {args.page_size} -B: {len(results_batched)}"
        )

        return render_template(
            "no_result.html",
            q=query,
            query_corrected=query_corrected,
            original_query=original_query,
        )  # no_response.html

    logger.debug(
        f"Q: {original_query} - P: {args.page_number} - T: {n_results} - P: {args.page_size} -B: {len(results_batched)}"
    )

    results = results_batched[args.page_number]

    return render_template(
        "response.html",
        q=query,
        query_corrected=query_corrected,
        original_query=original_query,
        rev=results,
        page=args.page_number,
        page_size=args.page_size,
        page_before_exists=args.page_number > 0,
        page_after_exists=args.page_number + 1 < len(results_batched),
        n_results=n_results,
    )
