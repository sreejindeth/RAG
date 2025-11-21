# NeoStats Blueprint Copilot

A Streamlit chatbot that blends Retrieval-Augmented Generation with optional live web search and adjustable response modes (concise vs. detailed). Built entirely in Python following the NeoStats challenge structure.

## Project Layout
```
project/
├── app.py               # Streamlit UI and chat orchestration
├── config/
│   └── config.py        # Settings + system prompts
├── models/
│   ├── embeddings.py    # SentenceTransformer wrapper
│   └── llm.py           # Gemini client helper
├── utils/
│   ├── file_loader.py   # Upload parsing helpers
│   ├── rag.py           # Chunking, vector store, context formatting
│   └── web_search.py    # Tavily live search helper
└── requirements.txt
```

## Quick Start
1. `cd project`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Export keys:
   ```bash
   export GEMINI_API_KEY="your-key"
   export TAVILY_API_KEY="optional-web-search-key"
   ```
5. `streamlit run app.py`

Upload TXT/MD/PDF/CSV files from the sidebar, toggle live web search, pick a response style, and start chatting. Citations are shown under each assistant reply.

## Deployment
Deploy to Streamlit Cloud by connecting this folder’s repo, setting the same environment variables (GEMINI_API_KEY, optional TAVILY_API_KEY), and pointing to `app.py`.
