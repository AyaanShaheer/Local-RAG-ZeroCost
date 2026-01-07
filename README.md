# Zero-Cost Local RAG Assistant

End-to-end Retrieval-Augmented Generation (RAG) system with full DevOps pipeline, deployed on Kubernetes with production monitoring.

## 🎯 Features

- **Local LLM Inference**: Ollama (Llama3/Gemma) - no API costs
- **Vector Search**: ChromaDB for semantic document retrieval
- **Microservices**: FastAPI backend + Streamlit frontend
- **Containerized**: Docker images for all components
- **Orchestration**: Kubernetes (Minikube) deployment
- **Observability**: Prometheus metrics + Grafana dashboards
- **Zero Cost**: Runs entirely on local infrastructure

## 🏗️ Architecture

<img width="2816" height="1536" alt="Gemini_Generated_Image_ykl61tykl61tykl6" src="https://github.com/user-attachments/assets/051c009f-03c1-4fac-8bab-c764514e0ed5" />


## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Minikube
- Ollama
- Python 3.10+

### Installation

1. Clone the repository
```bash
git clone https://github.com/AyaanShaheer/Local-RAG-ZeroCost.git
cd Local-RAG-ZeroCost
```

2. Install Ollama models
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

3. Start Minikube
```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube docker-env | Invoke-Expression
```

4. Build and deploy
```bash
docker build -t rag-backend:v1 -f docker/Dockerfile.api .
docker build -t rag-frontend:v1 -f docker/Dockerfile.ui .
kubectl apply -f k8s/
minikube tunnel
```

5. Access at `http://localhost:8502`

## 📊 Monitoring

Access Grafana dashboards:
```bash
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Default credentials: `admin` / (get password from secret)

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LlamaIndex
- **Frontend**: Streamlit
- **LLM**: Ollama (Llama3, Gemma)
- **Vector DB**: ChromaDB
- **Containers**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Monitoring**: Prometheus, Grafana

## 📝 Project Structure

```
.
├── src/
│   ├── api.py              # FastAPI backend
│   ├── ui.py               # Streamlit frontend
│   └── test_rag.py         # RAG pipeline test
├── docker/
│   ├── Dockerfile.api      # Backend container
│   └── Dockerfile.ui       # Frontend container
├── k8s/
│   ├── backend-deployment.yaml
│   └── frontend-deployment.yaml
└── requirements.txt
```

## 📄 License

MIT License
