.PHONY: help build up down logs clean test rebuild restart shell

# Colors for output
BLUE := \033[0;36m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help:
	@echo "$(BLUE)Facebook-Plus Docker Commands$(NC)"
	@echo "$(GREEN)Production:$(NC)"
	@echo "  make build          - Build Docker image"
	@echo "  make up             - Start production containers"
	@echo "  make down           - Stop containers"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-app       - View app logs only"
	@echo "  make restart        - Restart containers"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev-up         - Start dev environment"
	@echo "  make dev-down       - Stop dev environment"
	@echo "  make dev-logs       - View dev logs"
	@echo "  make shell          - Enter app shell"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  make clean          - Remove containers and images"
	@echo "  make rebuild        - Rebuild without cache"
	@echo "  make prune          - Clean up unused Docker resources"
	@echo "  make test           - Run tests"
	@echo "  make status         - Show container status"
	@echo ""

# Production Commands
build:
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker-compose build

up:
	@echo "$(BLUE)Starting production environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "  App: http://localhost:8000"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana: http://localhost:3000"

down:
	@echo "$(BLUE)Stopping containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f facebook-system

status:
	@docker-compose ps

restart:
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

# Development Commands
dev-up:
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Dev services started$(NC)"
	@echo "  App: http://localhost:8000"
	@echo "  Postgres: localhost:5432"
	@echo "  Redis: localhost:6379"

dev-down:
	@echo "$(BLUE)Stopping dev environment...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Dev environment stopped$(NC)"

dev-logs:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

shell:
	@docker-compose exec facebook-system bash

# Testing
test:
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec facebook-system python -m pytest tests/ -v

# Maintenance Commands
rebuild:
	@echo "$(BLUE)Rebuilding without cache...$(NC)"
	docker-compose build --no-cache

clean:
	@echo "$(RED)Removing containers, images, and volumes...$(NC)"
	docker-compose down -v
	docker image rm facebook-plus:latest 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

prune:
	@echo "$(BLUE)Pruning unused Docker resources...$(NC)"
	docker system prune -af --volumes
	@echo "$(GREEN)✓ Prune complete$(NC)"

# Monitoring
metrics:
	@echo "$(BLUE)Prometheus metrics:$(NC)"
	docker-compose exec facebook-system curl http://localhost:8000/metrics 2>/dev/null || echo "Metrics endpoint not available"

stats:
	@echo "$(BLUE)Container resource usage:$(NC)"
	docker-compose stats

# Development helpers
run-module:
	@read -p "Enter module number (1-11): " module; \
	docker-compose exec facebook-system python "$${module}_*.py"

install-deps:
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	docker-compose exec facebook-system pip install -r requirements.txt

lint:
	@echo "$(BLUE)Linting code...$(NC)"
	docker-compose exec facebook-system python -m flake8 . --max-line-length=120 || true

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	docker-compose exec facebook-system python -m black . || true

# Database commands (if using postgres in dev)
db-shell:
	docker-compose exec postgres psql -U facebook_user -d facebook_db

db-backup:
	@mkdir -p backups
	@docker-compose exec postgres pg_dump -U facebook_user facebook_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up$(NC)"

# Production deployment
push-image:
	@read -p "Enter registry (e.g., docker.io/username): " registry; \
	docker tag facebook-plus:latest $$registry/facebook-plus:latest; \
	docker push $$registry/facebook-plus:latest; \
	echo "$(GREEN)✓ Image pushed to $$registry$(NC)"

.PHONY: all $(MAKECMDGOALS)
