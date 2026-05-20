"""
RAG chatbot service for the Constitution of India.
Sets up the LangChain RAG chain with Mistral AI LLM.
"""

import os
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from backend.services.retriever import get_retriever
from backend.utils.logger import logger

# Load environment variables from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def format_docs(docs):
    """Format retrieved documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def get_chatbot():
    """
    Initialize and return the RAG chain and retriever.
    
    Returns:
        tuple: (rag_chain, retriever) — the chain to invoke with a question,
               and the retriever for fetching source documents.
    """
    logger.info("Initializing chatbot...")

    retriever = get_retriever()

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables. Check your .env file.")

    llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=api_key,
        temperature=0.1,
        max_tokens=512
    )

    template = """You are an expert assistant on the Constitution of India.

Use the context below to answer the question. Base your answer on the provided context.

Guidelines:
- Reference specific articles, parts, or sections when relevant
- Provide comprehensive, well-structured answers
- If the context contains related information, use it to build your answer
- If you truly cannot find any relevant information in the context, say "I don't have enough information about this specific topic in the available context."
- Be helpful and informative

Context:
{context}

Question: {question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info("Chatbot initialized successfully")
    return rag_chain, retriever
