from prometheus_client import Counter, Histogram

# Request-level metrics
REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total number of RAG queries",
    ["endpoint"]
)

REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds",
    "Latency of RAG queries",
    ["endpoint"]
)

# RAG-specific metrics
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
