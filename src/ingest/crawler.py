from __future__ import annotations

import hashlib
import time
from collections import deque
from datetime import datetime, timezone
from turtle import title
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag, parse_qsl, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup

from src.config import SETTINGS
from src.schemas import RawPage
from src.utils.text_utils import clean_text


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

DROP_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid"
}

BLOCKED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar",
    ".mp4", ".mp3"
)


class MuseumCrawler:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def crawl_site(self, site_config: Dict) -> List[RawPage]:
        seed_url = self._normalize_url(site_config["seed_url"])
        allowed_domains = {self._normalize_domain(d) for d in site_config["allowed_domains"]}
        allowed_prefixes = tuple(self._normalize_url(p) for p in site_config["allowed_prefixes"])
        museum_id = site_config["museum_id"]
        museum_name = site_config["museum_name"]

        queue: deque[str] = deque([seed_url])
        visited: Set[str] = set()
        pages: List[RawPage] = []

        while queue and len(pages) < SETTINGS.max_pages_per_site:
            url = self._normalize_url(queue.popleft())

            if not url or url in visited:
                continue
            if not self._is_allowed(url, allowed_domains, allowed_prefixes):
                continue

            visited.add(url)

            try:
                html, final_url = self._fetch_html(url)
                final_url = self._normalize_url(final_url)

                if not html:
                    continue
                if not self._is_allowed(final_url, allowed_domains, allowed_prefixes):
                    print(f"[SKIP] Redirected outside allowed scope: {url} -> {final_url}")
                    continue

                title, text, links = self._extract_page_data(html, final_url)

                if len(text) < 120:
                    print(f"[SKIP] Too little text: {final_url}")
                    continue

                pages.append(
                    RawPage(
                        museum_id=museum_id,
                        museum_name=museum_name,
                        source_url=final_url,
                        page_title=title or museum_name,
                        html=html,
                        text=text,
                        fetched_at=datetime.now(timezone.utc).isoformat(),
                    )
                )
                print(f"[OK] {museum_name}: {final_url}")

                for link in links:
                    normalized = self._normalize_url(link)
                    if (
                        normalized
                        and normalized not in visited
                        and self._is_allowed(normalized, allowed_domains, allowed_prefixes)
                    ):
                        queue.append(normalized)

                time.sleep(0.6)

            except Exception as exc:
                print(f"[WARN] Failed: {url} -> {exc}")

        return pages

    def _fetch_html(self, url: str) -> tuple[str, str]:
        response = self.session.get(
            url,
            timeout=SETTINGS.request_timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return response.text, response.url

    def _extract_page_data(self, html: str, base_url: str) -> Tuple[str, str, List[str]]:
        soup = BeautifulSoup(html, "lxml")

    # Remove clearly useless tags
        for tag in soup(["script", "style", "noscript", "svg", "iframe", "form"]):
            tag.decompose()

    # Remove obvious layout/boilerplate regions
        for tag in soup.find_all(["header", "footer", "nav", "aside"]):
            tag.decompose()

        boilerplate_keywords = [
            "footer", "header", "navbar", "nav", "menu", "submenu",
        "breadcrumb", "social", "share", "newsletter", "subscribe",
        "cookie", "policy", "popup", "modal", "search", "lang-switcher"
    ]

        for tag in soup.find_all(True):
            attrs = " ".join(
                str(x) for x in [
                    tag.get("id", ""),
                    " ".join(tag.get("class", []))
            ]
        ).lower()

        if any(keyword in attrs for keyword in boilerplate_keywords):
            tag.decompose()

        title = clean_text(soup.title.get_text(" ", strip=True) if soup.title else "")

    # Try to find the main content container
        main_container = None

        candidates = []
        if soup.main:
            candidates.append(soup.main)
        if soup.article:
            candidates.append(soup.article)

        candidates.extend(
            soup.find_all(
                ["div", "section"],
                attrs={
                    "class": lambda x: x and any(
                        kw in " ".join(x).lower()
                        for kw in ["content", "main", "article", "page", "post", "entry", "section"]
                )
            }
        )
    )

        candidates.extend(
            soup.find_all(
                ["div", "section"],
                attrs={
                    "id": lambda x: x and any(
                        kw in x.lower()
                        for kw in ["content", "main", "article", "page", "post", "entry", "section"]
                )
            }
        )
    )

    # Choose the candidate with the most useful text
        best_text_len = 0
        for candidate in candidates:
            pieces = []
            for tag in candidate.find_all(["h1", "h2", "h3", "p", "li"]):
                piece = clean_text(tag.get_text(" ", strip=True))
                if piece and len(piece) > 2:
                    pieces.append(piece)
            joined = "\n".join(pieces)
            if len(joined) > best_text_len:
                best_text_len = len(joined)
                main_container = candidate

        container = main_container if main_container else (soup.body or soup)

        text_parts = []
        seen = set()

        for tag in container.find_all(["h1", "h2", "h3", "p", "li"]):
            piece = clean_text(tag.get_text(" ", strip=True))
            if not piece or len(piece) < 3:
                continue
            if piece in seen:
                continue
            seen.add(piece)
            text_parts.append(piece)

        text = "\n".join(text_parts)

        links = []
        seen_links = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href:
                continue
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue

            full_url = urljoin(base_url, href)
            if full_url.lower().endswith(BLOCKED_EXTENSIONS):
                continue

            normalized = self._normalize_url(full_url)
            if normalized and normalized not in seen_links:
                seen_links.add(normalized)
                links.append(normalized)

        return title, text, links

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        domain = domain.lower().strip()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    @staticmethod
    def _normalize_url(url: str) -> str:
        if not url:
            return ""

        url, _ = urldefrag(url)
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return ""

        query = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k not in DROP_QUERY_KEYS
        ]

        normalized = parsed._replace(query=urlencode(query, doseq=True))
        url = urlunparse(normalized)

        if url.endswith("/"):
            url = url.rstrip("/")

        return url

    @classmethod
    def _is_allowed(cls, url: str, allowed_domains: Set[str], allowed_prefixes: Tuple[str, ...]) -> bool:
        parsed = urlparse(url)
        netloc = cls._normalize_domain(parsed.netloc)

        if netloc not in allowed_domains:
            return False

        return any(url.startswith(prefix.rstrip("/")) for prefix in allowed_prefixes)

    @staticmethod
    def make_filename(url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest() + ".json"