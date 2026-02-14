"""Chatbot Service - application service that orchestrates the chatbot experience."""

from __future__ import annotations
from typing import Generator

from chatbot.application.services.analysis_service import AnalysisService
from chatbot.infrastructure.llm.gemini_client import GeminiClient


class ChatbotService:
    """Application service that ties together analysis and LLM for the chatbot.

    This is the main orchestrator that:
    1. Loads and analyzes product data
    2. Injects analysis context into the LLM
    3. Handles user conversations
    """

    def __init__(self, csv_path: str, gemini_api_key: str) -> None:
        self._analysis_service = AnalysisService(csv_path)
        self._llm_client = GeminiClient(gemini_api_key)
        self._initialized = False

    def initialize(self) -> str:
        """Initialize the chatbot: load data, analyze, and inject context into LLM.

        Returns a status message about the loaded data.
        """
        # Step 1: Load and analyze data
        self._analysis_service.initialize()
        catalog = self._analysis_service.catalog

        # Step 2: Generate analysis context
        llm_context = self._analysis_service.get_llm_context()

        # Step 3: Inject context into LLM
        self._llm_client.inject_context(llm_context)

        self._initialized = True

        return (
            f"Veriler yüklendi: {catalog.total_products} ürün, "
            f"{len(catalog.categories)} kategori analiz edildi."
        )

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Process a user message and stream the response."""
        self._ensure_initialized()
        yield from self._llm_client.chat_stream(user_message)

    def chat(self, user_message: str) -> str:
        """Process a user message and return the full response."""
        self._ensure_initialized()
        return self._llm_client.chat(user_message)

    def reset_conversation(self) -> None:
        """Reset the conversation while keeping the analysis context."""
        self._llm_client.reset_conversation()

    def get_quick_stats(self) -> str:
        """Get a quick stats summary without using the LLM."""
        self._ensure_initialized()
        overview = self._analysis_service.analyzer.catalog_overview()
        sentiment = self._analysis_service.analyzer.sentiment_analysis_summary()

        lines = [
            f"Toplam Ürün: {overview['total_products']}",
            f"Kategori Sayısı: {overview['total_categories']}",
            f"Ortalama Puan: {overview['average_rating']}",
            f"Yorumlu Ürün: {overview['products_with_comments']}",
            f"Toplam Yorum: {sentiment['total_comments']}",
            f"Olumlu Yorum Oranı: {sentiment['positive_ratio']:.0%}",
            f"Trend Ürün: {overview['trending_count']}",
        ]
        return "\n".join(lines)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("Chatbot henüz başlatılmadı. Önce initialize() çağrılmalı.")
