# basic_rag_try
# Local RAG

A private, high-accuracy RAG system for analyzing legal contracts. 
Optimized for **Intel Ultra 5** and **Arc Graphics**.

## 🚀 Setup
1. Install [Ollama](https://ollama.com) and pull models:
   `ollama pull llama3.2` && `ollama pull nomic-embed-text`
2. Create environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run app: `streamlit run src/app.py`

## 🛡️ Privacy
This system is 100% local. No data is sent to the cloud.
