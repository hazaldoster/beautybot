"""Analysis Service - application service that orchestrates data loading and analysis."""

from __future__ import annotations

from chatbot.domain.entities.product_catalog import ProductCatalog
from chatbot.domain.services.product_analyzer import ProductAnalyzer
from chatbot.application.dto.insight_dto import InsightDTO, CategoryInsightDTO
from chatbot.infrastructure.data.csv_product_repository import CsvProductRepository


class AnalysisService:
    """Application service that coordinates loading data and running analysis.

    Acts as the bridge between infrastructure (CSV loading) and domain (analysis).
    """

    def __init__(self, csv_path: str) -> None:
        self._repository = CsvProductRepository(csv_path)
        self._catalog: ProductCatalog | None = None
        self._analyzer: ProductAnalyzer | None = None

    def initialize(self) -> None:
        """Load data and prepare the analyzer."""
        self._catalog = self._repository.load_catalog()
        self._analyzer = ProductAnalyzer(self._catalog)

    @property
    def catalog(self) -> ProductCatalog:
        if self._catalog is None:
            raise RuntimeError("Önce initialize() çağrılmalı.")
        return self._catalog

    @property
    def analyzer(self) -> ProductAnalyzer:
        if self._analyzer is None:
            raise RuntimeError("Önce initialize() çağrılmalı.")
        return self._analyzer

    def generate_full_insights(self) -> InsightDTO:
        """Generate complete insights DTO with all analysis results."""
        analyzer = self.analyzer
        catalog = self.catalog

        # Build category insights
        category_insights = []
        for cat in catalog.categories:
            cat_analysis = analyzer.category_analysis(cat)
            if "error" not in cat_analysis:
                category_insights.append(
                    CategoryInsightDTO(
                        category=cat,
                        product_count=cat_analysis["product_count"],
                        average_rating=cat_analysis["average_rating"],
                        total_comments=cat_analysis["total_comments"],
                        price_range=cat_analysis["price_range"],
                        top_products=cat_analysis["top_rated"],
                    )
                )

        return InsightDTO(
            catalog_overview=analyzer.catalog_overview(),
            sentiment_summary=analyzer.sentiment_analysis_summary(),
            top_commented=analyzer.most_discussed_products(5),
            top_engaging=analyzer.engagement_leaders(5),
            polarizing=analyzer.polarizing_products(5),
            best_value=analyzer.best_value_products(5),
            category_insights=category_insights,
            llm_context=analyzer.generate_llm_context(),
        )

    def get_llm_context(self) -> str:
        """Get the analysis context string for the LLM."""
        return self.analyzer.generate_llm_context()
