from __future__ import annotations

import streamlit as st

from config.config import settings, RESPONSE_MODES
from models.embeddings import get_embedding_model
from models.llm import GeminiClient
from utils.file_loader import load_document
from utils.rag import InMemoryVectorStore, build_context_block
from utils.web_search import live_web_search

st.set_page_config(page_title=settings.APP_NAME, layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm NeoStats, your financial research copilot. Upload reports, "
                "toggle live web search, and pick a response style to tailor the "
                "analysis." 
            ),
        }
    ]

if "vector_store" not in st.session_state:
    st.session_state.vector_store = InMemoryVectorStore()

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

if "response_mode" not in st.session_state:
    st.session_state.response_mode = "Detailed"

if "enable_search" not in st.session_state:
    st.session_state.enable_search = False


def _init_llm() -> GeminiClient | None:
    if "llm" in st.session_state:
        return st.session_state.llm
    try:
        st.session_state.llm = GeminiClient()
        return st.session_state.llm
    except ValueError as exc:
        st.error(str(exc))
    except RuntimeError as exc:
        st.error(f"LLM initialization failed: {exc}")
    return None


embedding_model = get_embedding_model()
llm = _init_llm()

with st.sidebar:
    st.title("Control Center")
    st.markdown(
        "Manage your knowledge base and retrieval behavior. Uploaded files stay in-memory only."
    )

    uploaded_files = st.file_uploader(
        "Upload financial docs",
        type=["txt", "md", "pdf", "csv", "tsv"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        for file in uploaded_files:
            try:
                name, content = load_document(file)
                added = st.session_state.vector_store.add_document(
                    name, content, embedding_model
                )
                st.session_state.uploaded_docs.append(name)
                st.success(f"Indexed {added} chunks from {name}.")
            except Exception as exc:  # pragma: no cover - UI feedback
                st.warning(f"Failed to ingest {file.name}: {exc}")

    if st.session_state.uploaded_docs:
        st.caption("Loaded documents:")
        for doc in st.session_state.uploaded_docs[-10:]:
            st.write(f"• {doc}")
        if st.button("Clear knowledge base"):
            st.session_state.vector_store.clear()
            st.session_state.uploaded_docs = []
            st.success("Cleared cached documents.")

    st.session_state.enable_search = st.toggle(
        "Enable live web search", value=st.session_state.enable_search
    )
    response_options = list(RESPONSE_MODES.keys())
    st.session_state.response_mode = st.radio(
        "Response style",
        options=response_options,
        index=response_options.index(st.session_state.response_mode),
    )

st.title(settings.APP_NAME)
st.markdown(
    "Use Retrieval-Augmented Generation with live search to craft informed answers."
)

chat_placeholder = st.container()
with chat_placeholder:
    for message in st.session_state.messages:
        avatar = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(avatar):
            st.markdown(message["content"])
            sources = message.get("sources")
            if sources:
                with st.expander("Sources"):
                    for source in sources:
                        label = source.get("title", "Source")
                        snippet = source.get("snippet", "")
                        url = source.get("uri")
                        text = f"**{label}** — {snippet}" if snippet else f"**{label}**"
                        if url:
                            st.markdown(f"[{text}]({url})")
                        else:
                            st.markdown(text)

prompt = st.chat_input("Ask anything about markets, strategy, or uploaded docs…")
if prompt and llm:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("NeoStats is thinking…"):
        sources = []
        try:
            doc_matches = st.session_state.vector_store.similarity_search(
                prompt, embedding_model, settings.VECTOR_TOP_K
            )
        except Exception as exc:
            doc_matches = []
            st.warning(f"Vector search failed: {exc}")

        web_results = []
        if st.session_state.enable_search:
            try:
                web_results = live_web_search(prompt)
            except Exception as exc:
                st.info(f"Web search unavailable: {exc}")

        context_block, sources = build_context_block(doc_matches, web_results)

        history = st.session_state.messages.copy()
        try:
            response_text = llm.generate(
                history=history,
                response_mode=st.session_state.response_mode,
                context_block=context_block,
            )
        except Exception as exc:
            response_text = "I encountered an error generating a response."
            st.error(str(exc))

    st.session_state.messages.append(
        {"role": "assistant", "content": response_text, "sources": sources}
    )
    st.rerun()
