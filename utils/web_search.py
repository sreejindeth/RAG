"""Utility to perform live web searches via the Tavily API."""

from __future__ import annotations

import time
from typing import Dict, List

import requests

from config.config import settings

_CACHE: Dict[str, tuple[float, List[dict]]] = {}
_CACHE_TTL = 60.0


def _is_cache_valid(entry: tuple[float, List[dict]]) -> bool:
    return (time.time() - entry[0]) < _CACHE_TTL


def live_web_search(query: str) -> List[dict]:
    if not query.strip() or not settings.TAVILY_API_KEY:
        return []

    cached = _CACHE.get(query)
    if cached and _is_cache_valid(cached):
        return cached[1]

    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "max_results": settings.MAX_WEB_RESULTS,
    }

    try:
        response = requests.post(
            settings.TAVILY_API_URL,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    results = data.get("results", [])
    normalized = [
        {
            "title": item.get("title", "Web Result"),
            "url": item.get("url"),
            "snippet": item.get("content", ""),
        }
        for item in results
    ]

    _CACHE[query] = (time.time(), normalized)
    return normalized

