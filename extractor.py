"""
Claude-powered album extractor.
Takes raw text from a scraper result and returns structured album data.
Stores new albums in the database (deduplicating by artist + title).
"""

import json
import logging
import os

import anthropic

import database as db

log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """\
You are a music data extraction assistant. Extract all album and artist mentions \
from the provided content. Return a JSON array where each item has:
  artist          (string)
  album_title     (string)
  year            (integer or null)
  country         (string or null — country or scene of origin)
  genre_tags      (array of strings)
  curatorial_context (the editor's description of the album, verbatim or closely \
paraphrased — NOT your own words. Must come from the source text.)
  source_author   (string or null — the bylined author if present)

Rules:
- Only include albums that are clearly the editorial focus, not passing references.
- curatorial_context must reflect what the human editor actually wrote.
- If a field is unknown, use null.
- Return ONLY the JSON array, no other text or markdown fences.\
"""


def extract_albums_from_text(raw_text: str, source_meta: dict) -> list[dict]:
    """
    Call Claude to extract albums from a raw text block.
    source_meta must have: source_name, source_url, source_author
    Returns list of album dicts ready for database insertion.
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return []

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_text}],
        )
        raw_json = message.content[0].text.strip()

        # Strip accidental markdown fences
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
            raw_json = raw_json.strip()

        albums = json.loads(raw_json)
        if not isinstance(albums, list):
            return []

    except (json.JSONDecodeError, anthropic.APIError, IndexError) as e:
        log.warning("Extraction failed for %s: %s", source_meta.get("source_url"), e)
        return []

    results = []
    for album in albums:
        artist = (album.get("artist") or "").strip()
        title = (album.get("album_title") or "").strip()
        if not artist or not title:
            continue

        # Use source_author from scraper if Claude didn't find one
        if not album.get("source_author") and source_meta.get("source_author"):
            album["source_author"] = source_meta["source_author"]

        album_data = {
            "artist": artist,
            "album_title": title,
            "year": album.get("year"),
            "country": album.get("country"),
            "genre_tags": album.get("genre_tags") or [],
            "source_name": source_meta["source_name"],
            "source_url": source_meta["source_url"],
            "source_author": album.get("source_author"),
            "curatorial_context": album.get("curatorial_context"),
        }

        if db.album_exists(artist, title):
            db.increment_times_seen(artist, title)
            log.debug("Already known: %s — %s (bumped times_seen)", artist, title)
        else:
            new_id = db.insert_album(album_data)
            album_data["id"] = new_id
            results.append(album_data)
            log.info("New album: %s — %s (id %d)", artist, title, new_id)

    return results


def run_extraction(scraped_items: list[dict]) -> int:
    """
    Process a list of scraper result dicts through Claude extraction.
    Returns total number of new albums stored.
    """
    total_new = 0
    for item in scraped_items:
        new_albums = extract_albums_from_text(
            item["raw_text"],
            {
                "source_name": item["source_name"],
                "source_url": item["source_url"],
                "source_author": item.get("source_author"),
            },
        )
        total_new += len(new_albums)
    return total_new
