import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.node_parser import SentenceSplitter

# --- Configuration ---
# 1. Setup the Embedding Model (The "Search Engine")
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

# 2. Setup the LLM (The "Reasoning Engine")
# Using the model ID from your screenshot
Settings.llm = Ollama(
    model="gemma3:latest", 
    request_timeout=300.0
)

# 3. Setup Chunking (How we split text)
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

def main():
    print("🚀 Starting Local RAG Pipeline...")

    # --- Step A: Create Dummy Data ---
    # We will create a test file directly to ensure you have something to search.
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open("data/test_doc.txt", "w", encoding="utf-8") as f:
        f.write("""
        Project Zero-Cost is a strict initiative to build a RAG pipeline without spending money.
        It utilizes Ollama for local LLMs, Minikube for orchestration, and ChromaDB for vector storage.
        The project is deployed on a Windows 11 host using WSL2.
        The primary engineer is an expert in Kubernetes and MLOps.
        """)
    print("✅ Created dummy document in 'data/test_doc.txt'")

    # --- Step B: Ingest & Index ---
    print("⏳ Loading and indexing documents (this uses nomic-embed-text)...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    print("✅ Indexing complete! Embeddings stored in memory.")

    # --- Step C: Query ---
    query_engine = index.as_query_engine()
    question = "What tools are used in Project Zero-Cost?"
    
    print(f"\n❓ Question: {question}")
    print("⏳ Generating answer with gemma3...")
    
    response = query_engine.query(question)
    
    print(f"\n💡 Answer:\n{response}")

if __name__ == "__main__":
    main()
