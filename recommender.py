"""
Recommendation engine.
Every Sunday evening: pulls the candidate pool, asks Claude to select
5 albums across the slot structure, and saves the result as a pending digest.
"""

import datetime
import json
import logging
import os


class _DateEncoder(json.JSONEncoder):
    """Makes datetime.date objects JSON-serialisable (PostgreSQL returns them as objects)."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

import anthropic

import database as db
from profile import TASTE_PROFILE

log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

RECOMMENDATION_SYSTEM = f"""\
You are a music recommendation engine with a deep understanding of a specific listener's \
taste profile. Your job is to select 5 albums from the candidate pool for this week's digest, \
following the slot structure precisely.

{TASTE_PROFILE}

SLOT STRUCTURE:
- Slot 1 (historical_deep_cut): Pre-2000 album. From a scene the listener has some fluency in. \
Must have strong curatorial framing from a named human editor. Never the obvious entry point.
- Slot 2 (contemporary_stretch): Post-2000. Highest discovery risk. No genre restrictions. \
Something genuinely interesting from the sources this week — shares only partial DNA with the \
taste profile. Explicitly note what partial overlap makes this a considered stretch, not random. \
If older_decade_requested is TRUE, pick a pre-2000 album for this slot instead.
- Slot 3 (world_music): From the designated region passed in the user message. IMPORTANT: You are \
NOT limited to the candidate pool for this slot. Draw freely on your knowledge of music from \
the designated region — any era, any release date. Pick the single most compelling album from \
that region and tradition that fits this listener's profile. If a strong candidate exists in \
the pool, use it. Otherwise, recommend from your own knowledge. For the curatorial_framing, \
draw on your knowledge of how the album has been received critically, its cultural context, \
and why it matters — write it in the voice of a knowledgeable human curator. Always include \
a world_music_context note explaining the tradition or scene briefly.
- Slot 4 (lighter_pick_1): Profile-matched for easier listen qualities. Must be editorially sourced.
- Slot 5 (lighter_pick_2): Same as Slot 4. Must be a different genre from Slot 4.

CONSTRAINTS:
- Never recommend albums already in the recommendation history.
- No genre clustering across the 5 picks.
- For Slots 1, 2, 4, 5: pick from the candidate pool only, and only albums with curatorial_context.
- For Slot 3: pool or your own knowledge — your call based on what's strongest.
- Apply appropriate listener_flags from this list where relevant:
    demanding_listen, lyrically_driven, significant_critical_reputation, immediate_listen, world_music_context

For the world_music slot, if you are recommending from your own knowledge (not the pool), \
set album_id to null and include a new_album object with full details.

Return a JSON object with this exact structure (no markdown, no extra text):
{{
  "picks": [
    {{
      "album_id": <integer from the candidate pool, or null for world_music picks from your knowledge>,
      "new_album": {{
        "artist": "...", "album_title": "...", "year": 1990, "country": "...",
        "genre_tags": ["..."], "curatorial_context": "...", "source_author": "your knowledge"
      }},
      "slot": "historical_deep_cut" | "contemporary_stretch" | "world_music" | "lighter_pick_1" | "lighter_pick_2",
      "recommendation_rationale": "<why this album for this slot, 2-3 sentences>",
      "listener_flags": ["demanding_listen", ...],
      "curatorial_framing": "<1-2 sentences in curator voice>",
      "world_music_context": "<brief note on tradition/scene, only for world_music slot>"
    }},
    ...
  ],
  "world_region_used": "<region name used for Slot 3>"
}}
"""


def build_candidate_summary(candidates: list[dict]) -> str:
    """Serialize candidates into a compact JSON block for the prompt."""
    slim = []
    for a in candidates:
        slim.append({
            "id": a["id"],
            "artist": a["artist"],
            "album_title": a["album_title"],
            "year": a.get("year"),
            "country": a.get("country"),
            "genre_tags": a.get("genre_tags"),
            "source_name": a.get("source_name"),
            "source_author": a.get("source_author"),
            "curatorial_context": (a.get("curatorial_context") or "")[:400],
            "times_seen": a.get("times_seen", 1),
        })
    return json.dumps(slim, ensure_ascii=False, indent=2)


def run_recommendation() -> dict | None:
    """
    Core recommendation function.
    Returns the digest JSON dict, or None on failure.
    """
    db.init_db()

    candidates = db.get_candidate_pool(limit=150)
    if len(candidates) < 5:
        log.error("Not enough candidates in pool (%d). Run scrapers first.", len(candidates))
        return None

    # Determine slot 3 region
    scene_followup = db.get_pending_scene_followup()
    if scene_followup:
        world_region = scene_followup
        log.info("Scene follow-up requested for: %s", world_region)
    else:
        world_region = db.get_next_world_region()
        log.info("World rotation region: %s", world_region)

    older_decade_requested = db.get_older_decade_requested()

    user_message = f"""
Here is the candidate album pool:

{build_candidate_summary(candidates)}

Slot 3 world music region this week: {world_region}
older_decade_requested for Slot 2: {older_decade_requested}

Please select the 5 albums for this week's digest.
"""

    log.info("Calling Claude recommendation engine...")
    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            system=RECOMMENDATION_SYSTEM,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)
    except (json.JSONDecodeError, anthropic.APIError, IndexError) as e:
        log.error("Recommendation failed: %s", e)
        return None

    picks = result.get("picks", [])
    if len(picks) < 5:
        log.error("Claude returned fewer than 5 picks: %d", len(picks))
        return None

    # Enrich each pick with full album data from DB
    enriched_picks = []
    slot_map = {}
    album_ids = []
    for pick in picks:
        album_id = pick.get("album_id")
        slot = pick.get("slot")

        # World music pick from Claude's own knowledge (no album_id)
        if not album_id and slot == "world_music" and pick.get("new_album"):
            new_album_data = pick["new_album"]
            new_album_data["source_name"] = "Claude's knowledge"
            new_album_data["source_url"] = None
            new_id = db.insert_album(new_album_data)
            album = db.get_album_by_id(new_id)
            pick["album"] = album
            slot_map[str(new_id)] = slot
            album_ids.append(new_id)
            enriched_picks.append(pick)
            log.info("World music pick from knowledge: %s — %s (inserted as id %d)",
                     new_album_data.get("artist"), new_album_data.get("album_title"), new_id)
            continue

        if not album_id:
            log.warning("Pick with no album_id and no new_album — skipping")
            continue

        album = db.get_album_by_id(album_id)
        if not album:
            log.warning("album_id %s not found in DB — skipping", album_id)
            continue
        pick["album"] = album
        slot_map[str(album_id)] = slot
        album_ids.append(album_id)
        enriched_picks.append(pick)

    if len(enriched_picks) < 5:
        log.error("After enrichment, only %d valid picks", len(enriched_picks))
        return None

    # Check for re-queued albums to append
    import requeue
    requeued = requeue.get_requeued_albums()
    if requeued:
        requeued_pick = {
            "album_id": requeued[0]["id"],
            "slot": "requeued",
            "recommendation_rationale": "You flagged this album last month — returning to it now.",
            "listener_flags": [],
            "curatorial_framing": requeued[0].get("curatorial_context", ""),
            "album": requeued[0],
            "is_requeue": True,
        }
        enriched_picks.append(requeued_pick)
        album_ids.append(requeued[0]["id"])
        requeue.mark_requeued_as_sent(requeued)

    digest = {
        "picks": enriched_picks,
        "world_region_used": result.get("world_region_used", world_region),
    }

    # Persist state
    db.mark_recommended(album_ids, slot_map)
    db.update_world_region_date(world_region)
    if scene_followup:
        db.clear_scene_followup(scene_followup)
    if older_decade_requested:
        db.mark_older_decade_acted()
    db.record_digest_history(album_ids, world_region)
    db.save_pending_digest(json.dumps(digest, ensure_ascii=False, cls=_DateEncoder))

    log.info("Recommendation complete. %d picks saved.", len(enriched_picks))
    return digest
