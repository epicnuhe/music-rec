"""
Digest builder.
Takes the recommendation output and produces an HTML email + plain text fallback.
"""

import hashlib
import hmac
import os
from datetime import date

APP_URL = os.environ.get("APP_URL", "http://localhost:8080")
APP_SECRET = os.environ.get("APP_SECRET", "dev-secret")

SLOT_LABELS = {
    "historical_deep_cut": "Historical Deep Cut",
    "contemporary_stretch": "This Week's Stretch",
    "world_music": "World Music",
    "lighter_pick_1": "Easy Listen",
    "lighter_pick_2": "Easy Listen",
    "requeued": "Returning Pick",
}

FLAG_LABELS = {
    "demanding_listen": "demanding listen — may take a few tries",
    "lyrically_driven": "lyrically driven — worth focused listening",
    "significant_critical_reputation": "significant critical reputation — worth the patience",
    "immediate_listen": "immediate listen — no patience required",
    "world_music_context": "",  # rendered separately
}


def _make_token(album_id: int, action: str) -> str:
    msg = f"{album_id}:{action}".encode()
    return hmac.new(APP_SECRET.encode(), msg, hashlib.sha256).hexdigest()


def _feedback_url(album_id: int, action: str) -> str:
    token = _make_token(album_id, action)
    return f"{APP_URL}/feedback?album_id={album_id}&action={action}&token={token}"


def _flag_html(flags: list[str]) -> str:
    if not flags:
        return ""
    rendered = []
    for f in flags:
        if f == "world_music_context":
            continue
        label = FLAG_LABELS.get(f, f)
        if label:
            rendered.append(f'<span style="color:#888;font-size:13px;font-style:italic;">{label}</span>')
    return "<br>".join(rendered)


def _album_html(pick: dict, is_last: bool = False) -> str:
    album = pick["album"]
    slot = pick.get("slot", "")
    slot_label = SLOT_LABELS.get(slot, slot.replace("_", " ").title())
    flags = pick.get("listener_flags", [])
    framing = pick.get("curatorial_framing") or album.get("curatorial_context") or ""
    world_ctx = pick.get("world_music_context", "")
    album_id = album["id"]
    is_requeue = pick.get("is_requeue", False)

    year = album.get("year") or ""
    country = album.get("country") or ""
    meta = ", ".join(filter(None, [str(year), country]))
    source = album.get("source_name") or ""
    author = album.get("source_author") or ""
    via = f"Via {source}" + (f" — {author}" if author else "")

    requeue_note = ""
    if is_requeue:
        requeue_note = '<p style="color:#888;font-size:13px;font-style:italic;">↩ Returning to this — you flagged it last month</p>'

    flags_html = _flag_html(flags)
    world_html = ""
    if slot == "world_music" and world_ctx:
        world_html = f'<p style="color:#666;font-size:13px;margin:6px 0 0;">{world_ctx}</p>'

    # Build action buttons
    buttons = []
    loved_url = _feedback_url(album_id, "loved")
    didnt_url = _feedback_url(album_id, "requeue")
    buttons.append(f'<a href="{loved_url}" style="{BTN_STYLE}background:#1a1a1a;color:#fff;">Loved it</a>')
    buttons.append(f'<a href="{didnt_url}" style="{BTN_STYLE}background:#f0f0f0;color:#333;">Didn\'t land</a>')

    if slot == "world_music":
        scene_url = _feedback_url(album_id, "scene_followup")
        buttons.append(f'<a href="{scene_url}" style="{BTN_STYLE}background:#f0f0f0;color:#333;">More from this scene</a>')

    buttons_html = " &nbsp; ".join(buttons)

    border_bottom = 'border-bottom:1px solid #e5e5e5;' if not is_last else ''

    return f"""
<tr><td style="padding:28px 0;{border_bottom}">
  <p style="margin:0 0 4px;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#999;">{slot_label}</p>
  <p style="margin:0 0 2px;font-size:20px;font-weight:700;color:#111;">{album['artist']} — <em>{album['album_title']}</em></p>
  {"<p style='margin:0 0 2px;font-size:13px;color:#888;'>" + meta + "</p>" if meta else ""}
  <p style="margin:0 0 12px;font-size:12px;color:#aaa;">{via}</p>
  {requeue_note}
  <p style="margin:0 0 10px;font-size:15px;line-height:1.6;color:#333;">{framing}</p>
  {world_html}
  {("<p style='margin:8px 0;'>" + flags_html + "</p>") if flags_html else ""}
  <p style="margin:14px 0 0;">{buttons_html}</p>
</td></tr>
"""


BTN_STYLE = (
    "display:inline-block;padding:8px 16px;border-radius:4px;"
    "font-size:13px;text-decoration:none;font-family:sans-serif;"
    "font-weight:500;margin-right:6px;"
)


def build_html_email(digest: dict) -> str:
    picks = digest["picks"]
    week_of = date.today().strftime("%-d %B %Y")

    album_rows = ""
    for i, pick in enumerate(picks):
        album_rows += _album_html(pick, is_last=(i == len(picks) - 1))

    # Global Slot 2 control — find the contemporary_stretch pick
    slot2_pick = next((p for p in picks if p.get("slot") == "contemporary_stretch"), None)
    older_btn = ""
    if slot2_pick:
        older_url = _feedback_url(slot2_pick["album"]["id"], "older_decade")
        older_btn = f"""
<tr><td style="padding:20px 0 0;text-align:center;border-top:1px solid #e5e5e5;">
  <a href="{older_url}" style="{BTN_STYLE}background:#f0f0f0;color:#333;font-size:12px;">
    Give me something older next week (Slot 2)
  </a>
</td></tr>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your music for the week of {week_of}</title>
</head>
<body style="margin:0;padding:0;background:#fafafa;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fafafa;">
<tr><td align="center" style="padding:40px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:6px;padding:40px;">
  <tr><td>
    <p style="margin:0 0 4px;font-size:12px;letter-spacing:0.1em;text-transform:uppercase;color:#aaa;">Weekly Digest</p>
    <h1 style="margin:0 0 32px;font-size:26px;font-weight:700;color:#111;">
      Music for the week of {week_of}
    </h1>
  </td></tr>
  {album_rows}
  {older_btn}
  <tr><td style="padding:32px 0 0;">
    <p style="margin:0;font-size:12px;color:#ccc;text-align:center;">
      This digest was assembled by a recommendation system you built.
    </p>
  </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def build_plain_text(digest: dict) -> str:
    picks = digest["picks"]
    week_of = date.today().strftime("%-d %B %Y")
    lines = [f"Music for the week of {week_of}", "=" * 50, ""]

    for pick in picks:
        album = pick["album"]
        slot_label = SLOT_LABELS.get(pick.get("slot", ""), pick.get("slot", ""))
        year = album.get("year") or ""
        country = album.get("country") or ""
        meta = ", ".join(filter(None, [str(year), country]))
        author = album.get("source_author") or ""
        source = album.get("source_name") or ""
        via = f"Via {source}" + (f" — {author}" if author else "")
        framing = pick.get("curatorial_framing") or album.get("curatorial_context") or ""
        flags = pick.get("listener_flags", [])

        lines += [
            f"[ {slot_label} ]",
            f"{album['artist']} — {album['album_title']}" + (f" ({meta})" if meta else ""),
            via,
            "",
            framing,
        ]
        if pick.get("is_requeue"):
            lines.append("↩ Returning to this — you flagged it last month")
        if flags:
            flag_strs = [FLAG_LABELS.get(f, f) for f in flags if f != "world_music_context" and FLAG_LABELS.get(f, f)]
            lines += flag_strs
        lines += ["", "-" * 40, ""]

    return "\n".join(lines)
