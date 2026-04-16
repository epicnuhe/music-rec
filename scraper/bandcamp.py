"""
Bandcamp Daily scraper.
Scrapes article listings from daily.bandcamp.com and pulls full article text.
Returns a list of raw text blocks for the extractor to process.
"""

import logging
import time

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

BASE_URL = "https://daily.bandcamp.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _get(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning("GET %s failed: %s", url, e)
        return None


def _scrape_article(url: str) -> dict | None:
    """Pull text content and author from a single Bandcamp Daily article."""
    r = _get(url)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "lxml")

    # Author byline
    author = None
    byline = soup.select_one(".byline-author, .author-name, [class*='byline'] a")
    if byline:
        author = byline.get_text(strip=True)

    # Article body text
    body_el = soup.select_one(
        "article, .article-body, [class*='editorial'], [class*='article-content']"
    )
    if not body_el:
        body_el = soup.find("main") or soup.find("body")

    text = body_el.get_text(separator="\n", strip=True) if body_el else ""
    if not text or len(text) < 100:
        return None

    return {"url": url, "author": author, "text": text[:8000]}  # cap to avoid huge prompts


def scrape() -> list[dict]:
    """
    Return a list of article dicts scraped from Bandcamp Daily.
    Each dict has: source_name, source_url, source_author, raw_text
    """
    results = []

    # Pull the main listing page
    r = _get(BASE_URL)
    if not r:
        log.error("Could not reach Bandcamp Daily main page")
        return results

    soup = BeautifulSoup(r.text, "lxml")

    # Find article links — Bandcamp Daily uses <a> tags inside article cards
    links = set()
    for a in soup.select("a[href]"):
        href = a["href"]
        if href.startswith("/"):
            href = BASE_URL + href
        if "daily.bandcamp.com" in href and href != BASE_URL:
            # Skip section/category pages — we want individual articles
            path = href.replace(BASE_URL, "")
            if path.count("/") >= 2 and "?" not in path:
                links.add(href)

    log.info("Bandcamp Daily: found %d article links", len(links))

    for url in list(links)[:20]:  # process up to 20 recent articles
        article = _scrape_article(url)
        if article:
            results.append({
                "source_name": "Bandcamp Daily",
                "source_url": article["url"],
                "source_author": article["author"],
                "raw_text": article["text"],
            })
        time.sleep(1)  # be polite

    log.info("Bandcamp Daily: scraped %d articles", len(results))
    return results
