from __future__ import annotations

from tqdm import tqdm

from src.config import CHUNKS_DIR
from src.retrieval.index_store import HybridIndexStore
from src.retrieval.ollama_client import OllamaClient
from src.schemas import ChunkRecord
from src.utils.io_utils import read_jsonl
from src.utils.text_utils import simple_tokenize


def main() -> None:
    rows = read_jsonl(CHUNKS_DIR / "chunks.jsonl")
    if not rows:
        raise FileNotFoundError("No chunks found. Run scripts/02_prepare_chunks.py first.")

    chunks = [ChunkRecord(**row) for row in rows]
    corpus = [chunk.text for chunk in chunks]
    tokenized = [simple_tokenize(text) for text in corpus]

    store = HybridIndexStore()
    store.save_chunks(chunks)
    store.save_bm25(tokenized)

    ollama = OllamaClient()
    batch_size = 16
    vectors = []
    for i in tqdm(range(0, len(corpus), batch_size), desc="Embedding chunks"):
        batch = corpus[i : i + batch_size]
        vectors.extend(ollama.embed(batch))
    store.save_vectors(vectors)

    print(f"[INFO] Indexed chunks: {len(chunks)}")
    print("[INFO] BM25 and vector indexes saved.")


if __name__ == "__main__":
    main()
