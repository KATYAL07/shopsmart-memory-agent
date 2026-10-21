# ShopSmart Memory Agent
> A personal retrieval-augmented generation (RAG) project by **Arnav Katyal**.

This project is a lightweight AI store assistant for a fictional e-commerce brand called ShopSmart. It retrieves relevant information from a local knowledge base before asking a language model to answer, so responses stay grounded in the supplied store data.

This is an independent personal project created and maintained by Arnav Katyal. The ShopSmart business, products, prices, orders, and policies are fictional workshop data.

## Features

- Overlapping text chunking for a small knowledge base
- Embeddings generated through OpenRouter
- Plain JSON vector memory instead of a vector database
- Cosine-similarity retrieval with configurable top-k results
- Grounded answers with chunk citations such as `[chunk-001]`
- Explicit fallback when the knowledge base does not support an answer
- Cached indexing that rebuilds when `kb.txt` changes

## Project structure

| File | Purpose |
| --- | --- |
| `memory_agent.py` | Indexing, retrieval, and interactive chat application |
| `web_app.py` | Local browser interface for the memory agent |
| `kb.txt` | Fictional ShopSmart knowledge base |
| `requirements.txt` | Python dependency list |
| `memory.json` | Generated local embedding index; ignored by Git |

## Requirements

- Python 3.10 or newer
- An OpenRouter API key

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Get an [OpenRouter](https://openrouter.ai/) API key and export it. Do not put the key in code or commit it.

```bash
export OPENROUTER_API_KEY="your-key"
```

Optional model overrides (both default to free OpenRouter models):

```bash
export OPENROUTER_EMBEDDING_MODEL="nvidia/nemotron-3-embed-1b:free"
export OPENROUTER_CHAT_MODEL="nvidia/nemotron-3.5-lightning:free"
```

## Run

```bash
python memory_agent.py
```

To use the browser interface locally:

```bash
python web_app.py
```

Open `http://localhost:8000` in your browser.

The first run indexes `kb.txt` and writes `memory.json`. Later runs reuse that file when the knowledge base and embedding model are unchanged.

```text
You: What is the return window for unused items?
```

Type `exit` to quit.

| Flag | Effect |
| --- | --- |
| `--reindex` | Rebuild `memory.json` from `kb.txt` |
| `--top-k N` | How many chunks to retrieve (default `3`) |

## How a question is answered

1. `kb.txt` is split into overlapping character chunks (500 characters, 60 overlap).
2. Each chunk is embedded and saved in `memory.json` with its text and chunk id.
3. The question is embedded and scored against every stored vector with cosine similarity.
4. The top matches are printed, then sent to the chat model as the only allowed context.
5. The model must cite chunk ids such as `[chunk-001]`, or say it could not find the answer in the knowledge base.

Try a question that is not in `kb.txt` to see the grounding behavior. `kb.txt` is fictional workshop data.

## License

Copyright (c) 2026 Arnav Katyal

This project is released under the [MIT License](LICENSE).
