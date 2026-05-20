"""
Flask application entry point for the Constitution of India RAG Chatbot.
"""

import os
import sys

# Ensure project root is on the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.routes.chat import chat_bp, init_chat_service
from backend.services.chatbot import get_chatbot
from backend.utils.logger import logger

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__, static_folder=None)
    CORS(app)

    # Initialize the chatbot (loads models — may take a moment)
    logger.info("=" * 50)
    logger.info("Starting Constitution of India RAG Chatbot")
    logger.info("=" * 50)

    qa_chain, retriever = get_chatbot()
    init_chat_service(qa_chain, retriever)

    # Register API routes
    app.register_blueprint(chat_bp)

    # Serve frontend static files
    @app.route("/")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    logger.info("Application ready - serving on http://localhost:5000")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=5000)
