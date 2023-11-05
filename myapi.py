from whoosh.qparser import QueryParser
from flask import Flask, request, render_template
from crawler_part1 import *
from index import INDEX, get_index_for_query, parse_domain_index


app = Flask(__name__)



@app.route("/")
def start():
    return"""
                <form action="/query" method="get">
                    <label>Query Domain:</label>
                    <input type="text" name="q">
                    <input type="submit" value="Query">
                </form>
                
                <br><br>
                
                <form action="/change" method="post">
                    <label>Change Domain:</label>
                    <input type="text" name="new_domain">
                    <input type="submit" value="Change">
                </form>
            """

@app.route("/change")
def query_new_index():
    
    new_domain = request.form.get("new_domain")
    parse_domain_index(new_domain, 50)
    return f"You changed to the new domain: {new_domain}"
    


@app.route("/query")
def query_index():
    
    question = request.args.get('q')
    
    print(question)
    
    with get_index_for_query().searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", INDEX.schema).parse(question)
        results = searcher.search(query)
        print(results)
        result_urls = [r['url'] for r in results]
        
    
    print(result_urls)
    return render_template("response.html", rev = result_urls)

