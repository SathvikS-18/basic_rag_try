import streamlit as st
import os
import chromadb
from markitdown import MarkItDown
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.postprocessor import LLMRerank
from llama_index.postprocessor.flashrank import FlashRankRerank

# --- 1. SETTINGS & HARDWARE OPTIMIZATION ---
Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

st.set_page_config(page_title="Production Contract AI", layout="wide")
st.title("🛡️ Production-Grade Local Contract Analyzer")

# --- 2. PERSISTENT DATABASE SETUP ---
# This ensures your uploaded contracts stay saved on your hard drive
CHROMA_PATH = "./contract_db"
db = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = db.get_or_create_collection("vendor_contracts")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# --- 3. THE RE-RANKER (Production Accuracy) ---
# This second AI checks the top 10 search results to find the #1 best answer
reranker = FlashRankRerank(top_n=3)

# --- 4. DATA PROCESSING ---
uploaded_file = st.sidebar.file_uploader("Upload Vendor Contract (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Parsing contract tables and clauses..."):
        # Save temp file for MarkItDown to read
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # MarkItDown handles complex PDF tables much better than standard readers
        md = MarkItDown()
        parsed = md.convert("temp.pdf")
        
        # Save to database
        doc = Document(text=parsed.text_content, metadata={"filename": uploaded_file.name})
        index = VectorStoreIndex.from_documents([doc], storage_context=storage_context)
        st.sidebar.success(f"Indexed: {uploaded_file.name}")

# --- 5. THE SEARCH ENGINE ---
query = st.text_input("Analyze your contract (e.g., 'What is the liability cap?')")

if query:
    # We grab 10 results, then the Re-ranker filters them down to the best 3
    query_engine = index.as_query_engine(
        similarity_top_k=10, 
        node_postprocessors=[reranker]
    )
    
    with st.spinner("Reasoning..."):
        response = query_engine.query(query)
        
        st.subheader("Legal Analysis")
        st.markdown(response.response)
        
        with st.expander("View Evidence & Citations"):
            for node in response.source_nodes:
                st.write(f"**Relevance Score: {node.score:.2f}**")
                st.info(node.node.get_content())