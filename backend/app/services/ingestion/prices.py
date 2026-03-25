"""yfinance OHLCV ingestion into price_snapshots."""
import logging
from datetime import date, datetime

import yfinance as yf
from sqlalchemy.orm import Session

from app.config import IngestionSettings
from app.models.price_snapshot import PriceSnapshot
from app.services.ingestion.retry import with_retry

logger = logging.getLogger(__name__)


def _row_date(idx) -> date:
    if hasattr(idx, "date"):
        d = idx.date()
        if isinstance(d, datetime):
            return d.date()
        return d
    if isinstance(idx, datetime):
        return idx.date()
    return idx


def ingest_prices_for_ticker(session: Session, ticker: str, settings: IngestionSettings) -> int:
    """
    Fetch daily history for ``ticker`` and replace overlapping rows in DB.
    Returns number of rows inserted.
    """
    t = yf.Ticker(ticker)

    def _fetch():
        return t.history(period=settings.yfinance_period, interval="1d", auto_adjust=True)

    hist = with_retry(
        _fetch,
        max_attempts=settings.max_retries,
        backoff_seconds=settings.retry_backoff_seconds,
        label=f"yfinance({ticker})",
    )
    if hist is None or hist.empty:
        logger.warning("yfinance returned no rows for %s", ticker)
        return 0

    dates = [_row_date(i) for i in hist.index]
    d_min, d_max = min(dates), max(dates)
    session.query(PriceSnapshot).filter(
        PriceSnapshot.ticker == ticker,
        PriceSnapshot.date >= d_min,
        PriceSnapshot.date <= d_max,
    ).delete(synchronize_session=False)

    count = 0
    for idx, row in hist.iterrows():
        d = _row_date(idx)
        vol = row.get("Volume")
        if vol is None or vol != vol:  # NaN check
            vol_int = None
        else:
            vol_int = int(float(vol))
        snap = PriceSnapshot(
            ticker=ticker,
            date=d,
            open=float(row["Open"]) if row.get("Open") == row.get("Open") else None,
            high=float(row["High"]) if row.get("High") == row.get("High") else None,
            low=float(row["Low"]) if row.get("Low") == row.get("Low") else None,
            close=float(row["Close"]),
            volume=vol_int,
        )
        session.add(snap)
        count += 1
    logger.info("Ingested %s price rows for %s (%s to %s)", count, ticker, d_min, d_max)
    return count


def run_price_ingestion(
    session: Session,
    settings: IngestionSettings,
    tickers: list[str] | None = None,
) -> dict:
    if not settings.enable_yfinance:
        logger.info("Skipping yfinance (INGEST_ENABLE_YFINANCE=false)")
        return {"skipped": True, "tickers": tickers or settings.tickers, "rows": 0}
    target_tickers = tickers or settings.tickers
    total = 0
    for ticker in target_tickers:
        total += ingest_prices_for_ticker(session, ticker.upper(), settings)
    return {"skipped": False, "tickers": target_tickers, "rows": total}
