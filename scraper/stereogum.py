"""
Stereogum scraper.
Uses feedparser for the RSS feed, then fetches article body text.
Returns raw text blocks for the extractor.
"""

import logging
import time

import feedparser
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

RSS_URL = "https://www.stereogum.com/feed/"
BASE_URL = "https://www.stereogum.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# We want album reviews and editorial features, not news bullets
RELEVANT_KEYWORDS = [
    "album review", "review", "best albums", "album of the week",
    "premiere", "listen", "stream", "new album", "full album"
]


def _get(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning("GET %s failed: %s", url, e)
        return None


def _is_relevant(entry) -> bool:
    title = (entry.get("title") or "").lower()
    tags = [t.get("term", "").lower() for t in entry.get("tags", [])]
    combined = title + " " + " ".join(tags)
    return any(kw in combined for kw in RELEVANT_KEYWORDS)


def _scrape_article(url: str, author: str | None) -> dict | None:
    r = _get(url)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "lxml")

    # Stereogum article body
    body_el = soup.select_one(
        ".article-body, .entry-content, article .content, [class*='post-content']"
    )
    if not body_el:
        body_el = soup.find("article") or soup.find("main")

    text = body_el.get_text(separator="\n", strip=True) if body_el else ""
    if len(text) < 100:
        return None

    # Try to find author if not already known
    if not author:
        author_el = soup.select_one(".author, .byline, [rel='author']")
        if author_el:
            author = author_el.get_text(strip=True)

    return {"text": text[:8000], "author": author}


def scrape() -> list[dict]:
    """Return article text blocks from Stereogum RSS."""
    results = []
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        log.error("Stereogum RSS returned no entries")
        return results

    log.info("Stereogum: %d RSS entries found", len(feed.entries))

    for entry in feed.entries[:30]:  # process up to 30 recent entries
        if not _is_relevant(entry):
            continue

        url = entry.get("link") or entry.get("id")
        if not url:
            continue

        author = None
        if entry.get("authors"):
            author = entry["authors"][0].get("name")

        article = _scrape_article(url, author)
        if article:
            results.append({
                "source_name": "Stereogum",
                "source_url": url,
                "source_author": article["author"],
                "raw_text": article["text"],
            })
        time.sleep(0.5)

    log.info("Stereogum: scraped %d relevant articles", len(results))
    return results
