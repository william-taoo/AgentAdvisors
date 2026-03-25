"""
Run full Phase 1.3 ingestion: prices, news (NewsAPI + RSS), Finnhub, Pinecone embeddings.
"""
import logging
import sys

import dotenv

dotenv.load_dotenv()

from app.config import get_ingestion_settings
from app.database import SessionLocal
from app.services.ingestion.embeddings import embed_recent_articles
from app.services.ingestion.finnhub import run_finnhub_ingestion
from app.services.ingestion.news import run_news_ingestion
from app.services.ingestion.prices import run_price_ingestion
from app.services.ingestion.targets import resolve_ingestion_targets

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("ingestion.pipeline")


def run_ingestion() -> dict:
    settings = get_ingestion_settings()
    session = SessionLocal()
    summary: dict = {}
    try:
        targets = resolve_ingestion_targets(session, settings)
        summary["targets"] = {
            "source": targets.source,
            "user_interest_count": targets.user_interest_count,
            "tickers": targets.tickers,
            "news_topics": targets.news_topics,
        }
        try:
            summary["prices"] = run_price_ingestion(
                session,
                settings,
                tickers=targets.tickers,
            )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Price ingestion failed")
            raise

        try:
            summary["news"] = run_news_ingestion(
                session,
                settings,
                tickers=targets.tickers,
                topics=targets.news_topics,
            )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("News ingestion failed")
            raise

        try:
            summary["finnhub"] = run_finnhub_ingestion(
                session,
                settings,
                tickers=targets.tickers,
            )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Finnhub ingestion failed")
            raise

        try:
            summary["embeddings"] = embed_recent_articles(session, settings)
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Embedding / Pinecone step failed")
            raise

        return summary
    finally:
        session.close()


def main() -> None:
    try:
        out = run_ingestion()
    except Exception:
        sys.exit(1)
    logger.info("Ingestion complete: %s", out)
    print(out)


if __name__ == "__main__":
    main()
