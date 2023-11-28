from fastapi import FastAPI, HTTPException, status
from loguru import logger
import requests
from bs4 import BeautifulSoup
import time
from search_engine.crawl import extract_text
from helper_api.spellchecker import fix_spelling
from helper_api.shemas import HealthCheck, Query, ReloadTextQuery

logger.add("helper_api.log", rotation="5 MB")

app = FastAPI()


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.post("/fix_spelling/")
def api_fix_spelling(query: Query) -> str:
    try:
        start = time.time()
        response = fix_spelling(query.text)
        logger.info(
            f"Chagned '{query} to {response} - Took {time.time()-start :.4} seconds.'"
        )
        return response
    except Exception as e:
        logger.exception(f"Failed for {query}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload_text/")
def request_page_and_get_text(query: ReloadTextQuery) -> dict:
    try:
        start_time = time.time()

        req = requests.get(query.url, timeout=query.timeout)
        req.raise_for_status()  # Raise an HTTPError for bad requests

        soup = BeautifulSoup(req.content, "html.parser")
        text = extract_text(soup)

        elapsed_time = time.time() - start_time
        logger.debug(f"Requesting {query.url} took {elapsed_time:.4f} seconds")

        return {"text": text, "success": True}
    except requests.RequestException as e:
        logger.error(f"Request failed for {query.url}: {e}")
        return {"text": "", "success": False, "error": str(e)}
    except Exception as e:
        logger.exception(f"An error occurred for {query.url}")
        raise HTTPException(status_code=500, detail=str(e))
