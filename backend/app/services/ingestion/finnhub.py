"""Finnhub analyst JSON ingestion into analyst_snapshots."""
import logging
from datetime import datetime, timedelta, timezone

import finnhub
from sqlalchemy.orm import Session

from app.config import IngestionSettings
from app.models.analyst_snapshot import AnalystSnapshot
from app.services.ingestion.retry import with_retry

logger = logging.getLogger(__name__)


def _jsonable(obj):
    """Convert Finnhub responses to JSON-serializable structures."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(x) for x in obj]
    return str(obj)


def ingest_finnhub_for_ticker(session: Session, ticker: str, settings: IngestionSettings) -> int:
    if not settings.finnhub_api_key:
        logger.warning("FINNHUB_API_KEY not set; skipping Finnhub")
        return 0

    client = finnhub.Client(api_key=settings.finnhub_api_key)
    sym = ticker.upper()
    rows = 0
    now = datetime.now(timezone.utc)

    to_d = datetime.now(timezone.utc).date()
    from_d = to_d - timedelta(days=365)
    from_s, to_s = str(from_d), str(to_d)

    endpoints = [
        ("recommendation_trends", lambda: client.recommendation_trends(sym)),
        (
            "earnings_calendar",
            lambda: client.earnings_calendar(_from=from_s, to=to_s, symbol=sym),
        ),
    ]

    for category, fn in endpoints:
        try:
            raw = with_retry(
                fn,
                max_attempts=settings.max_retries,
                backoff_seconds=settings.retry_backoff_seconds,
                label=f"finnhub.{category}({sym})",
            )
        except Exception as e:
            logger.error("Finnhub %s %s: %s", category, sym, e)
            continue

        payload = _jsonable(raw)
        if payload is None or (isinstance(payload, list) and len(payload) == 0):
            logger.debug("Finnhub %s %s: empty", category, sym)
            continue

        session.add(
            AnalystSnapshot(
                ticker=sym,
                category=category,
                payload=payload,
                fetched_at=now,
            )
        )
        rows += 1

    logger.info("Finnhub: stored %s snapshot rows for %s", rows, sym)
    return rows


def run_finnhub_ingestion(
    session: Session,
    settings: IngestionSettings,
    tickers: list[str] | None = None,
) -> dict:
    if not settings.enable_finnhub:
        logger.info("Skipping Finnhub (INGEST_ENABLE_FINNHUB=false)")
        return {"skipped": True, "rows": 0}
    if not settings.finnhub_api_key:
        logger.warning("FINNHUB_API_KEY missing; skipping Finnhub")
        return {"skipped": True, "rows": 0}
    target_tickers = tickers or settings.tickers
    total = 0
    for ticker in target_tickers:
        total += ingest_finnhub_for_ticker(session, ticker, settings)
    return {"skipped": False, "tickers": target_tickers, "rows": total}
