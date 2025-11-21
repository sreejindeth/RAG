"""Utilities for parsing uploaded files into raw text."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Tuple

import pandas as pd
import PyPDF2
from streamlit.runtime.uploaded_file_manager import UploadedFile


def _read_text(buffer: BytesIO, encoding: str = "utf-8") -> str:
    buffer.seek(0)
    return buffer.read().decode(encoding, errors="ignore")


def _read_pdf(buffer: BytesIO) -> str:
    buffer.seek(0)
    reader = PyPDF2.PdfReader(buffer)
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)


def _read_csv(buffer: BytesIO) -> str:
    buffer.seek(0)
    df = pd.read_csv(buffer)
    return df.to_csv(index=False)


def load_document(upload: UploadedFile) -> Tuple[str, str]:
    """Returns (document_name, text_content) for an uploaded file."""

    suffix = Path(upload.name).suffix.lower()
    content = ""
    data = BytesIO(upload.getvalue())

    if suffix in {".txt", ".md"}:
        content = _read_text(data)
    elif suffix == ".pdf":
        content = _read_pdf(data)
    elif suffix in {".csv", ".tsv"}:
        content = _read_csv(data)
    else:
        content = _read_text(data)

    return upload.name, content

