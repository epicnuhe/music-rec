"""
Re-queue checker.
Finds albums the user flagged for re-listening that are now due.
"""

import logging

import database as db

log = logging.getLogger(__name__)


def get_requeued_albums() -> list[dict]:
    """
    Return any albums that were flagged 'didn't land' and are now due
    for re-surfacing (~30 days later).
    """
    due = db.get_due_requeued_albums()
    if due:
        log.info("Re-queue: %d album(s) due this week", len(due))
    return due


def mark_requeued_as_sent(requeued_albums: list[dict]):
    """Mark all due re-queued albums as acted on after the digest is built."""
    for album in requeued_albums:
        db.mark_requeue_acted(album["feedback_id"])
