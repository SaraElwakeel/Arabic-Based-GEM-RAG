from typing import List

from bs4 import BeautifulSoup

from src.schemas import CleanPage, RawPage
from src.utils.text_utils import clean_text, classify_content_type, detect_language


BOILERPLATE_EXACT = {
    "سياسة الخصوصية",
    "الخصوصية",
    "privacy policy",
    "cookie policy",
    "cookies",
    "اشترك",
    "subscribe",
    "تابعنا",
    "follow us",
    "جميع الحقوق محفوظة",
    "all rights reserved",
    "اتصل بنا",
    "تواصل معنا",
    "contact us",
    "بحث",
    "search",
    "القائمة",
    "menu",
}

BOILERPLATE_CONTAINS = [
    "جميع الحقوق محفوظة",
    "all rights reserved",
    "privacy",
    "cookie",
    "newsletter",
    "subscribe",
    "تابعنا",
    "follow us",
    "مشاركة",
    "share",
    "facebook",
    "instagram",
    "youtube",
    "linkedin",
    "twitter",
    "whatsapp",
]


def is_arabic_heavy(text: str) -> bool:
    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    letters = sum(1 for ch in text if ch.isalpha())
    if letters == 0:
        return False
    return arabic_chars / letters >= 0.30


def is_low_value_line(line: str) -> bool:
    normalized = line.strip().lower()
    if not normalized:
        return True

    if normalized in BOILERPLATE_EXACT:
        return True

    if any(p in normalized for p in BOILERPLATE_CONTAINS):
        return True

    # very short fragments are usually bad navigation/menu leftovers
    if len(normalized) < 3:
        return True

    # weak one-word / tiny labels
    if len(normalized.split()) <= 2 and len(normalized) < 12:
        return True

    return False


class PageCleaner:
    def clean_page(self, raw_page: RawPage) -> CleanPage:
        soup = BeautifulSoup(raw_page.html, "lxml")

        raw_headings: List[str] = []
        seen_headings = set()

        for tag in soup.find_all(["h1", "h2", "h3"]):
            text = clean_text(tag.get_text(" ", strip=True))
            if not text:
                continue
            if is_low_value_line(text):
                continue
            if text in seen_headings:
                continue
            seen_headings.add(text)
            raw_headings.append(text)

        lines = []
        seen_lines = set()

        for line in raw_page.text.splitlines():
            cleaned_line = clean_text(line)
            if not cleaned_line:
                continue
            if is_low_value_line(cleaned_line):
                continue
            if cleaned_line in seen_lines:
                continue
            seen_lines.add(cleaned_line)
            lines.append(cleaned_line)

        # fallback: if filtering was too aggressive, keep original cleaned text
        if lines:
            cleaned_text = "\n".join(lines)
        else:
            cleaned_text = clean_text(raw_page.text)

        content_type = classify_content_type(cleaned_text, raw_page.page_title)
        language = detect_language(cleaned_text)

        return CleanPage(
            museum_id=raw_page.museum_id,
            museum_name=raw_page.museum_name,
            source_url=raw_page.source_url,
            page_title=raw_page.page_title,
            headings=raw_headings[:15],
            text=cleaned_text,
            content_type=content_type,
            language=language,
        )