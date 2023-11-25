import onnxruntime as ort

ort.set_default_logger_severity(3)

from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import pipeline
from search_engine import REPO_PATH
from typing import Tuple
import string
import re
import optimum

PUNCTUATION = set(string.punctuation)


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


def fix_spelling(query: str) -> Tuple[str, bool]:
    has_punctioation = any(i in PUNCTUATION for i in query)

    corrected = fix(query)

    if not has_punctioation:
        corrected = re.sub(r"[^\w\s?]", "", corrected)

    changed = query.lower() != corrected.lower()

    return corrected, changed
