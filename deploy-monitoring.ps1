# Deploy Monitoring Stack Script
# This script deploys Prometheus and Grafana to your Kubernetes cluster

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Deploying Monitoring Stack" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build Docker image
Write-Host "Step 1: Building Docker image with metrics..." -ForegroundColor Yellow
docker build -f docker/Dockerfile.api -t rag-backend:v2 .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Failed to build Docker image" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Load image into Minikube (if using Minikube)
Write-Host "Step 2: Loading image into Minikube..." -ForegroundColor Yellow
$context = kubectl config current-context
if ($context -like "*minikube*") {
    minikube image load rag-backend:v2
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Warning: Failed to load image into Minikube" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Image loaded into Minikube" -ForegroundColor Green
    }
} else {
    Write-Host "[i] Not using Minikube, skipping image load" -ForegroundColor Cyan
}
Write-Host ""

# Step 3: Deploy Prometheus
Write-Host "Step 3: Deploying Prometheus..." -ForegroundColor Yellow
kubectl apply -f k8s/prometheus-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Failed to deploy Prometheus" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Prometheus deployed" -ForegroundColor Green
Write-Host ""

# Step 4: Deploy Grafana
Write-Host "Step 4: Deploying Grafana..." -ForegroundColor Yellow
kubectl apply -f k8s/grafana-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Failed to deploy Grafana" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Grafana deployed" -ForegroundColor Green
Write-Host ""

# Step 5: Update backend service and deployment
Write-Host "Step 5: Updating RAG backend..." -ForegroundColor Yellow
kubectl apply -f k8s/rag-backend-service.yaml
kubectl apply -f k8s/backend-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Failed to update backend" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Backend updated" -ForegroundColor Green
Write-Host ""

# Step 6: Wait for pods to be ready
Write-Host "Step 6: Waiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "Waiting for Prometheus..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=120s
Write-Host "Waiting for Grafana..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=grafana --timeout=120s
Write-Host "Waiting for RAG backend..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=rag-backend --timeout=120s
Write-Host "[OK] All pods ready" -ForegroundColor Green
Write-Host ""

# Step 7: Display pod status
Write-Host "Step 7: Pod Status" -ForegroundColor Yellow
kubectl get pods -o wide
Write-Host ""

# Step 8: Display access instructions
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Prometheus UI:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/prometheus 9090:9090" -ForegroundColor White
Write-Host "  Then open: http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "Access Grafana UI:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/grafana 3000:3000" -ForegroundColor White
Write-Host "  Then open: http://localhost:3000" -ForegroundColor White
Write-Host "  Login: admin / admin" -ForegroundColor White
Write-Host ""
Write-Host "Access RAG Backend:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/rag-backend 8000:8000" -ForegroundColor White
Write-Host "  Metrics: http://localhost:8000/metrics" -ForegroundColor White
Write-Host ""
Write-Host "Import Dashboard:" -ForegroundColor Yellow
Write-Host "  File: observability/rag-dashboard.json" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see: observability/MONITORING.md" -ForegroundColor Cyan
