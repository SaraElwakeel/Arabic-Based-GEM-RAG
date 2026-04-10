from __future__ import annotations

from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.ollama_client import OllamaClient
from src.schemas import AskResponse, SourceItem
from src.service.prompt_builder import SYSTEM_PROMPT, build_user_prompt


class MuseumQAService:
    def __init__(self) -> None:
        self.retriever = HybridRetriever()
        self.ollama = OllamaClient()

    def ask(self, question: str, top_k: int | None = None) -> AskResponse:
        contexts = self.retriever.retrieve(question=question, top_k=top_k)
        user_prompt = build_user_prompt(question, contexts)
        answer = self.ollama.chat(
        SYSTEM_PROMPT,
        user_prompt + "\n\nتذكير: يجب أن تكون الإجابة النهائية بالعربية فقط."
)

        sources = [
            SourceItem(
                museum_id=chunk.museum_id,
                museum_name=chunk.museum_name,
                page_title=chunk.page_title,
                source_url=chunk.source_url,
                section_title=chunk.section_title,
                score=round(score, 4),
                text_preview=chunk.text[:220] + ("..." if len(chunk.text) > 220 else ""),
            )
            for chunk, score in contexts
        ]

        return AskResponse(
            answer=answer,
            sources=sources,
            retrieved_context_count=len(contexts),
        )