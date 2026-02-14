"""Web Presentation Layer - Flask server with SSE streaming for the chatbot UI."""

from __future__ import annotations
import os
import json
from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory

from chatbot.application.services.chatbot_service import ChatbotService


def create_app(csv_path: str | None = None, api_key: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
        static_url_path="/static",
    )

    # Resolve paths
    if not csv_path:
        csv_path = os.environ.get("BEAUTYBOT_CSV_PATH")
    if not csv_path:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(project_root, "all_categories_20250207_031918.csv")

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY ortam değişkeni ayarlanmamış.")

    # Initialize chatbot service (singleton for this app instance)
    chatbot = ChatbotService(csv_path=csv_path, gemini_api_key=api_key)
    status = chatbot.initialize()
    print(f"✓ {status}")

    # --- Routes ---

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/api/stats")
    def stats():
        """Return quick stats as JSON."""
        overview = chatbot._analysis_service.analyzer.catalog_overview()
        sentiment = chatbot._analysis_service.analyzer.sentiment_analysis_summary()
        return jsonify({
            "total_products": overview["total_products"],
            "total_categories": overview["total_categories"],
            "categories": overview["categories"],
            "average_rating": overview["average_rating"],
            "products_with_comments": overview["products_with_comments"],
            "total_comments": sentiment["total_comments"],
            "positive_ratio": sentiment["positive_ratio"],
            "negative_ratio": sentiment["negative_ratio"],
            "trending_count": overview["trending_count"],
        })

    @app.route("/api/insights")
    def insights():
        """Return detailed insights as JSON."""
        analyzer = chatbot._analysis_service.analyzer
        return jsonify({
            "top_commented": analyzer.most_discussed_products(5),
            "top_engaging": analyzer.engagement_leaders(5),
            "polarizing": analyzer.polarizing_products(5),
            "best_value": analyzer.best_value_products(5),
            "price_by_category": analyzer.price_comparison_by_category(),
        })

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Handle chat message and return streamed response via SSE."""
        data = request.get_json()
        if not data or not data.get("message"):
            return jsonify({"error": "Mesaj gerekli."}), 400

        message = data["message"].strip()
        if not message:
            return jsonify({"error": "Boş mesaj gönderilemez."}), 400

        def generate():
            try:
                for chunk in chatbot.chat_stream(message):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @app.route("/api/reset", methods=["POST"])
    def reset():
        """Reset the conversation."""
        chatbot.reset_conversation()
        return jsonify({"status": "ok", "message": "Konuşma sıfırlandı."})

    return app


def main() -> None:
    """Entry point for the web server."""
    import sys
    port = int(os.environ.get("PORT", 5000))

    # Parse --port from command line
    args = sys.argv[1:]
    if "--port" in args:
        idx = args.index("--port")
        if idx + 1 < len(args):
            port = int(args[idx + 1])

    app = create_app()
    print(f"🌐 Trendyol BeautyBot Web UI: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
