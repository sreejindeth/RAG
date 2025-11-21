import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Central configuration for the NeoStats Streamlit chatbot."""

    APP_NAME: str = os.getenv("APP_NAME", "NeoStats Blueprint Copilot")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    TAVILY_API_URL: str = os.getenv("TAVILY_API_URL", "https://api.tavily.com/search")
    MAX_SOURCE_SNIPPETS: int = int(os.getenv("MAX_SOURCE_SNIPPETS", 4))
    MAX_WEB_RESULTS: int = int(os.getenv("MAX_WEB_RESULTS", 3))
    VECTOR_TOP_K: int = int(os.getenv("VECTOR_TOP_K", 4))


settings = Settings()

SYSTEM_PROMPT = (
    "You are NeoStats, an elite financial strategist helping professionals reason with "
    "both proprietary knowledge bases and the live web. Be transparent about your "
    "sources and warn when information may be outdated."
)

RESPONSE_MODES = {
    "Concise": (
        "Provide a concise answer in at most three short paragraphs or bullet points. "
        "Focus on the highest-signal insights and avoid filler."
    ),
    "Detailed": (
        "Provide a full analysis with background context, calculations, and risk "
        "considerations. Anticipate follow-up questions and explain why your "
        "recommendations matter."
    ),
}

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

