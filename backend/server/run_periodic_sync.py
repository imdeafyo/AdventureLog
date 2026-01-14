#!/usr/bin/env python3
"""
Periodic sync runner for AdventureLog.
Runs sync_visited_regions management command every 60 seconds.
Managed by supervisord to ensure it inherits container environment variables.
"""
import os
import sys
import time
import logging
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django
django.setup()

from django.core.management import call_command

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 60

# Event used to signal shutdown from signal handlers
_stop_event = threading.Event()


def _seconds_until_next_midnight() -> float:
    """Return number of seconds until the next local midnight."""
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return (next_midnight - now).total_seconds()


def _handle_termination(signum, frame):
    """Signal handler for SIGTERM and SIGINT: request graceful shutdown."""
    logger.info(f"Received signal {signum}; shutting down gracefully...")
    _stop_event.set()


def run_sync():
    """Run the sync_visited_regions command."""
    try:
        logger.info("Running sync_visited_regions...")
        call_command('sync_visited_regions')
        logger.info("Sync completed successfully")
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)


def main():
    """Main loop - run sync every INTERVAL_SECONDS."""
    logger.info(f"Starting periodic sync worker for midnight background jobs...")

    # Install signal handlers so supervisord (or other process managers)
    # can request a clean shutdown using SIGTERM/SIGINT.
    signal.signal(signal.SIGTERM, _handle_termination)
    signal.signal(signal.SIGINT, _handle_termination)

    try:
        while not _stop_event.is_set():
            # Wait until the next local midnight (or until shutdown)
            wait_seconds = _seconds_until_next_midnight()
            hours = wait_seconds / 3600.0
            logger.info(
                f"Next sync scheduled in {wait_seconds:.0f}s (~{hours:.2f}h) at UTC midnight"
            )
            # Sleep until midnight or until stop event is set
            if _stop_event.wait(wait_seconds):
                break

            # It's midnight (or we woke up), run the sync once
            run_sync()

            # After running at midnight, loop continues to compute next midnight
    except Exception:
        logger.exception("Unexpected error in periodic sync loop")
    finally:
        logger.info("Periodic sync worker exiting")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Fallback in case the signal is delivered as KeyboardInterrupt
        logger.info("KeyboardInterrupt received — exiting")
        _stop_event.set()
    except SystemExit:
        logger.info("SystemExit received — exiting")
    finally:
        logger.info("run_periodic_sync terminated")
