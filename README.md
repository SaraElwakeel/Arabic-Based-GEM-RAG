# Grand Egyptian Museum (GEM) Arabic Website QA System

A fully local Arabic Question Answering system built specifically for the **official Grand Egyptian Museum (GEM) website**.

This project retrieves information only from the **official Arabic pages of GEM**, then answers user questions in **Arabic only** using a local Retrieval-Augmented Generation (RAG) pipeline powered by **Ollama**.

---

## Project Scope

This project is **strictly limited** to:

- **Grand Egyptian Museum (GEM) only**
- **Arabic question answering only**
- **Official GEM website content only**
- **Fully local execution**
- **No paid APIs**
- **No external web search**
- **No general knowledge fallback**
- **No guessing**

### Important Note

Earlier development versions of the project included experiments with content from other museum websites.  
The current version has been **restricted and rebuilt to support GEM only**.

The following are **not included** in the final system scope:

- Egyptian Museum in Tahrir
- National Museum of Egyptian Civilization (NMEC)
- Any non-GEM website
- Any external knowledge source

---

## Features

- Arabic-only QA interface
- Retrieval from official GEM Arabic website pages only
- Hybrid retrieval:
  - BM25 keyword retrieval
  - Local vector retrieval
- Local embeddings via Ollama
- Local answer generation via Ollama
- Clean Streamlit GUI
- Retrieved source display under each answer
- Strict grounded prompting
- Controlled fallback when information is not clearly supported

---

## Tech Stack

### Programming Language
- Python

### Retrieval / NLP
- BeautifulSoup
- rank-bm25
- Local vector embeddings via Ollama
- Local generation via Ollama

### Interface
- CLI
- Streamlit GUI
- FastAPI-ready project structure

### Local Models
- **Chat model:** `qwen3:4b`
- **Embedding model:** `qwen3-embedding:0.6b-fp16`

### Local Runtime
- Ollama running locally on:
  - `127.0.0.1:11434`

---

## Project Structure

```text
museum_rag_project/
│
├── app/
│   ├── rag_core.py
│   └── streamlit_app.py
│
├── scripts/
│   ├── 01_scrape_sites.py
│   ├── 02_prepare_chunks.py
│   ├── 03_build_indexes.py
│   └── 04_ask_cli.py
│
├── src/
│   ├── config.py
│   ├── retrieval/
│   ├── service/
│   ├── generation/
│   └── ...
│
├── data/
├── indexes/
├── requirements.txt
└── README.md
