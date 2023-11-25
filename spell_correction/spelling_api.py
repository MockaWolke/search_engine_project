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
import time
import os

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
