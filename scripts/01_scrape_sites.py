from __future__ import annotations

from src.config import MUSEUM_SITES, RAW_DIR
from src.ingest.crawler import MuseumCrawler
from src.utils.io_utils import write_json


def main() -> None:
    crawler = MuseumCrawler()
    total = 0

    for site in MUSEUM_SITES:
        print(f"\n[INFO] Crawling: {site['museum_name']}")
        pages = crawler.crawl_site(site)

        museum_dir = RAW_DIR / site["museum_id"]
        museum_dir.mkdir(parents=True, exist_ok=True)

        for page in pages:
            filename = crawler.make_filename(page.source_url)
            write_json(museum_dir / filename, page.model_dump())

        print(f"[INFO] Saved {len(pages)} pages for {site['museum_name']}")
        total += len(pages)

    print(f"\n[INFO] Done. Total raw pages saved: {total}")


if __name__ == "__main__":
    main()