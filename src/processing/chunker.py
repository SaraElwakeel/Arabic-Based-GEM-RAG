from __future__ import annotations

import hashlib
from typing import List, Tuple

from src.config import SETTINGS
from src.schemas import ChunkRecord, CleanPage


class HeaderAwareChunker:
    def chunk_page(self, page: CleanPage) -> List[ChunkRecord]:
        text = page.text
        if not text:
            return []

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        sections = self._build_sections(lines, page)
        chunks: List[ChunkRecord] = []

        for section_title, section_text in sections:
            chunks.extend(self._chunk_section(page, section_title, section_text))

        return chunks

    def _build_sections(self, lines: List[str], page: CleanPage) -> List[Tuple[str, str]]:
        known_headings = set(h.strip() for h in page.headings if h and h.strip())

        sections: List[Tuple[str, List[str]]] = []
        current_title = page.page_title
        current_lines: List[str] = []

        for line in lines:
            if self._is_heading_line(line, known_headings):
                if current_lines:
                    sections.append((current_title, current_lines))
                current_title = line
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, current_lines))

        # fallback if no sections formed
        if not sections:
            sections = [(page.page_title, lines)]

        return [(title, "\n".join(section_lines)) for title, section_lines in sections]

    def _is_heading_line(self, line: str, known_headings: set[str]) -> bool:
        if line in known_headings:
            return True

        # short informative line likely to be a heading
        if len(line) <= 80 and len(line.split()) <= 8:
            # avoid treating sentences as headings
            if not line.endswith(("۔", ".", "؟", "!", ":", "،")):
                return True

        return False

    def _chunk_section(self, page: CleanPage, section_title: str, section_text: str) -> List[ChunkRecord]:
        chunk_size = SETTINGS.chunk_size
        overlap = SETTINGS.chunk_overlap

        if len(section_text) <= chunk_size:
            return [self._make_chunk(page, section_title, section_text, 0, len(section_text))]

        chunks: List[ChunkRecord] = []
        start = 0

        while start < len(section_text):
            end = min(len(section_text), start + chunk_size)

            # try not to cut in the middle of a line
            if end < len(section_text):
                newline_pos = section_text.rfind("\n", start, end)
                if newline_pos != -1 and newline_pos > start:
                    end = newline_pos

            chunk_text = section_text[start:end].strip()

            if chunk_text:
                chunks.append(self._make_chunk(page, section_title, chunk_text, start, end))

            if end >= len(section_text):
                break

            start = max(end - overlap, start + 1)

        return chunks

    def _make_chunk(
        self,
        page: CleanPage,
        section_title: str,
        chunk_text: str,
        start: int,
        end: int,
    ) -> ChunkRecord:
        chunk_id = hashlib.md5(
            f"{page.source_url}|{section_title}|{start}|{end}".encode("utf-8")
        ).hexdigest()

        return ChunkRecord(
            chunk_id=chunk_id,
            museum_id=page.museum_id,
            museum_name=page.museum_name,
            source_url=page.source_url,
            page_title=page.page_title,
            section_title=section_title,
            content_type=page.content_type,
            language=page.language,
            text=chunk_text,
        )