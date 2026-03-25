"""
Pinecone vector upsert for article text (SentenceTransformers embeddings).

Create a Pinecone index with dimension 384 if using the default model ``all-MiniLM-L6-v2``.
"""
from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMBED_DIM = 384


@runtime_checkable
class NewsVectorStore(Protocol):
    """Abstract news embedding store (Pinecone or no-op)."""

    def upsert_article(self, article_id: int, text: str, metadata: dict) -> str | None:
        """Return embedding / vector id, or None if skipped."""


class NoOpNewsVectorStore:
    def upsert_article(self, article_id: int, text: str, metadata: dict) -> str | None:
        return None


class PineconeNewsVectorStore:
    def __init__(self, api_key: str, index_host: str, index_name: str) -> None:
        from pinecone import Pinecone

        self._pc = Pinecone(api_key=api_key)
        self._index = self._pc.Index(host=index_host)
        self._index_name = index_name
        self._model = None

    def _encode(self, text: str):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(_EMBED_MODEL_NAME)
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def upsert_article(self, article_id: int, text: str, metadata: dict) -> str | None:
        if not text or not text.strip():
            return None
        vec_id = f"article-{article_id}"
        values = self._encode(text[:8000])
        if len(values) != _EMBED_DIM:
            logger.warning("Unexpected embedding dim %s (expected %s)", len(values), _EMBED_DIM)
        meta = {k: str(v)[:200] for k, v in metadata.items() if v is not None}
        self._index.upsert(vectors=[{"id": vec_id, "values": values, "metadata": meta}])
        return vec_id


def build_news_vector_store(
    enable: bool,
    api_key: str | None,
    index_host: str | None,
    index_name: str,
) -> NewsVectorStore:
    if not enable or not api_key or not index_host:
        return NoOpNewsVectorStore()
    return PineconeNewsVectorStore(api_key=api_key, index_host=index_host, index_name=index_name)
