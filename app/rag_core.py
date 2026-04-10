from __future__ import annotations

from typing import Any, Dict, List

from src.service.qa_service import MuseumQAService

_service: MuseumQAService | None = None


def get_service() -> MuseumQAService:
    """Lazily create and reuse the existing QA service."""
    global _service
    if _service is None:
        _service = MuseumQAService()
    return _service



def _safe_get(obj: Any, attr: str, default: Any = "") -> Any:
    return getattr(obj, attr, default)



def normalize_sources(raw_sources: List[Any]) -> List[Dict[str, str]]:
    """Convert service source objects into a Streamlit-friendly dict format."""
    seen = set()
    normalized: List[Dict[str, str]] = []

    for src in raw_sources or []:
        page_title = _safe_get(src, "page_title", "") or ""
        section_title = _safe_get(src, "section_title", "") or ""
        source_url = _safe_get(src, "source_url", "") or ""

        key = (page_title, section_title, source_url)
        if key in seen:
            continue
        seen.add(key)

        normalized.append(
            {
                "page_title": page_title,
                "section_title": section_title,
                "source_url": source_url,
            }
        )

    return normalized



def answer_question(question: str) -> Dict[str, Any]:
    """
    Shared entry point for Streamlit and any future UI layer.
    Reuses the current GEM QA pipeline through MuseumQAService.
    """
    question = question.strip()

    if not question:
        return {"answer": "من فضلك اكتب سؤالًا بالعربية.", "sources": []}

    service = get_service()
    result = service.ask(question)

    return {
        "answer": _safe_get(result, "answer", ""),
        "sources": normalize_sources(_safe_get(result, "sources", [])),
    }
