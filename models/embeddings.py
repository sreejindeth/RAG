"""Embedding model helpers that can be reused throughout the app."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List

import numpy as np
from sentence_transformers import SentenceTransformer

from config.config import settings


class EmbeddingModel:
    """Thin wrapper around a SentenceTransformer embedding model."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: Iterable[str]) -> List[np.ndarray]:
        processed = [text.strip() for text in texts if text and text.strip()]
        if not processed:
            return []

        embeddings = self._model.encode(
            processed,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        if isinstance(embeddings, np.ndarray):
            return [embeddings[i] for i in range(len(processed))]
        return [np.asarray(vec) for vec in embeddings]


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    """Returns a cached embedding model instance."""

    return EmbeddingModel()

