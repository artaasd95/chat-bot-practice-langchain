# Deployment Documentation

This document provides comprehensive deployment instructions for the LangGraph Chat Bot System across different environments.

## Overview

The Chat Bot System supports multiple deployment strategies:

- **Development**: Local development with Docker Compose
- **Staging**: Docker Compose with production-like configuration
- **Production**: Kubernetes cluster deployment
- **Cloud**: AWS/GCP/Azure deployment options

## Prerequisites

### System Requirements

- **CPU**: Minimum 4 cores (8 cores recommended for production)
- **Memory**: Minimum 8GB RAM (16GB recommended for production)
- **Storage**: Minimum 50GB SSD (100GB+ recommended for production)
- **Network**: Stable internet connection for LLM API calls

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for production)
- kubectl (for Kubernetes deployment)
- Helm 3.0+ (optional, for Kubernetes)

## Environment Configuration

### Environment Variables

Create environment files for different deployment stages:

#### Development (.env.dev)

```bash
# API Configuration
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=Chat Bot System - Development
VERSION=1.0.0

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database Configuration
DATABASE_URL=postgresql://chatbot_user:chatbot_password@postgres:5432/chatbot_db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_DB=0

# Authentication
SECRET_KEY=your-secret-key-for-development
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-3.5-turbo
LLM_FALLBACK_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.7
LLM_CACHE_TTL=1800

# Logging
LOG_LEVEL=DEBUG

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
```

#### Production (.env.prod)

```bash
# API Configuration
DEBUG=false
API_V1_STR=/api/v1
PROJECT_NAME=Chat Bot System
VERSION=1.0.0

# CORS Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://chatbot_user:secure_password@postgres:5432/chatbot_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=secure_redis_password
REDIS_DB=0

# Authentication
SECRET_KEY=your-very-secure-secret-key-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# LLM Configuration
OPENAI_API_KEY=your-production-openai-api-key
LLM_MODEL=gpt-4
LLM_FALLBACK_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.7
LLM_CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Webhook Configuration
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT=30
```

## Development Deployment

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd chat-bot-practice-langchain
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**:
   ```bash
   make dev-up
   # or
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Initialize database**:
   ```bash
   make db-migrate
   # or
   docker-compose exec chat-service alembic upgrade head
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Auth API: http://localhost:8001/docs
   - Chat API: http://localhost:8002/docs
   - Admin API: http://localhost:8003/docs

### Development Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chatbot_db
      POSTGRES_USER: chatbot_user
      POSTGRES_PASSWORD: chatbot_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chatbot_user -d chatbot_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  auth-service:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: uvicorn app.auth_main:app --host 0.0.0.0 --port 8001 --reload
    ports:
      - "8001:8001"
    volumes:
      - ./app:/app/app
    env_file:
      - .env.dev
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  chat-service:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
    ports:
      - "8002:8002"
    volumes:
      - ./app:/app/app
    env_file:
      - .env.dev
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  admin-service:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: uvicorn app.admin_main:app --host 0.0.0.0 --port 8003 --reload
    ports:
      - "8003:8003"
    volumes:
      - ./app:/app/app
    env_file:
      - .env.dev
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - VITE_API_BASE_URL=http://localhost:8080
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.dev.conf:/etc/nginx/nginx.conf
    depends_on:
      - auth-service
      - chat-service
      - admin-service

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: chatbot_dev_network
```

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Production Deployment

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  auth-service:
    image: chatbot/auth-service:${VERSION}
    command: gunicorn app.auth_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
    env_file:
      - .env.prod
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  chat-service:
    image: chatbot/chat-service:${VERSION}
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002
    env_file:
      - .env.prod
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'

  admin-service:
    image: chatbot/admin-service:${VERSION}
    command: gunicorn app.admin_main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8003
    env_file:
      - .env.prod
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  frontend:
    image: chatbot/frontend:${VERSION}
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - auth-service
      - chat-service
      - admin-service
      - frontend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: chatbot_prod_network
```

### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Add local packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

## Kubernetes Deployment

### Namespace Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: chatbot-system
  labels:
    name: chatbot-system
    environment: production
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chatbot-config
  namespace: chatbot-system
data:
  API_V1_STR: "/api/v1"
  PROJECT_NAME: "Chat Bot System"
  VERSION: "1.0.0"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  DATABASE_POOL_SIZE: "20"
  DATABASE_MAX_OVERFLOW: "30"
  DATABASE_POOL_TIMEOUT: "30"
  REDIS_DB: "0"
  ACCESS_TOKEN_EXPIRE_MINUTES: "30"
  REFRESH_TOKEN_EXPIRE_DAYS: "7"
  ALGORITHM: "HS256"
  LLM_MODEL: "gpt-4"
  LLM_FALLBACK_MODEL: "gpt-3.5-turbo"
  LLM_MAX_TOKENS: "2048"
  LLM_TEMPERATURE: "0.7"
  LLM_CACHE_TTL: "3600"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_WINDOW: "60"
  WEBHOOK_TIMEOUT: "30"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
  namespace: chatbot-system
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  REDIS_PASSWORD: <base64-encoded-redis-password>
  SECRET_KEY: <base64-encoded-secret-key>
  OPENAI_API_KEY: <base64-encoded-openai-api-key>
  WEBHOOK_SECRET: <base64-encoded-webhook-secret>
```

### PostgreSQL Deployment

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: chatbot-system
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: chatbot_db
        - name: POSTGRES_USER
          value: chatbot_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - chatbot_user
            - -d
            - chatbot_db
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - chatbot_user
            - -d
            - chatbot_db
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: chatbot-system
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

### Redis Deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: chatbot-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --requirepass
        - $(REDIS_PASSWORD)
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: REDIS_PASSWORD
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - -a
            - $(REDIS_PASSWORD)
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - -a
            - $(REDIS_PASSWORD)
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: chatbot-system
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### Chat Service Deployment

```yaml
# k8s/chat-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-service
  namespace: chatbot-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chat-service
  template:
    metadata:
      labels:
        app: chat-service
    spec:
      containers:
      - name: chat-service
        image: chatbot/chat-service:1.0.0
        command:
        - gunicorn
        - app.main:app
        - -w
        - "4"
        - -k
        - uvicorn.workers.UvicornWorker
        - -b
        - 0.0.0.0:8002
        ports:
        - containerPort: 8002
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: REDIS_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: OPENAI_API_KEY
        envFrom:
        - configMapRef:
            name: chatbot-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: chat-service
  namespace: chatbot-system
spec:
  selector:
    app: chat-service
  ports:
  - port: 8002
    targetPort: 8002
  type: ClusterIP
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chatbot-ingress
  namespace: chatbot-system
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: chatbot-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /api/v1/auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8001
      - path: /api/v1/chat
        pathType: Prefix
        backend:
          service:
            name: chat-service
            port:
              number: 8002
      - path: /api/v1/admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 8003
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chat-service-hpa
  namespace: chatbot-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chat-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# k8s/monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: chatbot-system
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "chatbot_rules.yml"
    
    scrape_configs:
      - job_name: 'chatbot-services'
        static_configs:
          - targets: ['auth-service:8001', 'chat-service:8002', 'admin-service:8003']
        metrics_path: '/metrics'
        scrape_interval: 30s
      
      - job_name: 'postgres'
        static_configs:
          - targets: ['postgres:5432']
        metrics_path: '/metrics'
        scrape_interval: 30s
      
      - job_name: 'redis'
        static_configs:
          - targets: ['redis:6379']
        metrics_path: '/metrics'
        scrape_interval: 30s
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
  
  chatbot_rules.yml: |
    groups:
      - name: chatbot.rules
        rules:
          - alert: HighErrorRate
            expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: High error rate detected
              description: "Error rate is {{ $value }} errors per second"
          
          - alert: HighResponseTime
            expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: High response time detected
              description: "95th percentile response time is {{ $value }} seconds"
          
          - alert: DatabaseConnectionsHigh
            expr: pg_stat_activity_count > 80
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: High database connections
              description: "Database has {{ $value }} active connections"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "Chat Bot System Dashboard",
    "tags": ["chatbot"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}} - {{method}} {{status}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "id": 4,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "Active Connections"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Chat Bot System

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    strategy:
      matrix:
        service: [auth-service, chat-service, admin-service, frontend]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.24.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to Kubernetes
      run: |
        export KUBECONFIG=kubeconfig
        kubectl apply -f k8s/
        kubectl rollout restart deployment/auth-service -n chatbot-system
        kubectl rollout restart deployment/chat-service -n chatbot-system
        kubectl rollout restart deployment/admin-service -n chatbot-system
        kubectl rollout restart deployment/frontend -n chatbot-system
    
    - name: Verify deployment
      run: |
        export KUBECONFIG=kubeconfig
        kubectl rollout status deployment/auth-service -n chatbot-system
        kubectl rollout status deployment/chat-service -n chatbot-system
        kubectl rollout status deployment/admin-service -n chatbot-system
        kubectl rollout status deployment/frontend -n chatbot-system
```

## Security Considerations

### SSL/TLS Configuration

1. **Certificate Management**:
   - Use Let's Encrypt for automatic certificate renewal
   - Implement cert-manager in Kubernetes
   - Configure proper SSL/TLS termination

2. **Security Headers**:
   ```nginx
   add_header X-Frame-Options DENY;
   add_header X-Content-Type-Options nosniff;
   add_header X-XSS-Protection "1; mode=block";
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
   ```

3. **Network Security**:
   - Use network policies in Kubernetes
   - Implement proper firewall rules
   - Restrict database access to application services only

### Secrets Management

1. **Kubernetes Secrets**:
   - Use sealed-secrets or external-secrets operator
   - Rotate secrets regularly
   - Implement proper RBAC

2. **Environment Variables**:
   - Never commit secrets to version control
   - Use secret management tools (HashiCorp Vault, AWS Secrets Manager)
   - Implement secret rotation

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup-db.sh

BACKUP_DIR="/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="chatbot_db_backup_${DATE}.sql"

# Create backup
pg_dump -h postgres -U chatbot_user -d chatbot_db > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to cloud storage (optional)
# aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://your-backup-bucket/

# Clean up old backups (keep last 7 days)
find ${BACKUP_DIR} -name "chatbot_db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Disaster Recovery

1. **Recovery Procedures**:
   - Document step-by-step recovery process
   - Test recovery procedures regularly
   - Maintain offsite backups

2. **Monitoring and Alerting**:
   - Set up alerts for service failures
   - Monitor backup completion
   - Implement health checks

## Performance Optimization

### Database Optimization

1. **Connection Pooling**:
   - Configure appropriate pool sizes
   - Monitor connection usage
   - Implement connection timeouts

2. **Query Optimization**:
   - Add database indexes
   - Monitor slow queries
   - Implement query caching

### Application Optimization

1. **Caching Strategy**:
   - Implement Redis caching
   - Cache LLM responses
   - Use CDN for static assets

2. **Load Balancing**:
   - Configure proper load balancing
   - Implement health checks
   - Use session affinity when needed

## Troubleshooting

### Common Issues

1. **Service Not Starting**:
   ```bash
   # Check logs
   kubectl logs -f deployment/chat-service -n chatbot-system
   
   # Check events
   kubectl get events -n chatbot-system
   
   # Check pod status
   kubectl get pods -n chatbot-system
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connectivity
   kubectl exec -it deployment/chat-service -n chatbot-system -- \
     psql -h postgres -U chatbot_user -d chatbot_db -c "SELECT 1;"
   ```

3. **High Memory Usage**:
   ```bash
   # Check resource usage
   kubectl top pods -n chatbot-system
   
   # Check resource limits
   kubectl describe pod <pod-name> -n chatbot-system
   ```

### Debugging Commands

```bash
# View all resources
kubectl get all -n chatbot-system

# Check service endpoints
kubectl get endpoints -n chatbot-system

# View ingress status
kubectl get ingress -n chatbot-system

# Check persistent volumes
kubectl get pv,pvc -n chatbot-system

# View secrets
kubectl get secrets -n chatbot-system
```

This deployment documentation provides comprehensive guidance for deploying the Chat Bot System across different environments with proper security, monitoring, and maintenance procedures.