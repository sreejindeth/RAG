"""Retrieval utilities for chunking, storing, and querying documents."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np

from config.config import settings, CHUNK_SIZE, CHUNK_OVERLAP
from models.embeddings import EmbeddingModel


@dataclass
class StoredChunk:
    document_name: str
    content: str
    embedding: np.ndarray
    chunk_id: str


def _chunk_text(text: str) -> List[str]:
    tokens = text.replace("\r", " ").split()
    if not tokens:
        return []

    chunks: List[str] = []
    step = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)
    for start in range(0, len(tokens), step):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk = " ".join(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


class InMemoryVectorStore:
    """Very small, dependency-free vector store for demo purposes."""

    def __init__(self) -> None:
        self._chunks: List[StoredChunk] = []

    def clear(self) -> None:
        self._chunks.clear()

    def add_document(self, document_name: str, text: str, embedder: EmbeddingModel) -> int:
        chunks = _chunk_text(text)
        if not chunks:
            return 0

        embeddings = embedder.embed(chunks)
        added = 0
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = hashlib.md5(f"{document_name}:{chunk[:20]}".encode()).hexdigest()
            self._chunks.append(
                StoredChunk(
                    document_name=document_name,
                    content=chunk,
                    embedding=np.asarray(embedding, dtype=np.float32),
                    chunk_id=chunk_id,
                )
            )
            added += 1
        return added

    def similarity_search(
        self,
        query: str,
        embedder: EmbeddingModel,
        top_k: int | None = None,
    ) -> List[Tuple[StoredChunk, float]]:
        if not query.strip() or not self._chunks:
            return []

        query_vecs = embedder.embed([query])
        if not query_vecs:
            return []

        query_vec = query_vecs[0]
        scores: List[Tuple[StoredChunk, float]] = []
        for chunk in self._chunks:
            if chunk.embedding is None or not len(chunk.embedding):
                continue
            score = float(np.dot(query_vec, chunk.embedding))
            scores.append((chunk, score))

        scores.sort(key=lambda item: item[1], reverse=True)
        limit = top_k or settings.VECTOR_TOP_K
        return scores[:limit]


def build_context_block(
    doc_matches: Sequence[Tuple[StoredChunk, float]],
    web_results: Sequence[dict],
) -> Tuple[str, List[dict]]:
    """Formats retrieved context and returns text + structured citations."""

    sections: List[str] = []
    sources: List[dict] = []

    if doc_matches:
        lines = ["=== DOCUMENT CONTEXT ==="]
        for idx, (chunk, score) in enumerate(doc_matches, start=1):
            lines.append(
                f"[Doc {idx}] Source: {chunk.document_name}\nRelevance: {score:.2f}\n{chunk.content}\n"
            )
            sources.append(
                {
                    "title": f"{chunk.document_name} · Chunk {idx}",
                    "snippet": chunk.content[:180] + ("…" if len(chunk.content) > 180 else ""),
                    "uri": None,
                    "type": "document",
                }
            )
        sections.append("\n".join(lines))

    if web_results:
        lines = ["=== LIVE WEB RESULTS ==="]
        for idx, result in enumerate(web_results, start=1):
            lines.append(
                f"[Web {idx}] {result.get('title', 'Result')}\nURL: {result.get('url')}\nSummary: {result.get('snippet', '')}\n"
            )
            sources.append(
                {
                    "title": result.get("title", f"Web Result {idx}"),
                    "snippet": result.get("snippet", ""),
                    "uri": result.get("url"),
                    "type": "web",
                }
            )
        sections.append("\n".join(lines))

    context_block = "\n\n".join(sections)
    limited_sources = sources[: settings.MAX_SOURCE_SNIPPETS]
    return context_block, limited_sources

