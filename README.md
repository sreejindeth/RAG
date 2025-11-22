# NeoStats Blueprint Copilot

> A Streamlit-native financial copilot that blends Retrieval-Augmented Generation (RAG), live web search, and toggleable response modes to help analysts “imagine, build, solve.”

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Environment Setup](#environment-setup)
5. [Running Locally](#running-locally)
6. [Deployment Guide](#deployment-guide)
7. [Configuration Reference](#configuration-reference)
8. [Data & Control Flow](#data--control-flow)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap](#roadmap)

---

## Overview
- **Use Case:** Financial teams upload internal research, toggle live market search, and get contextual answers with citations.
- **Spec Compliance:** Pure Python/Streamlit codebase with `config/`, `models/`, `utils/`, `app.py`, `requirements.txt`.
- **LLM:** Google Gemini (`gemini-2.0-flash`).
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` for local vector search.
- **Live Search:** Tavily API (optional).

---

## Architecture
```
project/
├── app.py                 # Streamlit UI & orchestration
├── config/
│   └── config.py          # Settings dataclass, system prompt, response modes
├── models/
│   ├── embeddings.py      # SentenceTransformer wrapper + caching
│   └── llm.py             # Gemini client helper
├── utils/
│   ├── file_loader.py     # TXT/MD/PDF/CSV ingestion helpers
│   ├── rag.py             # Chunking, vector store, context builder
│   └── web_search.py      # Tavily HTTP client with caching
├── requirements.txt
├── README.md
└── project_overview.txt   # PPT-ready summary
```

---

## Key Features
1. **Retrieval-Augmented Generation:** Upload documents; the app chunks (700 tokens / 120 overlap), embeds, and retrieves relevant passages per query.
2. **Live Web Search:** Optional Tavily integration provides fresh headlines when internal docs lack the answer.
3. **Response Modes:** Concise vs. Detailed toggle adapts Gemini’s system instruction for each turn.
4. **Transparent Citations:** Assistant replies show which document chunks or web links were used.
5. **Robust UX:** Streamlit chat history, upload controls, and graceful error handling keep sessions stable.

---

## Environment Setup
1. Clone/download the `project/` directory.
2. Create and activate a virtual environment:
   ```bash
   cd project
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env.local` (ignored by git) and populate it:
   ```bash
   cat <<'EOF_ENV' > .env.local
   GEMINI_API_KEY=your_gemini_key
   TAVILY_API_KEY=your_tavily_key   # optional
   EOF_ENV
   ```
5. Load the environment variables:
   ```bash
   set -a
   source .env.local
   set +a
   ```

---

## Running Locally
```bash
streamlit run app.py
```
- Visit the localhost URL shown in the terminal.
- Upload TXT/MD/PDF/CSV files from the sidebar.
- Toggle live web search and choose the response mode.
- Ask questions via the chat input; sources appear under each assistant reply.

---

## Deployment Guide
### Streamlit Cloud
1. Push this `project/` folder to GitHub (remove `.env.local`, `.venv`, `__pycache__`).
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → “New app”.
3. Select the repo/branch containing `project/app.py`.
4. Under “Secrets”, add:
   ```
   GEMINI_API_KEY = "your_key"
   TAVILY_API_KEY = "optional_key"
   ```
5. Deploy and capture the Streamlit Cloud URL for your deliverables.

### Self-hosted
- Run `streamlit run app.py` on your server/container after exporting the same env vars.
- Optional: put an nginx proxy with TLS in front for production.

---

## Configuration Reference
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | NeoStats Blueprint Copilot | Display name |
| `GEMINI_MODEL` | `gemini-2.5-flash` | LLM used |
| `GEMINI_API_KEY` | — | **Required** key |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embeddings |
| `TAVILY_API_KEY` | — | Optional live search key |
| `TAVILY_API_URL` | `https://api.tavily.com/search` | Search endpoint |
| `MAX_WEB_RESULTS` | 3 | Tavily results per query |
| `VECTOR_TOP_K` | 4 | Document chunks returned |
| `MAX_SOURCE_SNIPPETS` | 4 | Citations shown per answer |

Override any of these by exporting environment variables or setting Streamlit secrets.

---

## Data & Control Flow
1. **Upload:** `file_loader.py` parses each file → `rag.py` chunks + embeds → stored in-memory vector store.
2. **Prompt:** User submits a question → optional Tavily search → vector similarity search → top chunks selected.
3. **Context Assembly:** `build_context_block` merges document + web snippets and assembles citations.
4. **LLM Response:** `GeminiClient.generate()` composes system instruction (base prompt + context + response mode) and calls `generate_content`.
5. **Display:** Assistant reply + citations are appended to session state and rendered in Streamlit.

---

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| `Missing GEMINI_API_KEY` | Ensure `.env.local` is sourced or secrets set in Streamlit Cloud. |
| `Gemini quota exhausted (429)` | Wait for quota reset or rotate keys. Web sources still show, but no AI answer is produced. |
| `Web search returns nothing` | Confirm `TAVILY_API_KEY`; if absent, the toggle safely does nothing. |
| PDF parsing errors | PyPDF2 falls back to blank text; convert to TXT if extraction fails. |
| Large uploads slow search | This in-memory store targets small datasets (<10 MB). Consider FAISS/Chroma/Pinecone for large corpora. |

---

## Roadmap
- Persistent vector store (FAISS/Chroma/Pinecone) for larger corpora.
- Additional file formats (XLSX, PPTX) and metadata filtering.
- Finance data tools (Alpha Vantage, Yahoo Finance) as extra “skills.”
- Automated unit tests for chunking/search utilities.
- Chat transcript export and multi-session history.

---

For a PPT-ready narrative (objective, features, challenges, deployment), see `project_overview.txt`. Contributions welcome—open an issue or PR with your ideas! 🚀
