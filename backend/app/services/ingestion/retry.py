"""Simple retry with exponential backoff for external API calls."""
import logging
import time
from typing import Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int,
    backoff_seconds: float,
    label: str = "call",
) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt == max_attempts:
                logger.warning("%s failed after %s attempts: %s", label, max_attempts, e)
                raise
            wait = backoff_seconds ** (attempt - 1)
            logger.debug("%s attempt %s/%s: %s; retrying in %.1fs", label, attempt, max_attempts, e, wait)
            time.sleep(wait)
    assert last_exc is not None
    raise last_exc
