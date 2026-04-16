"""
Entry point for cron jobs.
Railway cron services call this with a job name argument.

Usage:
    python main.py scrape-main      # Bandcamp + Stereogum (Mon/Wed/Fri)
    python main.py scrape-nts       # NTS Radio (Tue/Thu)
    python main.py recommend        # Build digest (Sunday evening)
    python main.py deliver          # Send email (Monday 9am)
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("main")


def _ensure_db():
    import database as db
    db.init_db()


def job_scrape_main():
    """Scrape Bandcamp Daily and Stereogum, extract albums."""
    _ensure_db()
    from scraper import bandcamp, stereogum
    import extractor

    log.info("=== Scraping Bandcamp Daily ===")
    bc_items = bandcamp.scrape()
    bc_new = extractor.run_extraction(bc_items)
    log.info("Bandcamp: %d new albums extracted", bc_new)

    log.info("=== Scraping Stereogum ===")
    sg_items = stereogum.scrape()
    sg_new = extractor.run_extraction(sg_items)
    log.info("Stereogum: %d new albums extracted", sg_new)

    log.info("scrape-main complete. Total new: %d", bc_new + sg_new)


def job_scrape_nts():
    """Scrape NTS Radio and extract albums."""
    _ensure_db()
    from scraper import nts
    import extractor

    log.info("=== Scraping NTS Radio ===")
    nts_items = nts.scrape()
    nts_new = extractor.run_extraction(nts_items)
    log.info("NTS: %d new albums extracted", nts_new)


def job_recommend():
    """Run the recommendation engine and save the pending digest."""
    _ensure_db()
    import recommender

    log.info("=== Running Recommendation Engine ===")
    digest = recommender.run_recommendation()
    if digest:
        log.info("Digest built successfully with %d picks", len(digest["picks"]))
    else:
        log.error("Recommendation engine returned nothing")
        sys.exit(1)


def job_deliver():
    """Send the pending digest email."""
    _ensure_db()
    import delivery

    log.info("=== Sending Weekly Digest Email ===")
    success = delivery.send_weekly_digest()
    if not success:
        log.error("Email delivery failed")
        sys.exit(1)
    log.info("Email delivered successfully")


JOBS = {
    "scrape-main": job_scrape_main,
    "scrape-nts": job_scrape_nts,
    "recommend": job_recommend,
    "deliver": job_deliver,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in JOBS:
        print(f"Usage: python main.py <job>")
        print(f"Available jobs: {', '.join(JOBS)}")
        sys.exit(1)

    job_name = sys.argv[1]
    log.info("Starting job: %s", job_name)
    JOBS[job_name]()
    log.info("Job %s finished", job_name)
