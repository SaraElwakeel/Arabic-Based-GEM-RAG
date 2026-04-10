from __future__ import annotations

import re
from typing import List, Dict, Tuple

from src.config import SETTINGS
from src.retrieval.index_store import HybridIndexStore
from src.retrieval.ollama_client import OllamaClient
from src.schemas import ChunkRecord


GOOD_URL_HINTS = [
    "visit", "plan", "faq", "ticket", "tickets", "opening", "hours",
    "education", "facility", "facilities", "service", "services",
    "زيارة", "خطط", "مواعيد", "تعليمي", "تعليم", "مرافق", "خدمات", "تذاكر"
]

BAD_URL_HINTS = [
    "privacy", "policy", "cookie", "sustainability", "host-an-event",
    "legal", "terms", "event", "/search", "?query=",
    "الخصوصية", "سياسة", "الاستدامة", "بحث"
]

GOOD_CONTENT_TYPES = {
    "visit_info": 0.20,
    "services": 0.20,
    "facilities": 0.18,
    "education": 0.18,
    "faq": 0.15,
}

AR_STOPWORDS = {
    "ما", "ماذا", "كيف", "هل", "في", "من", "عن", "على", "إلى", "يوجد",
    "المتحف", "المصري", "الكبير"
}


class HybridRetriever:
    def __init__(self) -> None:
        self.store = HybridIndexStore()
        self.ollama = OllamaClient()
        self.chunks = self.store.load_chunks()

    def retrieve(self, question: str, top_k: int | None = None) -> List[Tuple[ChunkRecord, float]]:
        top_k = top_k or SETTINGS.top_k_final

        bm25_hits = self.store.bm25_search(question, SETTINGS.top_k_bm25)
        query_vec = self.ollama.embed([question])[0]
        vec_hits = self.store.vector_search(query_vec, SETTINGS.top_k_vector)

        merged: Dict[int, float] = {}
        self._merge_scores(merged, bm25_hits, weight=1.0)
        self._merge_scores(merged, vec_hits, weight=1.0)

        query_terms = self._extract_query_terms(question)

        rescored = []
        for idx, base_score in merged.items():
            chunk = self.chunks[idx]
            final_score = self._rerank_score(chunk, question, query_terms, base_score)
            rescored.append((idx, final_score))

        ranked = sorted(rescored, key=lambda x: x[1], reverse=True)

        results = []
        seen_urls = set()

        for idx, score in ranked:
            chunk = self.chunks[idx]
            if chunk.source_url in seen_urls:
                continue
            seen_urls.add(chunk.source_url)
            results.append((chunk, score))
            if len(results) >= top_k:
                break

        return results

    def _rerank_score(
        self,
        chunk: ChunkRecord,
        question: str,
        query_terms: List[str],
        base_score: float,
    ) -> float:
        score = base_score

        page_title = (chunk.page_title or "").lower()
        section_title = (chunk.section_title or "").lower()
        source_url = (chunk.source_url or "").lower()
        text = chunk.text or ""
        text_lower = text.lower()

        # Boost title/section overlap
        section_overlap = sum(1 for term in query_terms if term in section_title)
        page_overlap = sum(1 for term in query_terms if term in page_title)

        score += section_overlap * 0.28
        score += page_overlap * 0.16

        # Boost text overlap slightly
        text_overlap = sum(1 for term in query_terms if term in text_lower)
        score += min(text_overlap, 5) * 0.04

        # Boost useful content types
        score += GOOD_CONTENT_TYPES.get(chunk.content_type, 0.0)

        # URL hints
        if any(hint in source_url for hint in GOOD_URL_HINTS):
            score += 0.12

        if any(hint in source_url for hint in BAD_URL_HINTS):
            score -= 0.40

        # Slight preference for richer chunks
        text_len = len(text.strip())
        if 120 <= text_len <= 1200:
            score += 0.05
        elif text_len < 60:
            score -= 0.08

        return score

    @staticmethod
    def _extract_query_terms(question: str) -> List[str]:
        tokens = re.findall(r"[\w\u0600-\u06FF]+", question.lower())
        terms = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if token in AR_STOPWORDS:
                continue
            if len(token) < 2:
                continue
            terms.append(token)
        return list(dict.fromkeys(terms))

    @staticmethod
    def _merge_scores(bucket: Dict[int, float], hits: List[Tuple[int, float]], weight: float = 1.0) -> None:
        if not hits:
            return

        raw_scores = [score for _, score in hits]
        min_s, max_s = min(raw_scores), max(raw_scores)
        denom = (max_s - min_s) or 1.0

        for idx, score in hits:
            normalized = (score - min_s) / denom
            bucket[idx] = bucket.get(idx, 0.0) + (normalized * weight)