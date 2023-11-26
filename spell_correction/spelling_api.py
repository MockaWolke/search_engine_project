import onnxruntime as ort

ort.set_default_logger_severity(3)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import pipeline
from search_engine import REPO_PATH
from loguru import logger
import uvicorn  # for pipreqs
import optimum  # for pipreqs
import requests
from bs4 import BeautifulSoup
import time
import os
from search_engine.crawl import extract_text


os.chdir(REPO_PATH)

logger.add("spell.log", rotation="5 MB")


tokenizer = AutoTokenizer.from_pretrained(
    REPO_PATH / "spellchecking_onnx",
)
model = ORTModelForSeq2SeqLM.from_pretrained(
    REPO_PATH / "spellchecking_onnx",
)
spelling_pipeline = pipeline(
    "text2text-generation", model=model, device="cpu", tokenizer=tokenizer
)


def fix(query: str) -> str:
    max_len = int(len(query) * 1.2)

    model_output = spelling_pipeline(query, max_new_tokens=max_len)

    return model_output[0]["generated_text"]


app = FastAPI()


class Query(BaseModel):
    text: str


@app.post("/fix_spelling/")
def api_fix_spelling(query: Query) -> str:
    try:
        start = time.time()
        response = fix(query.text)
        logger.info(
            f"Chagned '{query} to {response} - Took {time.time()-start :.4} seconds.'"
        )
        return response
    except Exception as e:
        logger.exception(f"Failed for {query}")
        raise HTTPException(status_code=500, detail=str(e))


class ReloadTextQuery(BaseModel):
    url: str
    timeout: int = 10  # Default timeout value


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
