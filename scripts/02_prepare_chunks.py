from __future__ import annotations

from pathlib import Path

from src.config import CHUNKS_DIR, CLEANED_DIR, RAW_DIR
from src.processing.cleaner import PageCleaner
from src.processing.chunker import HeaderAwareChunker
from src.schemas import RawPage
from src.utils.io_utils import read_json, write_json, write_jsonl


def iter_raw_files():
    for museum_dir in RAW_DIR.iterdir():
        if museum_dir.is_dir():
            for file in museum_dir.glob("*.json"):
                yield file


def main() -> None:
    cleaner = PageCleaner()
    chunker = HeaderAwareChunker()

    all_chunks = []
    cleaned_pages = []

    for raw_file in iter_raw_files():
        raw_page = RawPage(**read_json(raw_file))
        clean_page = cleaner.clean_page(raw_page)
        cleaned_pages.append(clean_page.model_dump())
        chunks = chunker.chunk_page(clean_page)
        all_chunks.extend(chunk.model_dump() for chunk in chunks)

    write_jsonl(CLEANED_DIR / "clean_pages.jsonl", cleaned_pages)
    write_jsonl(CHUNKS_DIR / "chunks.jsonl", all_chunks)
    print(f"[INFO] Clean pages: {len(cleaned_pages)}")
    print(f"[INFO] Chunks: {len(all_chunks)}")


if __name__ == "__main__":
    main()
