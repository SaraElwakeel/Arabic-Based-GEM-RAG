from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.schemas import AskRequest, AskResponse
from src.service.qa_service import MuseumQAService

app = FastAPI(title="Egyptian Museums RAG API", version="1.0.0")


@app.get("/")
def root() -> dict:
    return {"message": "Egyptian Museums RAG API is running."}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    try:
        service = MuseumQAService()
        return service.ask(payload.question, payload.top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=f"Missing index files. Build the corpus first. {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
