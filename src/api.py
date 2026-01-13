import os
import shutil
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.node_parser import SentenceSplitter

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

DOCUMENT_COUNT = Gauge(
    "rag_documents_total",
    "Total number of indexed documents"
)

UPLOAD_COUNT = Counter(
    "rag_uploads_total",
    "Total number of document uploads",
    ["status"]
)

QUERY_COUNT = Counter(
    "rag_queries_total",
    "Total number of queries",
    ["status"]
)

EMBEDDING_LATENCY = Histogram(
    "rag_embedding_latency_seconds",
    "Time spent generating embeddings"
)

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Time spent retrieving documents"
)

LLM_LATENCY = Histogram(
    "rag_llm_latency_seconds",
    "Time spent generating LLM response"
)

# --- Setup Global Settings (Same as before) ---
#Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=OLLAMA_URL)
Settings.llm = Ollama(model="gemma3:latest", base_url=OLLAMA_URL, request_timeout=300.0)
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

app = FastAPI(title="Zero-Cost RAG API")

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Prometheus middleware for tracking requests
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    
    method = request.method
    endpoint = request.url.path
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status = response.status_code
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        return response
    except Exception as e:
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        raise

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
    try:
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process and update index with timing
        start_embedding = time.time()
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if index is None:
            index = VectorStoreIndex.from_documents(documents)
        else:
            # Insert new document into existing index
            for doc in documents:
                index.insert(doc)
        
        EMBEDDING_LATENCY.observe(time.time() - start_embedding)
        
        # Persist changes
        index.storage_context.persist(persist_dir=INDEX_DIR)
        
        # Update metrics
        UPLOAD_COUNT.labels(status="success").inc()
        DOCUMENT_COUNT.set(len(index.docstore.docs) if index else 0)
        
        return {"filename": file.filename, "status": "Indexed successfully"}
    except Exception as e:
        UPLOAD_COUNT.labels(status="failure").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_index(request: QueryRequest):
    global index
    try:
        if index is None:
            raise HTTPException(status_code=400, detail="Index not initialized. Upload a document first.")
        
        # Track retrieval time
        start_retrieval = time.time()
        query_engine = index.as_query_engine()
        
        # Track LLM time
        start_llm = time.time()
        response = query_engine.query(request.prompt)
        llm_duration = time.time() - start_llm
        
        retrieval_duration = time.time() - start_retrieval
        
        # Update metrics
        RETRIEVAL_LATENCY.observe(retrieval_duration)
        LLM_LATENCY.observe(llm_duration)
        QUERY_COUNT.labels(status="success").inc()
        
        return {"response": str(response)}
    except HTTPException:
        QUERY_COUNT.labels(status="failure").inc()
        raise
    except Exception as e:
        QUERY_COUNT.labels(status="failure").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "running"}
