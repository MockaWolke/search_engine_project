import requests
import flask
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import nltk
from tqdm import tqdm

nltk.download('stopwords',download_dir= "stopwords_dir")


from nltk.corpus import stopwords


STOP_WORDS = set(word.lower() for word in stopwords.words('english'))


def preprocess_words(soup):
    
    words = set()
    
    for word in soup.text.lower().split():
        
        word : str = word
        if re.match("^[a-zA-Z]+$", word) and word not in STOP_WORDS:
            words.add(word)
            
    return words


def parse_domain(domain, limit_page_visited):
    
    links = [domain]
    have_or_will_visit = set()

    words_to_links = defaultdict(set)

    process_bar = tqdm(range(limit_page_visited), f"Crawling the {domain} domain.")
    
    
    while links:
    
        url = links.pop()
        
        req = requests.get(url, timeout=3)
        soup = BeautifulSoup(req.content, 'html.parser')


        # parse text


        for word in preprocess_words(soup):
            
            words_to_links[word].add(url)

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
                
                
            
    return words_to_links


def search(list_of_words, words_to_links):
    
    first_word = list_of_words[0]
    word = first_word.lower()
    
    if word not in words_to_links:
        
        print(f"{word} is not inside our index. Cant find match!")
        return
    
    words_mathed_with_all = words_to_links[word]
    
    for word in list_of_words[1:]:
        
        word = word.lower()
        
        if word not in words_to_links:
            
            print(f"{word} is not inside our index. Cant find match!")
            return
        
        words_mathed_with_all.intersection_update( words_to_links[word])
        
    return words_mathed_with_all
       



