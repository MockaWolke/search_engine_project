# Our Search Engine

## Installation

To install the required packages, run:

```bash
pip install -r requirements.txt
pip install -e .
```

## Features

### 1. Crawling

- The crawling code is located in `search_engine/crawl.py`. We have wrapped it in `utils/crawl_page.py` for easy usage. To add a new index, use:

`python script utils/crawl_page.py -d some_domain.de -s index_name -t number_of_websites `

The crawler is limited to the specified domain and tries to find `-t` total valid pages. We have implemented nuances to improve efficiency, such as limiting the number of new pages per single page, bias towards shorter URLs, and ignoring PHP pages. The pages are then added to a Whoosh index.

- Configuration, including the current index, can be set in `.env` files. Set `CURRENT_INDEX` to your desired index.

- Three small Wikipedia indexes are provided in `indexes.zip`, which can be unzipped using `utils/unzip.py`.

### 2. Start Page

- The start page allows users to choose the page size. The "search" button is disabled until an input is provided. It also features flowfields in the background implemented with JavaScript.

### 3. Querying

- We first search for pages matching all query tokens. If insufficient results are found, an "or" query is executed, displaying missing tokens. Results are sorted by the fewest missing tokens.

- If no results are found, a search retry page is provided.

#### Argument Validation

- Queries are validated using a dataclass. For invalid inputs (like a pagesize of 0 or empty queries), an error page with informative messages is displayed.

#### Spellchecking

- We use Huggingface's "oliverguhr/spelling-correction-english-base" model, a text2text transformer based on Microsoft's Bard.

- To quickly run it on VMs, we converted the model to ONNX format and run it using the CPU-optimized ONNX runtime. Use the following command to download and convert the model:

`` optimum-cli export onnx --model oliverguhr/spelling-correction-english-base --optimize O1 spellchecking_onnx/`  ``

- Due to compatibility issues with the Apache runtime, we created a small "helper_api" using Uvicorn and FastAPI.

- To run it, use:

Ensure that this port corresponds to `SPELL_PORT` set in the `.env`.

#### Highlighting

- We encountered similar issues when reloading URLs for highlighting. Since we did not store complete texts during crawling, we had to resend requests, which was not feasible with the Apache runtime. Therefore, we shifted this to the helper API.

- The highlighting mechanism scans the text for a window of width `WORD_WINDOW_LENGTH` (set in `.env`) and displays the window with the highest occurrence of matched terms.

## Logging and Hyperparameters

- Logging is implemented using Loguru, with logs saved in `api.log` and `helper_api.log`.

- In `search_engine/__init__.py`, you can see that various settings, like the timeout for the helper API and other hyperparameters, are controlled via the `.env` file.

## Testing

- For easier development and deployment, we wrote several Pytest tests, which can be run with:

`pytest -W ignore`
