# Prometheus & Grafana Monitoring Setup Guide

This guide walks you through deploying and using Prometheus and Grafana to monitor your RAG application.

## Prerequisites

- Kubernetes cluster running (Minikube, Docker Desktop, or any K8s cluster)
- kubectl configured to connect to your cluster
- Docker for building images

## Quick Start

### 1. Build and Deploy the Updated Application

First, rebuild your Docker image with the updated metrics instrumentation:

```bash
# Navigate to your project directory
cd d:\Local-RAG-ZeroCost

# Build the updated Docker image
docker build -f docker/Dockerfile.api -t rag-backend:v2 .

# If using Minikube, load the image into Minikube
minikube image load rag-backend:v2
```

### 2. Update the Backend Deployment

Update `k8s/backend-deployment.yaml` to use the new image version (change `v1` to `v2`):

```yaml
image: rag-backend:v2
```

### 3. Deploy All Kubernetes Resources

```bash
# Deploy Prometheus
kubectl apply -f k8s/prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana-deployment.yaml

# Deploy/update the backend service
kubectl apply -f k8s/rag-backend-service.yaml
kubectl apply -f k8s/backend-deployment.yaml

# Optional: Deploy ServiceMonitor (if using Prometheus Operator)
kubectl apply -f observability/servicemonitor.yaml
```

### 4. Verify Deployments

```bash
# Check all pods are running
kubectl get pods

# You should see:
# - rag-backend-* (your application)
# - prometheus-*
# - grafana-*
```

### 5. Access Prometheus UI

```bash
# Port-forward to Prometheus
kubectl port-forward svc/prometheus 9090:9090
```

Open your browser to [http://localhost:9090](http://localhost:9090)

**Verify metrics are being scraped:**
1. Go to Status → Targets
2. Look for the `rag-backend` job
3. Ensure the state is "UP"

**Test some queries:**
- `rag_requests_total` - Total request count
- `rate(rag_requests_total[5m])` - Request rate per second
- `rag_documents_total` - Number of indexed documents
- `histogram_quantile(0.95, rate(rag_request_latency_seconds_bucket[5m]))` - 95th percentile latency

### 6. Access Grafana UI

```bash
# Port-forward to Grafana
kubectl port-forward svc/grafana 3000:3000
```

Open your browser to [http://localhost:3000](http://localhost:3000)

**Login credentials:**
- Username: `admin`
- Password: `admin`

### 7. Import the Dashboard

1. In Grafana, click the "+" icon → Import
2. Click "Upload JSON file"
3. Select `observability/rag-dashboard.json`
4. Click "Load"
5. Select "Prometheus" as the data source
6. Click "Import"

You should now see the RAG Application Metrics dashboard with all panels!

## Dashboard Panels Explained

### Overview Panels
- **Request Rate**: Shows requests per second across all endpoints
- **Request Latency**: P50, P95, P99 latency percentiles
- **Total Documents Indexed**: Current count of documents in the index
- **Total Uploads**: Cumulative upload count
- **Total Queries**: Cumulative query count
- **Query Success Rate**: Percentage of successful queries

### RAG-Specific Panels
- **Embedding Latency**: Time spent generating embeddings during upload
- **Retrieval Latency**: Time spent retrieving relevant documents
- **LLM Response Latency**: Time spent generating LLM responses
- **Upload Success vs Failure Rate**: Track upload reliability
- **Query Success vs Failure Rate**: Track query reliability

## Generate Test Data

To see metrics in action, generate some load:

```bash
# Port-forward to the backend
kubectl port-forward svc/rag-backend 8000:8000

# Upload a test document
curl -X POST -F "file=@README.md" http://localhost:8000/upload

# Run some queries
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is this project about?"}'

# Check health endpoint
curl http://localhost:8000/health

# View raw metrics
curl http://localhost:8000/metrics
```

After generating some traffic, refresh your Grafana dashboard to see the metrics update!

## Troubleshooting

### Prometheus not scraping metrics

1. Check if the rag-backend service is exposing the metrics endpoint:
   ```bash
   kubectl port-forward svc/rag-backend 8000:8000
   curl http://localhost:8000/metrics
   ```

2. Check Prometheus logs:
   ```bash
   kubectl logs -l app=prometheus
   ```

3. Verify the service annotations:
   ```bash
   kubectl get svc rag-backend -o yaml
   ```

### Grafana showing "No Data"

1. Verify Prometheus data source is configured:
   - Go to Configuration → Data Sources
   - Ensure Prometheus is listed and URL is `http://prometheus:9090`

2. Test the data source connection

3. Check if Prometheus has data:
   - Go to Prometheus UI
   - Run queries manually

### Pods not starting

```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

## Customizing the Dashboard

You can edit the dashboard in Grafana:

1. Click the dashboard settings (gear icon)
2. Click "JSON Model" to see/edit the raw JSON
3. Add new panels by clicking "Add Panel"
4. Save the dashboard
5. Export it back to JSON for version control

## Production Considerations

For production deployments, consider:

1. **Persistent Storage**: Replace `emptyDir` with PersistentVolumeClaims
2. **Security**: Change default Grafana password
3. **High Availability**: Run multiple Prometheus/Grafana replicas
4. **Alerts**: Configure Alertmanager for critical metrics
5. **Data Retention**: Configure Prometheus retention policies
6. **Authentication**: Set up proper authentication for Grafana
7. **HTTPS**: Use TLS for all services

## Available Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `rag_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `rag_request_latency_seconds` | Histogram | HTTP request latency by method, endpoint |
| `rag_documents_total` | Gauge | Number of documents in the index |
| `rag_uploads_total` | Counter | Total document uploads by status |
| `rag_queries_total` | Counter | Total queries by status |
| `rag_embedding_latency_seconds` | Histogram | Embedding generation time |
| `rag_retrieval_latency_seconds` | Histogram | Document retrieval time |
| `rag_llm_latency_seconds` | Histogram | LLM response generation time |

## Next Steps

- Set up alerting rules in Prometheus
- Create additional dashboards for specific use cases
- Integrate with external monitoring systems (DataDog, New Relic, etc.)
- Add custom business metrics to track application-specific KPIs
