"""
Application and ingestion settings from environment variables.

API keys (where required):
- NEWSAPI_API_KEY — https://newsapi.org (NewsAPI.org developer key)
- FINNHUB_API_KEY — https://finnhub.io (Finnhub API key)
- PINECONE_API_KEY — optional; Pinecone console
- PINECONE_INDEX_HOST — optional; serverless index host URL from Pinecone

No key required: yfinance (Yahoo Finance, unofficial), public RSS URLs.
"""
import os
from dataclasses import dataclass, field
from typing import List


def _bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _csv(name: str, default: List[str]) -> List[str]:
    raw = os.getenv(name)
    if not raw:
        return list(default)
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass
class IngestionSettings:
    """Feature flags and parameters for the Phase 1.3 ingestion pipeline."""

    enable_yfinance: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_YFINANCE", True)
    )
    enable_newsapi: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_NEWSAPI", True)
    )
    enable_rss: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_RSS", True)
    )
    enable_finnhub: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_FINNHUB", True)
    )
    enable_pinecone: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_PINECONE", False)
    )
    enable_user_scoped_targets: bool = field(
        default_factory=lambda: _bool("INGEST_ENABLE_USER_SCOPED_TARGETS", True)
    )

    newsapi_api_key: str | None = field(
        default_factory=lambda: os.getenv("NEWSAPI_API_KEY")
    )
    finnhub_api_key: str | None = field(
        default_factory=lambda: os.getenv("FINNHUB_API_KEY")
    )
    pinecone_api_key: str | None = field(
        default_factory=lambda: os.getenv("PINECONE_API_KEY")
    )
    pinecone_index_host: str | None = field(
        default_factory=lambda: (
            os.getenv("PINECONE_INDEX_HOST") or os.getenv("PINECONE_HOST")
        )
    )
    pinecone_index_name: str | None = field(
        default_factory=lambda: os.getenv(
            "PINECONE_INDEX_NAME", "agentadvisors-news"
        )
    )

    tickers: List[str] = field(
        default_factory=lambda: _csv("INGEST_TICKERS", ["AAPL", "MSFT", "GOOGL"])
    )
    yfinance_period: str = field(
        default_factory=lambda: os.getenv("INGEST_YF_PERIOD", "1mo")
    )
    newsapi_page_size: int = field(
        default_factory=lambda: int(os.getenv("INGEST_NEWSAPI_PAGE_SIZE", "20"))
    )
    rss_feed_urls: List[str] = field(
        default_factory=lambda: _csv(
            "INGEST_RSS_FEEDS",
            [
                "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            ],
        )
    )
    http_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("INGEST_HTTP_TIMEOUT", "30"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("INGEST_MAX_RETRIES", "3"))
    )
    retry_backoff_seconds: float = field(
        default_factory=lambda: float(os.getenv("INGEST_RETRY_BACKOFF", "1.5"))
    )


def get_ingestion_settings() -> IngestionSettings:
    return IngestionSettings()
