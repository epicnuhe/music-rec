"""
Flask web server — handles feedback button clicks from email links.
Runs as the Railway web service (always on).
"""

import hashlib
import hmac
import logging
import os
from datetime import date, timedelta

from flask import Flask, request, abort

import database as db

app = Flask(__name__)
log = logging.getLogger(__name__)

APP_SECRET = os.environ.get("APP_SECRET", "dev-secret")

VALID_ACTIONS = {"loved", "requeue", "scene_followup", "older_decade"}

CONFIRMATION_MESSAGES = {
    "loved": lambda title: f"Got it — marked <strong>{title}</strong> as a favourite. It'll shape future picks.",
    "requeue": lambda title: f"Got it — <strong>{title}</strong> flagged for re-queue. You'll hear it again in about a month.",
    "scene_followup": lambda title: f"Got it — next week's world music slot will dig deeper into the same region.",
    "older_decade": lambda title: f"Got it — next week's stretch pick (Slot 2) will be something pre-2000.",
}


def _verify_token(album_id: int, action: str, token: str) -> bool:
    msg = f"{album_id}:{action}".encode()
    expected = hmac.new(APP_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)


def _confirmation_page(message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Got it</title>
<style>
  body {{font-family:Georgia,serif;background:#fafafa;display:flex;align-items:center;
        justify-content:center;min-height:100vh;margin:0;}}
  .card {{background:#fff;border-radius:8px;padding:48px;max-width:480px;text-align:center;
          box-shadow:0 2px 12px rgba(0,0,0,.06);}}
  p {{color:#333;font-size:18px;line-height:1.6;}}
  .close {{margin-top:24px;font-size:14px;color:#aaa;}}
</style>
</head>
<body>
<div class="card">
  <p>{message}</p>
  <p class="close">You can close this tab.</p>
</div>
</body>
</html>"""


@app.route("/feedback")
def feedback():
    db.init_db()

    try:
        album_id = int(request.args.get("album_id", ""))
        action = request.args.get("action", "")
        token = request.args.get("token", "")
    except (ValueError, TypeError):
        abort(400)

    if action not in VALID_ACTIONS:
        abort(400)

    if not _verify_token(album_id, action, token):
        abort(403)

    album = db.get_album_by_id(album_id)
    if not album:
        abort(404)

    title = f"{album['artist']} — {album['album_title']}"

    if action == "loved":
        db.record_feedback(album_id, "loved")

    elif action == "requeue":
        requeue_date = (date.today() + timedelta(days=30)).isoformat()
        db.record_feedback(album_id, "requeue", requeue_date=requeue_date)

    elif action == "scene_followup":
        # Find which region this album was in (from world_rotation logic via digest_history)
        # We store it as the slot_assigned region name in the album record
        region = album.get("slot_assigned", "")
        if region and region != "world_music":
            # slot_assigned stores the slot name; we need the region from digest_history
            region = None
        # Fall back: look up last world_rotation region from digest_history
        if not region:
            with db.get_conn() as conn:
                row = conn.execute(
                    "SELECT world_region FROM digest_history ORDER BY date_sent DESC LIMIT 1"
                ).fetchone()
                region = row["world_region"] if row else None

        if region:
            db.request_scene_followup(region)
        db.record_feedback(album_id, "scene_followup")

    elif action == "older_decade":
        db.record_feedback(album_id, "older_decade")

    msg = CONFIRMATION_MESSAGES[action](title)
    return _confirmation_page(msg)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logging.basicConfig(level=logging.INFO)
    db.init_db()
    app.run(host="0.0.0.0", port=port)
