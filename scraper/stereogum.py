"""
Stereogum scraper.
Pulls from multiple category-specific RSS feeds rather than the noisy main feed.
Targets: reviews, album of the week, new music, and monthly genre columns.
Returns raw text blocks for the extractor.
"""

import logging
import time

import feedparser
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

BASE_URL = "https://www.stereogum.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Category-specific RSS feeds — each of these is already editorial/album-focused
CATEGORY_FEEDS = [
    "https://www.stereogum.com/category/reviews/feed/",
    "https://www.stereogum.com/category/album-of-the-week/feed/",
    "https://www.stereogum.com/category/new-music/feed/",
    "https://www.stereogum.com/category/lists/feed/",
    "https://www.stereogum.com/tag/this-month-in-electronic/feed/",
    "https://www.stereogum.com/tag/this-month-in-rap/feed/",
    "https://www.stereogum.com/tag/the-week-in-pop/feed/",
    "https://www.stereogum.com/tag/whats-good/feed/",
]

# Skip pure news/event articles — everything else is fair game
SKIP_KEYWORDS = [
    "tour dates", "dies at", "dead at", "passes away", "lawsuit",
    "arrest", "fired", "drama", "beef", "beef with", "announces tour",
    "tickets on sale", "festival lineup",
]


def _get(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning("GET %s failed: %s", url, e)
        return None


def _should_skip(entry) -> bool:
    title = (entry.get("title") or "").lower()
    return any(kw in title for kw in SKIP_KEYWORDS)


def _scrape_article(url: str, author: str | None) -> dict | None:
    r = _get(url)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "lxml")

    # Stereogum article body — try multiple selectors
    body_el = soup.select_one(
        ".article-body, .entry-content, [class*='post-content'], [class*='article-content']"
    )
    if not body_el:
        body_el = soup.find("article") or soup.find("main")

    text = body_el.get_text(separator="\n", strip=True) if body_el else ""
    if len(text) < 150:
        return None

    # Try to find author if not already known
    if not author:
        author_el = soup.select_one(
            ".author-name, .byline a, [rel='author'], [class*='author'] a"
        )
        if author_el:
            author = author_el.get_text(strip=True)

    return {"text": text[:8000], "author": author}


def _collect_entries_from_feed(feed_url: str) -> list[dict]:
    """Pull entries from a single RSS feed URL."""
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        log.debug("No entries from %s", feed_url)
        return []
    log.debug("%s: %d entries", feed_url, len(feed.entries))
    return feed.entries


def scrape() -> list[dict]:
    """
    Pull article text from Stereogum's category-specific feeds.
    Returns list of raw text blocks for the extractor.
    """
    results = []
    seen_urls = set()

    for feed_url in CATEGORY_FEEDS:
        entries = _collect_entries_from_feed(feed_url)

        for entry in entries[:15]:  # up to 15 per category feed
            if _should_skip(entry):
                continue

            url = entry.get("link") or entry.get("id")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

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

    log.info("Stereogum: scraped %d articles across %d category feeds",
             len(results), len(CATEGORY_FEEDS))
    return results
