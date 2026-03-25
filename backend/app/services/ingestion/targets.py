"""Resolve ingestion targets from user preferences, with env fallback."""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import IngestionSettings
from app.models.user_research_interest import UserResearchInterest


@dataclass
class IngestionTargets:
    tickers: list[str]
    news_topics: list[str]
    user_interest_count: int
    source: str


def _normalize(items: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = item.strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def resolve_ingestion_targets(
    session: Session,
    settings: IngestionSettings,
) -> IngestionTargets:
    # Default from env settings (good for local/dev).
    env_tickers = [t.upper() for t in settings.tickers]
    env_topics = list(env_tickers)

    if not settings.enable_user_scoped_targets:
        return IngestionTargets(
            tickers=_normalize(env_tickers),
            news_topics=_normalize(env_topics),
            user_interest_count=0,
            source="env_only",
        )

    interests = (
        session.query(UserResearchInterest)
        .filter(UserResearchInterest.is_active.is_(True))
        .all()
    )
    if not interests:
        return IngestionTargets(
            tickers=_normalize(env_tickers),
            news_topics=_normalize(env_topics),
            user_interest_count=0,
            source="env_fallback_no_user_interests",
        )

    user_tickers = [i.ticker.upper() for i in interests if i.ticker]
    user_topics = [
        *[i.ticker.upper() for i in interests if i.ticker],
        *[i.industry for i in interests if i.industry],
        *[i.sector for i in interests if i.sector],
        *[i.keyword for i in interests if i.keyword],
    ]

    merged_tickers = _normalize([*env_tickers, *user_tickers])
    merged_topics = _normalize([*env_topics, *user_topics])

    return IngestionTargets(
        tickers=merged_tickers,
        news_topics=merged_topics,
        user_interest_count=len(interests),
        source="merged_env_and_user_interests",
    )
