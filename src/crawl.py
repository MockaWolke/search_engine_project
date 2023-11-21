from . import SCHEMA, REPO_PATH, INDEXES_DIR
from whoosh.index import create_in
import requests
from tqdm import tqdm
from requests import ReadTimeout, TooManyRedirects, HTTPError, ConnectionError, Response
from bs4 import BeautifulSoup
import os
from typing import List, Optional
import numpy as np
from loguru import logger
from urllib.parse import urlparse, urljoin


def parse_domain_index(
    domain: str,
    index_dir: str,
    limit_page_visited,
    timeout=10,
    new_pages_limit: Optional[int] = 10,
    sample_by_length: bool = True,
    max_url_len: Optional[int] = 200,
):
    # check for empty directory
    if os.path.isdir(index_dir) and os.listdir(index_dir):
        raise ValueError(f"index_dir {index_dir} already exists and contains items.")

    os.makedirs(index_dir, exist_ok=True)

    # set up logging
    logger.add(os.path.join(index_dir, "logs.log"))

    logger.info(f"Start Parsing {domain} and saving sites to {index_dir}")

    # set index and writer
    writing_index = create_in(index_dir, SCHEMA)
    writer = writing_index.writer()

    try:
        succesfully_added = parse_links(
            domain,
            limit_page_visited,
            timeout,
            writer,
            new_pages_limit,
            sample_by_length,
            max_url_len,
        )
        logger.success(f"Saved {succesfully_added} pages to {index_dir}")

    except KeyboardInterrupt:
        logger.warning("Manual interrupt detected. Committing changes...")
    except Exception as e:
        logger.exception("An error occurred")
    finally:
        writer.commit()
        logger.info("Changes committed")


def get_domain(url):
    """Extract the domain from a URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc


def sample_weighted_by_len(
    links: List[str], k, with_weighting: bool = True
) -> List[str]:
    if k >= len(links):
        return links

    if not with_weighting:
        return np.random.choice(
            np.asarray(links),
            k,
            False,
        ).tolist()

    lenghts = np.array([len(s) for s in links])

    longest = np.max(lenghts)

    weights = np.log(longest - lenghts + 1) + 0.01

    weights /= weights.sum()

    return np.random.choice(np.asarray(links), k, False, weights).tolist()


def extract_text(soup: BeautifulSoup) -> str:
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Remove all links
    for a_tag in soup.find_all("a"):
        a_tag.extract()

    # Now get the text
    return soup.get_text()


to_utf8 = lambda x: x.encode("utf-8").decode("utf-8")


def parse_links(
    domain: str,
    limit_page_visited: int,
    timeout: int,
    writer,
    new_pages_limit: Optional[int] = 10,
    sample_by_length: bool = True,
    max_url_len: Optional[int] = 200,
):
    links = [domain]
    have_or_will_visit = {domain}
    process_bar = tqdm(range(limit_page_visited), f"Crawling the {domain} domain.")
    succesfully_added: int = 0

    main_domain = get_domain(domain)

    while len(links) > 0 and succesfully_added < limit_page_visited:
        url = links.pop()

        try:
            req = requests.get(url, timeout=timeout)
            req.raise_for_status()  # Raise an HTTPError for bad requests

        except (ReadTimeout, ConnectionError, TooManyRedirects, HTTPError) as e:
            logger.error(f"Request failed for {url}: {e}")
            continue

        soup = BeautifulSoup(req.content, "html.parser")

        # we first extract the next links

        possible_links = extract_next_links(
            domain, max_url_len, have_or_will_visit, main_domain, soup
        )

        # because here we delete all to receive the text

        text = extract_text(soup)

        logger.debug(f"Adding {url}")

        writer.add_document(
            url=to_utf8(url),
            content=to_utf8(text),
            title=to_utf8(soup.title.text),
        )

        # add new links

        process_bar.update(1)
        succesfully_added += 1

        if limit_page_visited is None:
            new_links = possible_links

        else:
            new_links = sample_weighted_by_len(
                possible_links, new_pages_limit, sample_by_length
            )

        have_or_will_visit.update(new_links)
        links.extend(new_links)

    return succesfully_added


def extract_next_links(domain, max_url_len, have_or_will_visit, main_domain, soup):
    possible_links = []

    for link in soup.find_all("a", href=True):
        link_url: str = link["href"]

        parsed_link = urlparse(link_url)
        stripped_link_url = parsed_link._replace(fragment="").geturl()

        if stripped_link_url == "":
            continue

        absolute_link_url = urljoin(domain, link_url)

        # Check if the link's domain is the same as the main domain
        if get_domain(absolute_link_url) != main_domain:
            continue

        if max_url_len is not None and len(absolute_link_url) > max_url_len:
            continue

        if ".php?" in absolute_link_url:
            continue

            # Check if the link has already been scheduled or visited
        if absolute_link_url not in have_or_will_visit:
            possible_links.append(absolute_link_url)
    return possible_links
