from __future__ import annotations

from typing import List, Dict, Any
import requests

from src.config import SETTINGS


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = SETTINGS.ollama_base_url.rstrip("/")
        self.timeout = SETTINGS.request_timeout * 3

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        response = requests.post(
            f"{self.base_url}/embed",
            json={"model": SETTINGS.ollama_embed_model, "input": texts},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"]

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "model": SETTINGS.ollama_chat_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return data["message"]["content"].strip()
