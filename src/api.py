import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.node_parser import SentenceSplitter

# --- Setup Global Settings (Same as before) ---
#Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=OLLAMA_URL)
Settings.llm = Ollama(model="gemma3:latest", base_url=OLLAMA_URL, request_timeout=300.0)
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

app = FastAPI(title="Zero-Cost RAG API")

# Global variables to hold the index in memory
INDEX_DIR = "./chroma_db"
UPLOAD_DIR = "./data_uploads"
index = None

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def initialize_index():
    """Load index from disk or create a new one."""
    global index
    if os.path.exists(INDEX_DIR) and os.listdir(INDEX_DIR):
        print("Loading existing index...")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        index = load_index_from_storage(storage_context)
    else:
        print("Creating new empty index...")
        # Start with empty list, will add documents later
        index = VectorStoreIndex.from_documents([]) 
        index.storage_context.persist(persist_dir=INDEX_DIR)

# Initialize on startup
initialize_index()

class QueryRequest(BaseModel):
    prompt: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global index
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    
    # Save file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process and update index
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    
    if index is None:
        index = VectorStoreIndex.from_documents(documents)
    else:
        # Insert new document into existing index
        for doc in documents:
            index.insert(doc)
    
    # Persist changes
    index.storage_context.persist(persist_dir=INDEX_DIR)
    
    return {"filename": file.filename, "status": "Indexed successfully"}

@app.post("/query")
async def query_index(request: QueryRequest):
    global index
    if index is None:
        raise HTTPException(status_code=400, detail="Index not initialized. Upload a document first.")
    
    query_engine = index.as_query_engine()
    response = query_engine.query(request.prompt)
    return {"response": str(response)}

@app.get("/health")
def health_check():
    return {"status": "running"}
