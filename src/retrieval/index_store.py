from __future__ import annotations

import pickle
from typing import List, Tuple

import numpy as np
from rank_bm25 import BM25Okapi

from src.config import INDEX_DIR
from src.schemas import ChunkRecord
from src.utils.io_utils import read_jsonl, write_jsonl
from src.utils.text_utils import simple_tokenize

CHUNKS_PATH = INDEX_DIR / "indexed_chunks.jsonl"
BM25_PATH = INDEX_DIR / "bm25.pkl"
VECTORS_PATH = INDEX_DIR / "vectors.npy"
TOKENS_PATH = INDEX_DIR / "tokenized_corpus.pkl"


class HybridIndexStore:
    def save_chunks(self, chunks: List[ChunkRecord]) -> None:
        write_jsonl(CHUNKS_PATH, [chunk.model_dump() for chunk in chunks])

    def load_chunks(self) -> List[ChunkRecord]:
        return [ChunkRecord(**row) for row in read_jsonl(CHUNKS_PATH)]

    def save_bm25(self, tokenized_corpus: List[List[str]]) -> None:
        bm25 = BM25Okapi(tokenized_corpus)
        with BM25_PATH.open("wb") as f:
            pickle.dump(bm25, f)
        with TOKENS_PATH.open("wb") as f:
            pickle.dump(tokenized_corpus, f)

    def load_bm25(self) -> BM25Okapi:
        with BM25_PATH.open("rb") as f:
            return pickle.load(f)

    def save_vectors(self, vectors: List[List[float]]) -> None:
        arr = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        arr = arr / norms
        np.save(VECTORS_PATH, arr)

    def load_vectors(self) -> np.ndarray:
        return np.load(VECTORS_PATH)

    def vector_search(self, query_vector: List[float], top_k: int) -> List[Tuple[int, float]]:
        vectors = self.load_vectors()
        q = np.array(query_vector, dtype=np.float32)

        if q.ndim == 1:
            q = q.reshape(1, -1)

        q_norm = np.linalg.norm(q, axis=1, keepdims=True)
        q_norm[q_norm == 0] = 1.0
        q = q / q_norm

        scores = vectors @ q.T
        scores = scores.squeeze(axis=1)

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(i), float(scores[i])) for i in top_indices]

    def bm25_search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        bm25 = self.load_bm25()
        query_tokens = simple_tokenize(query)
        scores = bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(i), float(scores[i])) for i in top_indices]