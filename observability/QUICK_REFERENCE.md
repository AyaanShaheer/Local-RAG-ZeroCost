# Quick Reference - Prometheus & Grafana Monitoring

## 🚀 One-Command Deployment

```powershell
.\deploy-monitoring.ps1
```

---

## 🔗 Access URLs

| Service | Port Forward Command | URL | Credentials |
|---------|---------------------|-----|-------------|
| **Prometheus** | `kubectl port-forward svc/prometheus 9090:9090` | http://localhost:9090 | N/A |
| **Grafana** | `kubectl port-forward svc/grafana 3000:3000` | http://localhost:3000 | admin / admin |
| **RAG Backend** | `kubectl port-forward svc/rag-backend 8000:8000` | http://localhost:8000 | N/A |
| **Metrics Endpoint** | `kubectl port-forward svc/rag-backend 8000:8000` | http://localhost:8000/metrics | N/A |

---

## 📊 Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rag_requests_total` | Counter | Total HTTP requests |
| `rag_request_latency_seconds` | Histogram | Request latency |
| `rag_documents_total` | Gauge | Documents in index |
| `rag_uploads_total` | Counter | Document uploads |
| `rag_queries_total` | Counter | RAG queries |
| `rag_embedding_latency_seconds` | Histogram | Embedding time |
| `rag_retrieval_latency_seconds` | Histogram | Retrieval time |
| `rag_llm_latency_seconds` | Histogram | LLM response time |

---

## 🔍 Useful PromQL Queries

```promql
# Request rate (req/sec)
rate(rag_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(rag_request_latency_seconds_bucket[5m]))

# Success rate percentage
sum(rate(rag_queries_total{status="success"}[5m])) / sum(rate(rag_queries_total[5m])) * 100

# Average embedding time
rate(rag_embedding_latency_seconds_sum[5m]) / rate(rag_embedding_latency_seconds_count[5m])

# Total documents
rag_documents_total

# Upload failure rate
rate(rag_uploads_total{status="failure"}[5m])
```

---

## 🧪 Generate Test Data

```bash
# Port-forward first
kubectl port-forward svc/rag-backend 8000:8000

# Upload document
curl -X POST -F "file=@README.md" http://localhost:8000/upload

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test query"}'

# Health check
curl http://localhost:8000/health

# Raw metrics
curl http://localhost:8000/metrics
```

---

## 📈 Import Dashboard

1. Access Grafana: http://localhost:3000
2. Login: `admin` / `admin`
3. Click **+** → **Import**
4. Upload: `observability/rag-dashboard.json`
5. Select data source: **Prometheus**
6. Click **Import**

---

## 🔧 Troubleshooting

### Check Pod Status
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Verify Metrics Endpoint
```bash
kubectl port-forward svc/rag-backend 8000:8000
curl http://localhost:8000/metrics | grep rag_
```

### Check Prometheus Targets
1. Access Prometheus UI
2. Status → Targets
3. Find `rag-backend` job
4. Status should be "UP"

### Grafana No Data
1. Configuration → Data Sources
2. Click Prometheus
3. Test connection
4. Check URL: `http://prometheus:9090`

---

## 📁 File Structure

```
Local-RAG-ZeroCost/
├── src/
│   └── api.py                          # ✨ Instrumented with metrics
├── k8s/
│   ├── prometheus-deployment.yaml      # 🆕 Prometheus setup
│   ├── grafana-deployment.yaml         # 🆕 Grafana setup
│   ├── backend-deployment.yaml         # ✏️ Updated to v2
│   └── rag-backend-service.yaml        # ✏️ Added annotations
├── observability/
│   ├── rag-dashboard.json              # 🆕 Grafana dashboard
│   ├── servicemonitor.yaml             # Existing
│   └── MONITORING.md                   # 🆕 Full guide
└── deploy-monitoring.ps1               # 🆕 Deployment script
```

Legend: 🆕 New | ✏️ Modified | ✨ Enhanced

---

## ⚡ Key Commands

```bash
# Deploy everything
.\deploy-monitoring.ps1

# Check status
kubectl get pods
kubectl get svc

# Restart deployments
kubectl rollout restart deployment/prometheus
kubectl rollout restart deployment/grafana
kubectl rollout restart deployment/rag-backend

# Delete everything
kubectl delete -f k8s/prometheus-deployment.yaml
kubectl delete -f k8s/grafana-deployment.yaml

# View logs
kubectl logs -l app=prometheus -f
kubectl logs -l app=grafana -f
kubectl logs -l app=rag-backend -f
```

---

## 📚 Documentation

- **Full Guide**: `observability/MONITORING.md`
- **Walkthrough**: See artifacts directory
- **Implementation Plan**: See artifacts directory

---

## 🎯 Next Steps

1. Run `.\deploy-monitoring.ps1`
2. Access Grafana and import dashboard
3. Generate test traffic
4. Watch metrics update in real-time!

---

For detailed information, see [MONITORING.md](file:///d:/Local-RAG-ZeroCost/observability/MONITORING.md)
