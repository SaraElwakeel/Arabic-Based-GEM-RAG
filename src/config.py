from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEANED_DIR = DATA_DIR / "cleaned"
CHUNKS_DIR = DATA_DIR / "chunks"
INDEX_DIR = DATA_DIR / "index"
CACHE_DIR = DATA_DIR / "cache"

for path in [DATA_DIR, RAW_DIR, CLEANED_DIR, CHUNKS_DIR, INDEX_DIR, CACHE_DIR]:
    path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    import os

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/api")
    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:4b")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "qwen3-embedding")
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "25"))
    max_pages_per_site: int = int(os.getenv("MAX_PAGES_PER_SITE", "40"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k_bm25: int = int(os.getenv("TOP_K_BM25", "6"))
    top_k_vector: int = int(os.getenv("TOP_K_VECTOR", "6"))
    top_k_final: int = int(os.getenv("TOP_K_FINAL", "6"))
    use_playwright: bool = os.getenv("USE_PLAYWRIGHT", "false").lower() == "true"


SETTINGS = Settings()

MUSEUM_SITES = [
    {
        "museum_id": "gem",
        "museum_name": "Grand Egyptian Museum",
        "seed_url": "https://gem.eg/ar/",
        "allowed_domains": ["gem.eg", "www.gem.eg"],
        "allowed_prefixes": [
            "https://gem.eg/ar/",
            "https://www.gem.eg/ar/",
        ],
    }
]
