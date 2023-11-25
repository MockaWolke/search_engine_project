## Install

`pip install -e .`

`optimum-cli export onnx --model oliverguhr/spelling-correction-english-base --optimize O1 spellchecking_onnx/`

`python unzip.py`

`uvicorn spelling_api:app --host 0.0.0.0 --port 8008`

## Test

Then hopefully this work.

`pytest -W ignore`
