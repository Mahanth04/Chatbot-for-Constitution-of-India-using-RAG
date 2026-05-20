"""
FAISS index ingestion script.
Reads the Constitution text, chunks it, and builds the vector index.
Run this once before starting the chatbot.
"""

import os
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.services.retriever import get_embeddings
from backend.utils.logger import logger

# Resolve paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "constitution.txt")
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_index")


def create_vector_db():
    """
    Build the FAISS vector index from the Constitution text file.
    Uses article-aware chunking to keep article text together.
    """
    logger.info("Starting ingestion from: %s", DATA_PATH)

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Data file not found: %s" % DATA_PATH)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        full_text = f.read()

    logger.info("Full text length: %d characters", len(full_text))

    # Split into article-aware chunks using regex for article boundaries
    # First do a coarse split by article patterns, then sub-chunk large pieces
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=150,
        separators=[
            "\n\n\n",          # Major section breaks
            "\n\n",            # Paragraph breaks
            "\n",              # Line breaks
            ". ",              # Sentences
            " ",               # Words
        ],
        keep_separator=True,
    )

    # Load as LangChain document
    loader = TextLoader(DATA_PATH, encoding="utf-8")
    documents = loader.load()

    docs = splitter.split_documents(documents)
    logger.info("Total chunks created: %d", len(docs))

    # Log some sample chunks for verification
    if docs:
        logger.info("Sample chunk 0: %s", docs[0].page_content[:100])
        mid = len(docs) // 2
        logger.info("Sample chunk %d: %s", mid, docs[mid].page_content[:100])

    embeddings = get_embeddings()

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(FAISS_INDEX_PATH)

    logger.info("FAISS index saved to: %s (%d vectors)", FAISS_INDEX_PATH, len(docs))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    create_vector_db()
