from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RawPage(BaseModel):
    museum_id: str
    museum_name: str
    source_url: str
    page_title: str
    html: str
    text: str
    fetched_at: str


class CleanPage(BaseModel):
    museum_id: str
    museum_name: str
    source_url: str
    page_title: str
    headings: List[str] = Field(default_factory=list)
    text: str
    content_type: str = "general"
    language: str = "ar"


class ChunkRecord(BaseModel):
    chunk_id: str
    museum_id: str
    museum_name: str
    source_url: str
    page_title: str
    section_title: str
    content_type: str
    language: str = "ar"
    text: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["ما مواعيد زيارة المتحف القومي للحضارة المصرية؟"])
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class SourceItem(BaseModel):
    museum_id: str
    museum_name: str
    page_title: str
    source_url: str
    section_title: str
    score: float
    text_preview: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    retrieved_context_count: int