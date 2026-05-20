"""
Advanced retriever with cross-encoder reranking for the Constitution of India.
Uses FAISS vector store + BGE embeddings + MS-MARCO cross-encoder.
"""

import os
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from backend.utils.logger import logger

# Resolve paths relative to project root (parent of backend/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_index")

# Embedding model configuration
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Create and return the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


class RerankedRetriever(BaseRetriever):
    """Custom retriever with cross-encoder reranking for higher quality results."""

    embeddings: HuggingFaceEmbeddings = None
    db: FAISS = None
    reranker: CrossEncoder = None

    def __init__(self):
        super().__init__()
        logger.info("Loading embeddings model: %s", EMBEDDING_MODEL)
        self.embeddings = get_embeddings()

        logger.info("Loading FAISS index from: %s", FAISS_INDEX_PATH)
        self.db = FAISS.load_local(
            FAISS_INDEX_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        logger.info("Loading reranker model: %s", RERANKER_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL)
        logger.info("Retriever initialized successfully")

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """
        Retrieve and rerank documents for the given query.
        
        1. Fetch 10 initial candidates via FAISS similarity search
        2. Rerank using cross-encoder
        3. Return top 5 results
        """
        # Step 1: Get initial candidates
        initial_docs = self.db.similarity_search(query, k=20)

        # Step 2: Score with cross-encoder
        pairs = [[query, doc.page_content] for doc in initial_docs]
        scores = self.reranker.predict(pairs)

        # Step 3: Sort by reranker scores (descending)
        doc_score_pairs = sorted(
            zip(initial_docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Step 4: Return top 5
        return [doc for doc, _ in doc_score_pairs[:8]]


def get_retriever() -> RerankedRetriever:
    """Factory function to create a RerankedRetriever instance."""
    return RerankedRetriever()
