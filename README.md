# 🚀 DevOps FastAPI Project

A complete DevOps learning project featuring a **TODO List REST API** built with **FastAPI**, demonstrating CI/CD, Docker, Kubernetes, and monitoring concepts.

---

## 📁 Project Structure

```
devops-fastapi-project/
├── src/
│   ├── main.py              # FastAPI application (TODO List API)
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       ├── __init__.py
│       └── test_main.py     # Unit tests
├── .github/
│   └── workflows/
│       ├── dev.yml          # CI/CD pipeline for dev branch
│       └── main.yml         # CI/CD pipeline for main branch
├── k8s/
│   ├── deployment.yaml      # Kubernetes deployment (2 replicas)
│   ├── service.yaml         # Kubernetes NodePort service (port 30000)
│   └── configmap.yaml       # Kubernetes configuration
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Local development with Docker
├── sonar-project.properties # SonarCloud code quality configuration
└── README.md               # This file
```

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check (used by Kubernetes) |
| GET | `/metrics` | Application metrics |
| GET | `/todos` | List all TODOs |
| POST | `/todos` | Create a new TODO |
| GET | `/todos/{id}` | Get a specific TODO |
| PUT | `/todos/{id}` | Update a TODO |
| DELETE | `/todos/{id}` | Delete a TODO |
| PUT | `/todos/{id}/complete` | Mark TODO as completed |

---

## 📅 Day-by-Day Setup Guide

### Day 1: Run the Application Locally

**Prerequisites:**
- Python 3.11+
- Git

**Steps:**

```bash
# 1. Clone the repository
git clone https://github.com/mohamedkhemaissia/devops-fastapi-project.git
cd devops-fastapi-project

# 2. Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. Run the application
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Test it:**
- Open your browser: http://localhost:8000/docs (Swagger UI)
- Or use curl:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn DevOps"}'
curl http://localhost:8000/todos
```

**Run tests:**
```bash
cd src
pytest tests/ -v
```

---

### Day 2: Docker

**Prerequisites:**
- Docker installed (`sudo apt install docker.io`)

**Build and run with Docker:**

```bash
# Build the Docker image
docker build -t todo-api .

# Run the container
docker run -p 8000:8000 todo-api

# Access: http://localhost:8000/docs
```

**Run with Docker Compose (easier for development):**

```bash
# Start (with auto-reload)
docker-compose up

# Start in background
docker-compose up -d

# Stop
docker-compose down

# Rebuild if you changed code
docker-compose up --build
```

**Useful Docker commands:**
```bash
# List running containers
docker ps

# See container logs
docker logs todo-api

# Stop a container
docker stop todo-api

# List images
docker images
```

---

### Day 3: GitHub Actions CI/CD

The project has two pipelines:

**`.github/workflows/dev.yml`** - Runs on push to `dev` branch:
1. ✅ Run tests
2. ✅ SonarCloud code quality scan
3. ✅ Build Docker image
4. ✅ Push to GitHub Container Registry with `dev` tag

**`.github/workflows/main.yml`** - Runs on push to `main` branch:
1. ✅ Run tests
2. ✅ SonarCloud code quality scan
3. ✅ Build Docker image
4. ✅ Push to GitHub Container Registry with `latest` tag

**Setup SonarCloud:**
1. Go to https://sonarcloud.io
2. Sign in with GitHub
3. Create a new project linked to this repo
4. Get your `SONAR_TOKEN`
5. Go to GitHub → Settings → Secrets → Add `SONAR_TOKEN`

**Test the pipeline:**
```bash
git checkout -b dev
git push origin dev
# Watch the pipeline run at: https://github.com/mohamedkhemaissia/devops-fastapi-project/actions
```

---

### Day 4: Kubernetes

**Prerequisites:**
- kubectl installed
- A Kubernetes cluster (minikube, kind, or cloud)

**Install Kind (local Kubernetes):**
```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create a cluster
kind create cluster --name devops-cluster

# Verify
kubectl cluster-info
```

**Deploy the application:**
```bash
# Apply all Kubernetes files
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=todo-api
```

**Access the application:**
```bash
# With minikube
minikube service todo-api-service --url

# With kind, port-forward
kubectl port-forward service/todo-api-service 8000:80

# Access: http://localhost:8000/docs
```

**Useful kubectl commands:**
```bash
# Scale up/down
kubectl scale deployment todo-api-deployment --replicas=3

# Rolling update (no downtime!)
kubectl set image deployment/todo-api-deployment todo-api=<new-image>

# Rollback
kubectl rollout undo deployment/todo-api-deployment

# Delete all resources
kubectl delete -f k8s/
```

---

## 🔍 Understanding Key Concepts

### Health Checks (Kubernetes Probes)

The deployment has two health checks:

- **Liveness Probe** (`/health`): "Is the app alive?" → If this fails, Kubernetes **restarts** the pod
- **Readiness Probe** (`/health`): "Is the app ready?" → If this fails, Kubernetes **stops sending traffic** to this pod

### Resource Limits

```yaml
resources:
  requests:   # Minimum guaranteed resources
    memory: "64Mi"
    cpu: "50m"
  limits:     # Maximum allowed resources
    memory: "256Mi"
    cpu: "200m"
```

### Rolling Update Strategy

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Add 1 extra pod during update
    maxUnavailable: 0  # Never take a pod down before a new one is up
```
This means **zero downtime deployments**!

---

## ❓ Common Interview Questions

**Q: What is CI/CD?**
> CI (Continuous Integration) = automatically test and build code on every push.
> CD (Continuous Deployment) = automatically deploy to production after tests pass.

**Q: Why use Docker?**
> Docker packages the application with all its dependencies, so "it works on my machine" also works everywhere else.

**Q: What is the difference between liveness and readiness probes?**
> Liveness = "Is the app alive?" (restart if dead). Readiness = "Is the app ready to handle requests?" (remove from load balancer if not ready).

**Q: Why 2 replicas in Kubernetes?**
> High availability. If one pod crashes or is being updated, the other one keeps serving traffic.

**Q: What is a ConfigMap?**
> A Kubernetes object to store configuration as key-value pairs, separate from the application code. This follows the 12-factor app principle of separating config from code.

---

## 🔧 Development

```bash
# Run tests
cd src && pytest tests/ -v

# Check a specific test
pytest tests/test_main.py::test_health_check -v

# Run with coverage (install pytest-cov first)
pytest tests/ -v --cov=.
```
