"""Gemini LLM Client - infrastructure service for interacting with Google Gemini API."""

from __future__ import annotations
from typing import Generator

from google import genai
from google.genai import types


class GeminiClient:
    """Infrastructure service that wraps the Google Gemini API for chat interactions.

    Maintains conversation history for multi-turn chat and streams responses.
    """

    MODEL = "gemini-3-flash-preview"

    SYSTEM_PROMPT = """Sen bir güzellik ürünleri uzmanı chatbot'sun. Trendyol'daki güzellik ürünleri veritabanından
elde edilen detaylı analizlere dayanarak kullanıcılara yardımcı oluyorsun.

Görevlerin:
1. Kullanıcıların sorularını veriye dayalı olarak yanıtlamak
2. Ürün önerileri yapmak (puan, yorum, fiyat/performans bazında)
3. Kategori bazında analizler sunmak
4. Yorum ve duygu analizlerini yorumlamak
5. Trend ürünleri ve kutuplaştırıcı ürünleri açıklamak
6. Fiyat karşılaştırmaları yapmak

Kuralların:
- Her zaman Türkçe yanıt ver
- Veriye dayalı konuş, tahmin yapma
- Kullanıcıya samimi ama profesyonel bir dille hitap et
- Fiyatları TL olarak belirt
- Ürün önerirken neden önerdiğini açıkla (yüksek puan, olumlu yorumlar, iyi fiyat/performans vb.)
- Olumsuz yorumları da dürüstçe paylaş, tek taraflı olma
- Eğer bir bilgiye sahip değilsen, bunu açıkça belirt

Aşağıda sana verilen analiz verileri, tüm katalog üzerinden yapılan kapsamlı bir analizdir.
Bu verileri kullanarak kullanıcının sorularını yanıtla."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._history: list[types.Content] = []
        self._context_injected = False

    def inject_context(self, analysis_context: str) -> None:
        """Inject the product analysis context as the first message in the conversation."""
        context_message = types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"İşte güzellik ürünleri veritabanının kapsamlı analizi:\n\n{analysis_context}\n\n"
                    "Bu verileri kullanarak sorularıma yanıt vereceksin. Hazır mısın?"
                ),
            ],
        )
        ack_message = types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text="Evet, güzellik ürünleri veritabanının analizini aldım. "
                    "Tüm kategoriler, puanlar, yorumlar, fiyat aralıkları ve trend ürünler hakkında "
                    "detaylı bilgiye sahibim. Sorularınızı yanıtlamaya hazırım!"
                ),
            ],
        )
        self._history = [context_message, ack_message]
        self._context_injected = True

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Send a message and stream the response back, maintaining conversation history."""
        if not self._context_injected:
            raise RuntimeError("Önce inject_context() ile analiz bağlamı yüklenmeli.")

        # Add user message to history
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
        self._history.append(user_content)

        config = types.GenerateContentConfig(
            system_instruction=self.SYSTEM_PROMPT,
            thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
        )

        full_response = []

        for chunk in self._client.models.generate_content_stream(
            model=self.MODEL,
            contents=self._history,
            config=config,
        ):
            text = chunk.text
            if text:
                full_response.append(text)
                yield text

        # Add assistant response to history
        assistant_content = types.Content(
            role="model",
            parts=[types.Part.from_text(text="".join(full_response))],
        )
        self._history.append(assistant_content)

    def chat(self, user_message: str) -> str:
        """Send a message and return the full response (non-streaming)."""
        return "".join(self.chat_stream(user_message))

    def reset_conversation(self) -> None:
        """Reset conversation history but keep the analysis context."""
        if self._context_injected and len(self._history) >= 2:
            self._history = self._history[:2]  # Keep only context + ack
        else:
            self._history = []
            self._context_injected = False
