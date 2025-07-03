# Chat Bot Microservices Architecture

This document describes the containerized microservices architecture for the FastAPI chat bot application.

## Architecture Overview

The application is split into three independent microservices:

1. **Auth Service** (`auth:8001`) - User authentication and authorization
2. **Chat Service** (`chat:8002`) - Chat functionality and LangChain integration
3. **Admin Service** (`admin:8003`) - Administrative panel and user management
4. **API Gateway** (`nginx:80`) - Request routing and load balancing
5. **Database** (`postgres:5432`) - Shared PostgreSQL database
6. **Cache** (`redis:6379`) - Redis for caching and session management

## Services Description

### Auth Service
- **Port**: 8001
- **Responsibilities**:
  - User registration and login
  - JWT token management
  - Password operations
  - User profile management
- **Endpoints**: `/api/v1/auth/*`
- **Database**: Initializes tables and creates admin user

### Chat Service
- **Port**: 8002
- **Responsibilities**:
  - Chat message processing
  - LangChain integration
  - Webhook handling
  - AI response generation
- **Endpoints**: `/api/v1/chat/*`, `/webhook/*`
- **Dependencies**: Requires auth service for user validation

### Admin Service
- **Port**: 8003
- **Responsibilities**:
  - User management
  - System statistics
  - Administrative operations
  - Chat history management
- **Endpoints**: `/api/v1/admin/*`
- **Dependencies**: Requires auth service for admin validation

### API Gateway (Nginx)
- **Port**: 80
- **Responsibilities**:
  - Request routing
  - Load balancing
  - Rate limiting
  - CORS handling
  - Security headers

## Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available
- Ports 80, 5432, 6379, 8001-8003 available

### Environment Setup

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Update the `.env` file with your configuration:
```env
# Database
DATABASE_URL=postgresql+asyncpg://chatbot:password@postgres:5432/chatbot_db

# Authentication
SECRET_KEY=your-super-secret-key-here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# LangChain/OpenAI
OPENAI_API_KEY=your-openai-api-key
LANGCHAIN_API_KEY=your-langchain-api-key

# Redis
REDIS_URL=redis://redis:6379/0
```

### Running the Application

1. Build and start all services:
```bash
docker-compose up --build
```

2. For production deployment:
```bash
docker-compose -f docker-compose.yml up -d
```

3. Check service health:
```bash
# Overall health
curl http://localhost/health

# Individual service health
curl http://localhost/auth/health
curl http://localhost/chat/health
curl http://localhost/admin/health
```

## API Documentation

Once running, access the API documentation:

- **Auth Service**: http://localhost/api/v1/auth/docs
- **Chat Service**: http://localhost/api/v1/chat/docs
- **Admin Service**: http://localhost/api/v1/admin/docs
- **API Gateway Info**: http://localhost/

## Service Communication

### Inter-Service Authentication
Services communicate using internal network calls with JWT tokens:

```python
# Example: Chat service validating user
headers = {"Authorization": f"Bearer {token}"}
response = await httpx.get("http://auth:8001/api/v1/auth/me", headers=headers)
```

### Database Access
All services share the same PostgreSQL database but only the Auth service initializes tables and creates the admin user.

### Caching
Redis is available for all services for caching and session management.

## Scaling

### Horizontal Scaling
Scale individual services based on load:

```bash
# Scale chat service to 3 instances
docker-compose up --scale chat=3

# Scale auth service to 2 instances
docker-compose up --scale auth=2
```

### Load Balancing
Nginx automatically load balances between multiple instances of the same service.

### Resource Allocation
Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  chat:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Monitoring and Logging

### Health Checks
All services include health check endpoints:
- Individual: `/{service}/health`
- Gateway: `/health`

### Logs
View service logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth
docker-compose logs -f chat
docker-compose logs -f admin
```

### Monitoring
The system includes comprehensive monitoring tools:

#### Metrics Collection
- **Prometheus**: Collects and stores metrics from all services
  - LLM usage metrics (requests, latency, tokens)
  - API metrics (requests, latency, status codes)
  - Graph execution metrics (node execution times, success rates)
  - System metrics (active users, conversations)

#### Visualization
- **Grafana**: Provides dashboards for monitoring system performance
  - LLM Monitoring Dashboard: Shows LLM usage, latency, and error rates
  - API Dashboard: Tracks API performance and usage patterns
  - System Dashboard: Monitors overall system health

#### LangSmith Integration
- **LangSmith**: Provides comprehensive tracing, monitoring, and evaluation for LangChain and LangGraph components
  - **Tracing Implementation**:
    - Automatically traces all LLM calls via the `track_llm_usage` decorator
    - Captures all LangGraph node executions with the `track_graph_node` decorator
    - Records inputs, outputs, and execution times for each component
    - Maintains parent-child relationships between graph nodes and LLM calls
  
  - **Monitoring Capabilities**:
    - Real-time dashboards showing LLM usage patterns and performance
    - Token usage tracking by model and request type
    - Cost analysis tools to optimize LLM spending
    - Performance metrics for each graph node and LLM call
    - Anomaly detection for identifying unusual patterns
  
  - **Debugging Features**:
    - Interactive visualization of LangGraph execution paths
    - Detailed inspection of state at each node in the graph
    - Error tracing with full context of failures
    - Comparison tools to identify differences between runs
    - Replay functionality to reproduce issues
  
  - **Evaluation Tools**:
    - A/B testing framework for comparing different models and prompts
    - Custom evaluation metrics for assessing response quality
    - Automated testing against ground truth datasets
    - User feedback integration for continuous improvement
    - Historical performance tracking over time

## Security

### Network Security
- Services communicate over internal Docker network
- Only API Gateway exposes external ports
- Database and Redis are not externally accessible

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Admin-only endpoints protected

### Rate Limiting
Nginx implements rate limiting:
- Auth endpoints: 10 requests/minute
- API endpoints: 100 requests/minute

## Development

### Local Development
For development with hot reload:

```bash
# Start only database and redis
docker-compose up postgres redis

# Run services locally
uvicorn app.auth_main:app --host 0.0.0.0 --port 8001 --reload
uvicorn app.chat_main:app --host 0.0.0.0 --port 8002 --reload
uvicorn app.admin_main:app --host 0.0.0.0 --port 8003 --reload
```

### Testing
Run tests for each service:

```bash
# Test auth service
docker-compose exec auth pytest app/tests/

# Test chat service
docker-compose exec chat pytest app/tests/

# Test admin service
docker-compose exec admin pytest app/tests/
```

## Deployment

### Production Deployment

1. **Environment Variables**: Use Docker secrets or external secret management
2. **SSL/TLS**: Configure SSL certificates in Nginx
3. **Database**: Use managed PostgreSQL service
4. **Monitoring**: Add health checks and monitoring
5. **Backup**: Implement database backup strategy

### Docker Swarm
For Docker Swarm deployment:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml chatbot
```

### Kubernetes
For Kubernetes deployment, convert docker-compose to k8s manifests:

```bash
# Using kompose
kompose convert
kubectl apply -f .
```

## Troubleshooting

### Common Issues

1. **Service won't start**:
   ```bash
   docker-compose logs [service-name]
   ```

2. **Database connection issues**:
   - Check if PostgreSQL is running
   - Verify DATABASE_URL in environment
   - Check network connectivity

3. **Authentication failures**:
   - Verify SECRET_KEY is set
   - Check JWT token expiration
   - Ensure admin user was created

4. **Chat service issues**:
   - Verify OpenAI API key
   - Check LangChain configuration
   - Monitor resource usage

### Performance Tuning

1. **Database**:
   - Tune PostgreSQL configuration
   - Add database indexes
   - Use connection pooling

2. **Redis**:
   - Configure memory limits
   - Set appropriate eviction policies
   - Monitor memory usage

3. **Application**:
   - Tune worker processes
   - Optimize database queries
   - Implement caching strategies

## Migration from Monolith

If migrating from the original monolithic application:

1. **Database**: No changes needed, same schema
2. **Environment**: Update URLs to point to services
3. **Client Applications**: Update API endpoints to use gateway
4. **Authentication**: Tokens remain compatible

## Support

For issues and questions:
1. Check service logs
2. Verify environment configuration
3. Test individual service health
4. Review this documentation

---

**Note**: This microservices architecture provides better scalability, maintainability, and deployment flexibility compared to the monolithic approach.