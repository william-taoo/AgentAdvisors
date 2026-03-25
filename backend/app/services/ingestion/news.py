"""NewsAPI and RSS ingestion into articles."""
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional, Set

import feedparser
from newsapi import NewsApiClient
from sqlalchemy.orm import Session

from app.config import IngestionSettings
from app.models.article import Article
from app.services.ingestion.retry import with_retry

logger = logging.getLogger(__name__)


def _parse_published(entry) -> Optional[datetime]:
    if getattr(entry, "published_parsed", None):
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if getattr(entry, "published", None):
        try:
            return parsedate_to_datetime(entry.published)
        except (TypeError, ValueError):
            pass
    return None


def _truncate_title(title: str, max_len: int = 500) -> str:
    title = (title or "").strip() or "(no title)"
    if len(title) <= max_len:
        return title
    return title[: max_len - 1] + "…"


def _existing_urls(session: Session) -> Set[str]:
    rows = session.query(Article.url).filter(Article.url.isnot(None)).all()
    return {r[0] for r in rows if r[0]}


def ingest_newsapi(
    session: Session,
    settings: IngestionSettings,
    existing_urls: Set[str],
    topics: list[str],
) -> int:
    if not settings.enable_newsapi:
        logger.info("Skipping NewsAPI (INGEST_ENABLE_NEWSAPI=false)")
        return 0
    if not settings.newsapi_api_key:
        logger.warning("NEWSAPI_API_KEY not set; skipping NewsAPI")
        return 0

    client = NewsApiClient(api_key=settings.newsapi_api_key)
    added = 0

    for topic in topics:
        q = topic.upper()

        def _fetch():
            return client.get_everything(
                q=q,
                language="en",
                sort_by="publishedAt",
                page_size=min(settings.newsapi_page_size, 100),
            )

        try:
            data = with_retry(
                _fetch,
                max_attempts=settings.max_retries,
                backoff_seconds=settings.retry_backoff_seconds,
                label=f"NewsAPI({q})",
            )
        except Exception as e:
            logger.error("NewsAPI failed for %s: %s", q, e)
            continue

        if data.get("status") != "ok":
            logger.error("NewsAPI error for %s: %s", q, data.get("message", data))
            continue

        for art in data.get("articles") or []:
            url = art.get("url") or ""
            title = _truncate_title(art.get("title") or "")
            if url and url in existing_urls:
                continue
            published = None
            if art.get("publishedAt"):
                try:
                    published = datetime.fromisoformat(
                        art["publishedAt"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass
            row = Article(
                title=title,
                url=url or None,
                source="newsapi",
                published_at=published,
                content=art.get("description") or art.get("content"),
                tickers=q,
            )
            session.add(row)
            if url:
                existing_urls.add(url)
            added += 1

    logger.info("NewsAPI: added %s articles", added)
    return added


def ingest_rss(
    session: Session,
    settings: IngestionSettings,
    existing_urls: Set[str],
    tickers: list[str],
) -> int:
    if not settings.enable_rss:
        logger.info("Skipping RSS (INGEST_ENABLE_RSS=false)")
        return 0
    if not settings.rss_feed_urls:
        logger.info("No INGEST_RSS_FEEDS configured; skipping RSS")
        return 0

    tickers_csv = ",".join(t.upper() for t in tickers)
    added = 0

    for feed_url in settings.rss_feed_urls:

        def _parse():
            return feedparser.parse(feed_url)

        try:
            parsed = with_retry(
                _parse,
                max_attempts=settings.max_retries,
                backoff_seconds=settings.retry_backoff_seconds,
                label=f"RSS({feed_url})",
            )
        except Exception as e:
            logger.error("RSS parse failed %s: %s", feed_url, e)
            continue

        for entry in parsed.entries or []:
            url = getattr(entry, "link", None) or ""
            if url and url in existing_urls:
                continue
            title = _truncate_title(getattr(entry, "title", "") or "")
            pub = _parse_published(entry)
            row = Article(
                title=title,
                url=url or None,
                source=f"rss:{feed_url[:80]}",
                published_at=pub,
                content=getattr(entry, "summary", None),
                tickers=tickers_csv,
            )
            session.add(row)
            if url:
                existing_urls.add(url)
            added += 1

    logger.info("RSS: added %s articles", added)
    return added


def run_news_ingestion(
    session: Session,
    settings: IngestionSettings,
    tickers: list[str] | None = None,
    topics: list[str] | None = None,
) -> dict:
    target_tickers = tickers or settings.tickers
    target_topics = topics or [t.upper() for t in target_tickers]
    existing = _existing_urls(session)
    n1 = ingest_newsapi(session, settings, existing, target_topics)
    n2 = ingest_rss(session, settings, existing, target_tickers)
    return {
        "topics": target_topics,
        "newsapi": n1,
        "rss": n2,
        "total": n1 + n2,
    }
