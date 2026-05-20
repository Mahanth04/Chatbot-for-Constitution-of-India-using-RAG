# Constitution of India — RAG AI Chatbot

An AI-powered chatbot that answers questions about the Constitution of India using Retrieval-Augmented Generation (RAG) with LangChain, FAISS, and Mistral AI.

## Features

- **RAG Pipeline** — Retrieves relevant constitutional text and generates accurate answers
- **Cross-Encoder Reranking** — Improves retrieval quality using MS-MARCO reranker
- **Modern Chat UI** — Dark-themed, glassmorphism design with typing animations
- **Flask API** — Clean REST API with CORS and error handling

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_api_key_here
```

### 3. Build FAISS index (first time only)

```bash
python -m backend.services.ingest
```

### 4. Run the application

```bash
python backend/app.py
```

Open **http://localhost:5000** in your browser.

## Project Structure

```
├── .env                    # API keys (not committed)
├── requirements.txt        # Python dependencies
├── Constitution_of_India.pdf
├── data/
│   └── constitution.txt    # Extracted text
├── faiss_index/            # Vector store
├── backend/
│   ├── app.py              # Flask entry point
│   ├── routes/
│   │   └── chat.py         # POST /chat endpoint
│   ├── services/
│   │   ├── chatbot.py      # RAG chain setup
│   │   ├── retriever.py    # FAISS + reranker
│   │   └── ingest.py       # Index builder
│   └── utils/
│       └── logger.py       # Logging config
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## API

### POST /chat

```json
// Request
{ "message": "What is Article 21?" }

// Response
{ "response": "Article 21 protects the right to life..." }
```

### GET /health

```json
{ "status": "healthy" }
```

## Tech Stack

- **LLM**: Mistral AI (mistral-small-latest)
- **Embeddings**: BAAI/bge-base-en-v1.5
- **Reranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Vector Store**: FAISS
- **Backend**: Flask + LangChain
- **Frontend**: Vanilla HTML/CSS/JS
