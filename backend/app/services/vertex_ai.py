from __future__ import annotations

from typing import Any, Dict, List, Optional

from google.cloud import aiplatform

from ..config import get_settings


class VertexAIClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._model: Optional[aiplatform.gapic.PredictionServiceClient] = None
        if self._settings.enable_google_services and self._settings.google_project_id:
            try:
                aiplatform.init(project=self._settings.google_project_id, location=self._settings.google_location)
            except Exception:
                return

    def generate_deal_notes(
        self,
        prompt: str,
        context_chunks: List[str],
        output_type: str = "summary",
    ) -> str:
        if not self._settings.enable_google_services or not self._settings.google_project_id:
            return self._fallback(prompt, context_chunks, output_type)
        try:
            model = aiplatform.GenerativeModel(self._settings.vertex_model)
            response = model.generate_content([
                {
                    "role": "system",
                    "parts": [
                        {
                            "text": (
                                "You are an elite venture analyst producing {} deal notes."
                                "Focus on clarity, evidence, and investment diligence."
                            ).format(output_type)
                        }
                    ],
                },
                {"role": "user", "parts": [{"text": prompt}]},
                {"role": "user", "parts": [{"text": "\n\n".join(context_chunks)}]},
            ])
            return response.text or self._fallback(prompt, context_chunks, output_type)
        except Exception:
            return self._fallback(prompt, context_chunks, output_type)

    @staticmethod
    def _fallback(prompt: str, context_chunks: List[str], output_type: str) -> str:
        joined = "\n\n".join(context_chunks[-5:])
        header = f"[{output_type.upper()}]"
        body = f"Prompt: {prompt}\n\nContext Snapshot:\n{joined}"[:4000]
        footer = "\n\n(Enable Vertex AI for richer analysis.)"
        return f"{header}\n{body}{footer}"


_vertex_client: VertexAIClient | None = None


def get_vertex_client() -> VertexAIClient:
    global _vertex_client
    if _vertex_client is None:
        _vertex_client = VertexAIClient()
    return _vertex_client
