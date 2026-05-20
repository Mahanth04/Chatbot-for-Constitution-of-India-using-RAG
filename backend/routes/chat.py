"""
Chat route — handles the POST /chat endpoint.
"""

from flask import Blueprint, request, jsonify
from backend.utils.logger import logger

chat_bp = Blueprint("chat", __name__)

# These will be set by the app factory after initialization
qa_chain = None
retriever = None


def init_chat_service(chain, ret):
    """
    Inject the chatbot chain and retriever into this module.
    Called once at startup from app.py.
    """
    global qa_chain, retriever
    qa_chain = chain
    retriever = ret


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Handle a chat message from the user.
    
    Request JSON:
        {"message": "user question"}
    
    Response JSON:
        {"response": "chatbot reply"}
    """
    try:
        data = request.get_json(silent=True)

        if not data or "message" not in data:
            logger.warning("Bad request: missing 'message' field")
            return jsonify({"error": "Request must include a 'message' field."}), 400

        message = data["message"].strip()

        if not message:
            logger.warning("Bad request: empty message")
            return jsonify({"error": "Message cannot be empty."}), 400

        logger.info("Question received: %s", message[:100])

        # Get answer from RAG chain
        answer = qa_chain.invoke(message)

        logger.info("Answer generated successfully (%d chars)", len(answer))

        return jsonify({"response": answer})

    except Exception as e:
        logger.error("Error processing chat request: %s", str(e), exc_info=True)
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


@chat_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})
