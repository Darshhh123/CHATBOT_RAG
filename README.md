# RAG Chatbot - Animal Care Assistant

An AI-powered Retrieval-Augmented Generation (RAG) chatbot designed for educational animal care guidance and veterinary hospital information retrieval.  
The application uses a local Chroma vector database, LangChain orchestration, Gemini LLM integration, and a Streamlit-based user interface.

> ⚠️ Disclaimer: This project provides educational information only and should not be considered professional veterinary advice, diagnosis, or treatment.

---

# Features

- Retrieval-Augmented Generation (RAG)
- Local ChromaDB vector storage
- Educational animal care assistant
- Veterinary hospital information retrieval
- Gemini-powered conversational AI
- Prompt template orchestration using LangChain
- Streamlit-based web interface
- Local document ingestion pipeline
- Image input support using base64 encoding
- LangGraph workflow support

---

# Tech Stack

## Language
- Python 3.10+

---

## LLM & Orchestration
- LangChain
- LangChain Core
- LangChain Community
- LangChain Google GenAI
- LangGraph

---

## Vector Database
- ChromaDB
- Local SQLite-backed vector storage

---

## Embeddings
- Sentence Transformers

---

## Frontend/UI
- Streamlit
- HTML/CSS/JavaScript assets

---

---

## Image Processing
- Pillow (PIL)

---

## Additional Tools
- pathlib
- os
- base64

---

# Project Structure

```bash
RAG_Chatbot/
│
├── app.py                     # Streamlit app entry point
├── care_llm.py                # LLM + RAG orchestration
├── requirements.txt           # Project dependencies
├── chroma.sqlite3             # Local Chroma vector database
│
├── templates/                 # Frontend templates
├── js/                        # JavaScript assets
├── css/                       # CSS assets
│
├── data/
│   └── hospitals/             # Veterinary hospital data
│
├── env2/                      # Optional local virtual environment
│
└── README.md
