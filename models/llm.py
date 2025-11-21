"""LLM helpers for talking to Google Gemini."""

from __future__ import annotations

from typing import List, Dict

import google.generativeai as genai

from config.config import settings, SYSTEM_PROMPT, RESPONSE_MODES


def _format_history(history: List[Dict[str, str]]) -> List[Dict[str, object]]:
    contents: List[Dict[str, object]] = []
    for message in history:
        role = message.get("role", "user")
        text = message.get("content", "")
        if not text:
            continue
        contents.append({"role": role, "parts": [text]})
    return contents


class GeminiClient:
    """Simple wrapper around google-generativeai."""

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "Missing GEMINI_API_KEY. Set it as an environment variable before running the app."
            )

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)

    def generate(
        self,
        history: List[Dict[str, str]],
        response_mode: str,
        context_block: str,
    ) -> str:
        system_instruction = SYSTEM_PROMPT
        if context_block:
            system_instruction += f"\n\nAdditional Context:\n{context_block}"

        mode_instruction = RESPONSE_MODES.get(response_mode, "")
        if mode_instruction:
            system_instruction += f"\n\nResponse Style:\n{mode_instruction}"

        contents = _format_history(history)
        if not contents:
            raise ValueError("History must include at least one user message.")

        try:
            response = self.model.generate_content(
                contents=contents,
                system_instruction=system_instruction,
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "max_output_tokens": 1024,
                },
            )
        except Exception as exc:  # pragma: no cover - handled at runtime
            raise RuntimeError(f"Gemini generation failed: {exc}") from exc

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()

