from whoosh.qparser import QueryParser
from flask import Flask, request, render_template
from src.query import get_index_for_query
from src import REPO_PATH
import os

os.chdir(REPO_PATH)

app = Flask(__name__)


CURRENT_INDEX = "wikipedia_big"


@app.route("/")
def start():
    return render_template("start.html", current_index=CURRENT_INDEX)


# @app.route("/change")
# def query_new_index():

#     new_domain = request.form.get("new_domain")
#     parse_domain_index(new_domain, 50)
#     return f"You changed to the new domain: {new_domain}"


@app.route("/query")
def query_index():
    question = request.args.get("q")

    index = get_index_for_query(CURRENT_INDEX)

    with index.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", index.schema).parse(question)
        results = searcher.search(query)
        print(results)
        result_urls = [r["url"] for r in results]

    print(result_urls)
    return render_template("response.html", rev=result_urls)
