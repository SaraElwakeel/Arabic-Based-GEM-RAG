# Egyptian Museums RAG (Local + Ollama)

A fully local Retrieval-Augmented Generation project for answering questions about major museums in Egypt from official museum websites.

## Features
- Local LLM and embeddings through Ollama
- Arabic-friendly website QA pipeline
- Museum-focused crawling from official websites
- Hybrid retrieval: BM25 + vector similarity
- FastAPI endpoint and CLI tester
- Source citations in the final answer

## Target websites
- GEM: https://gem.eg/ar/
- Egyptian Museum in Tahrir (MOTA): https://mota.gov.eg/ar/%D8%A7%D9%84%D8%A2%D8%AB%D8%A7%D8%B1-%D9%88%D8%A7%D9%84%D9%85%D8%AA%D8%A7%D8%AD%D9%81/%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%B3-%D8%A7%D9%84%D8%A3%D8%B9%D9%84%D9%89-%D9%84%D9%84%D8%A2%D8%AB%D8%A7%D8%B1/%D8%AF%D9%84%D9%8A%D9%84-%D9%85%D8%AA%D8%A7%D8%AD%D9%81-%D8%A7%D9%84%D8%A2%D8%AB%D8%A7%D8%B1-%D8%A7%D9%84%D9%85%D9%81%D8%AA%D9%88%D8%AD%D8%A9-%D9%84%D9%84%D8%B2%D9%8A%D8%A7%D8%B1%D8%A9-%D8%AC%D8%AF%D9%8A%D8%AF/%D8%A7%D9%84%D9%85%D8%AA%D8%AD%D9%81-%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A-%D8%A8%D8%A7%D9%84%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1/
- NMEC: https://nmec.gov.eg/ar/

## 1) Install
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

If you want Playwright fallback for dynamic pages:
```bash
playwright install
```

## 2) Start Ollama and pull models
```bash
ollama serve
ollama pull qwen3:4b
ollama pull qwen3-embedding
```

## 3) Build the corpus and indexes
```bash
python scripts/01_scrape_sites.py
python scripts/02_prepare_chunks.py
python scripts/03_build_indexes.py
```

## 4) Test from CLI
```bash
python scripts/04_ask_cli.py
```

## 5) Run the API
```bash
uvicorn src.api.main:app --reload
```
Open: http://127.0.0.1:8000/docs

## Project structure
```text
museum_rag_project/
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── chunks/
│   ├── index/
│   └── cache/
├── scripts/
├── src/
│   ├── api/
│   ├── ingest/
│   ├── processing/
│   ├── retrieval/
│   ├── service/
│   └── utils/
├── .env.example
├── requirements.txt
└── README.md
```

## Notes
- The scraper is conservative and stays inside the target sites.
- Some official pages may block simple requests. If that happens, set `USE_PLAYWRIGHT=true` in `.env`.
- The system is grounded: if the answer is not found in retrieved content, it should say so.

## API example
POST `/ask`
```json
{
  "question": "ما مواعيد زيارة المتحف القومي للحضارة المصرية؟"
}
```

## Suggested next improvements
- Add better Arabic reranking
- Add page type classification (tickets / hours / exhibits / contact)
- Add source freshness checks and recrawling schedule
