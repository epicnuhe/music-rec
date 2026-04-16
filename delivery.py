"""
Email delivery via Resend API.
"""

import json
import logging
import os
from datetime import date

import resend

import database as db
import digest as digest_builder

log = logging.getLogger(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY", "")
DELIVERY_EMAIL = os.environ.get("DELIVERY_EMAIL", "")
FROM_ADDRESS = "music-rec@resend.dev"


def send_weekly_digest() -> bool:
    """
    Pull the pending digest from the database and send it.
    Returns True on success.
    """
    db.init_db()

    pending_json = db.get_pending_digest()
    if not pending_json:
        log.error("No pending digest found. Did the recommendation engine run?")
        return False

    digest_data = json.loads(pending_json)
    week_of = date.today().strftime("%-d %B %Y")

    html = digest_builder.build_html_email(digest_data)
    text = digest_builder.build_plain_text(digest_data)

    try:
        params = {
            "from": f"Music Rec <{FROM_ADDRESS}>",
            "to": [DELIVERY_EMAIL],
            "subject": f"Your music for the week of {week_of}",
            "html": html,
            "text": text,
        }
        response = resend.Emails.send(params)
        log.info("Email sent. Resend id: %s", response.get("id"))
        db.mark_digest_sent()
        return True
    except Exception as e:
        log.error("Failed to send email: %s", e)
        return False
