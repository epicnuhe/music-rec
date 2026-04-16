"""
NTS Radio scraper.
NTS is a React SPA, so we scrape what the server renders — primarily show
listings and episode description pages. Content may be partial; that is OK.
Returns raw text blocks for the extractor.
"""

import logging
import time

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

BASE_URL = "https://www.nts.live"
SHOWS_URL = "https://www.nts.live/shows"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# NTS also provides a public API endpoint for recent episodes
NTS_API_RECENT = "https://www.nts.live/api/v2/latest?limit=20"


def _get(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning("GET %s failed: %s", url, e)
        return None


def _scrape_via_api() -> list[dict]:
    """Try to pull recent episode data from NTS's public API."""
    results = []
    r = _get(NTS_API_RECENT)
    if not r:
        return results

    try:
        data = r.json()
        results_list = data if isinstance(data, list) else data.get("results", [])
        for ep in results_list:
            # NTS API episode shape varies — extract what we can
            name = ep.get("name", "")
            description = ep.get("description", "")
            host = ep.get("broadcast", {}).get("created_by", "") if isinstance(ep.get("broadcast"), dict) else ""
            show_alias = ep.get("show_alias", "")
            episode_url = f"{BASE_URL}/shows/{show_alias}" if show_alias else BASE_URL

            text = f"{name}\n{description}".strip()
            if len(text) > 50:
                results.append({
                    "source_name": "NTS Radio",
                    "source_url": episode_url,
                    "source_author": host or None,
                    "raw_text": text[:6000],
                })
    except Exception as e:
        log.warning("NTS API parse error: %s", e)

    return results


def _scrape_via_html() -> list[dict]:
    """Fallback: scrape the NTS shows page HTML directly."""
    results = []
    r = _get(SHOWS_URL)
    if not r:
        return results

    soup = BeautifulSoup(r.text, "lxml")
    # Try to find show description blocks
    for block in soup.select("[class*='show'], [class*='episode'], article")[:30]:
        text = block.get_text(separator="\n", strip=True)
        if len(text) > 80:
            results.append({
                "source_name": "NTS Radio",
                "source_url": SHOWS_URL,
                "source_author": None,
                "raw_text": text[:4000],
            })

    return results


def scrape() -> list[dict]:
    """Return a list of NTS episode/show text blocks."""
    results = _scrape_via_api()
    if not results:
        log.info("NTS API returned nothing — falling back to HTML scrape")
        results = _scrape_via_html()

    log.info("NTS Radio: gathered %d content blocks", len(results))
    return results
