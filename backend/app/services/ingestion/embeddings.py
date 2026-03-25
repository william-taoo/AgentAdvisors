"""After inserting articles, embed and upsert to Pinecone; update embedding_id."""
import logging

from sqlalchemy.orm import Session

from app.config import IngestionSettings
from app.models.article import Article
from app.services.ingestion.news_store import NoOpNewsVectorStore, build_news_vector_store

logger = logging.getLogger(__name__)


def embed_recent_articles(session: Session, settings: IngestionSettings, limit: int = 200) -> int:
    """Embed articles with null embedding_id (most recent first). Returns count updated."""
    store = build_news_vector_store(
        settings.enable_pinecone,
        settings.pinecone_api_key,
        settings.pinecone_index_host,
        settings.pinecone_index_name or "agentadvisors-news",
    )
    if isinstance(store, NoOpNewsVectorStore):
        logger.info("Pinecone skipped (INGEST_ENABLE_PINECONE=false or missing keys)")
        return 0

    q = (
        session.query(Article)
        .filter(Article.embedding_id.is_(None))
        .order_by(Article.id.desc())
        .limit(limit)
    )
    rows = q.all()
    updated = 0
    for art in rows:
        text = (art.content or "") or (art.title or "")
        eid = store.upsert_article(
            art.id,
            text,
            {"title": art.title, "url": art.url, "tickers": art.tickers},
        )
        if eid:
            art.embedding_id = eid
            updated += 1
    logger.info("Pinecone: updated embedding_id on %s articles", updated)
    return updated
