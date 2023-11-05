from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
from whoosh import index
import tqdm
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from crawler_part1 import *

schema = Schema(
    url=ID(unique=False, stored=True),     # unique=True ensures that each URL is unique
    title=TEXT(stored=True),
    content=TEXT(stored=True)
)


INDEX_DIR = "indexdir"

INDEX = create_in(INDEX_DIR, schema)

def get_index_for_query():
    
    return index.open_dir(INDEX_DIR)


def parse_domain_index(domain, limit_page_visited):
    
    
    writer = INDEX.writer()
    
    links = [domain]
    have_or_will_visit = {domain}


    process_bar = tqdm(range(limit_page_visited), f"Crawling the {domain} domain.")
    
    
    while links:
    
        url = links.pop()
        
        req = requests.get(url, timeout=3)
        soup = BeautifulSoup(req.content, 'html.parser')


        # parse text

        preprocessed_words = " ".join(preprocess_words(soup)).encode('utf-8').decode('utf-8') 

        writer.add_document(url = url.encode('utf-8').decode('utf-8'), 
                            content = preprocessed_words, 
                            title = soup.title.text.encode('utf-8').decode('utf-8') )

        # add new links
        
        process_bar.update(1)
        
        for link in soup.find_all("a"):
            
            link_as_string : str = link['href']
            
            if not link_as_string.startswith(domain) and "www" in link_as_string:
                
                # go other page
                continue
            
            elif not link_as_string.startswith(domain):
                
                link_as_string = domain + link_as_string
    
            if link_as_string not in have_or_will_visit:
                
                if  len(have_or_will_visit) >= limit_page_visited:
                    continue
                
                have_or_will_visit.add(link_as_string)
                links.append(link_as_string)
                
                
    print(have_or_will_visit)
    writer.commit()
