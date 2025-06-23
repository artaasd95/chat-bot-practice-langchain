# Makefile for Chat Bot Microservices

.PHONY: help build up down logs clean dev prod test backup restore

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build all Docker images"
	@echo "  up         - Start all services (development)"
	@echo "  down       - Stop all services"
	@echo "  logs       - Show logs from all services"
	@echo "  clean      - Clean up containers, networks, and volumes"
	@echo "  dev        - Start development environment with hot reload"
	@echo "  prod       - Start production environment"
	@echo "  test       - Run tests in all services"
	@echo "  backup     - Create database backup"
	@echo "  restore    - Restore database from backup"
	@echo "  shell-auth - Open shell in auth service"
	@echo "  shell-chat - Open shell in chat service"
	@echo "  shell-admin - Open shell in admin service"
	@echo "  shell-db   - Open PostgreSQL shell"
	@echo "  health     - Check health of all services"

# Build all images
build:
	docker-compose build

# Start development environment
up:
	docker-compose up

# Start development environment in background
up-d:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Show logs for specific service
logs-auth:
	docker-compose logs -f auth

logs-chat:
	docker-compose logs -f chat

logs-admin:
	docker-compose logs -f admin

logs-nginx:
	docker-compose logs -f nginx

# Clean up everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

# Development environment with hot reload
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-d:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production environment
prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Stop production
prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Run tests
test:
	docker-compose exec auth pytest app/tests/ -v || true
	docker-compose exec chat pytest app/tests/ -v || true
	docker-compose exec admin pytest app/tests/ -v || true

# Test specific service
test-auth:
	docker-compose exec auth pytest app/tests/ -v

test-chat:
	docker-compose exec chat pytest app/tests/ -v

test-admin:
	docker-compose exec admin pytest app/tests/ -v

# Database operations
backup:
	docker-compose exec postgres pg_dump -U chatbot chatbot_db > backup_$$(date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Usage: make restore FILE=backup_file.sql"
	@if [ -z "$(FILE)" ]; then echo "Please specify FILE=backup_file.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U chatbot chatbot_db < $(FILE)

# Shell access
shell-auth:
	docker-compose exec auth /bin/bash

shell-chat:
	docker-compose exec chat /bin/bash

shell-admin:
	docker-compose exec admin /bin/bash

shell-db:
	docker-compose exec postgres psql -U chatbot chatbot_db

shell-redis:
	docker-compose exec redis redis-cli

# Health checks
health:
	@echo "Checking service health..."
	@curl -s http://localhost/health || echo "Gateway: FAILED"
	@curl -s http://localhost/auth/health || echo "Auth: FAILED"
	@curl -s http://localhost/chat/health || echo "Chat: FAILED"
	@curl -s http://localhost/admin/health || echo "Admin: FAILED"

# Service management
restart-auth:
	docker-compose restart auth

restart-chat:
	docker-compose restart chat

restart-admin:
	docker-compose restart admin

restart-nginx:
	docker-compose restart nginx

# Scale services
scale-chat:
	@echo "Usage: make scale-chat REPLICAS=3"
	@if [ -z "$(REPLICAS)" ]; then echo "Please specify REPLICAS=number"; exit 1; fi
	docker-compose up --scale chat=$(REPLICAS) -d

scale-auth:
	@echo "Usage: make scale-auth REPLICAS=2"
	@if [ -z "$(REPLICAS)" ]; then echo "Please specify REPLICAS=number"; exit 1; fi
	docker-compose up --scale auth=$(REPLICAS) -d

# Monitoring
stats:
	docker stats

ps:
	docker-compose ps

# Update and rebuild
update:
	docker-compose pull
	docker-compose build --no-cache
	docker-compose up -d

# Initialize fresh environment
init:
	make clean
	make build
	make up-d
	@echo "Waiting for services to start..."
	sleep 30
	make health

# Quick development setup
quick-dev:
	cp .env.example .env
	@echo "Please update .env file with your configuration"
	@echo "Then run: make dev"

# Production deployment
deploy:
	@echo "Deploying to production..."
	make prod-down
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
	make prod-build
	@echo "Waiting for services to start..."
	sleep 60
	make health
	@echo "Production deployment complete!"