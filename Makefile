.PHONY: help start stop build clean test setup init-submodules

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: init-submodules build ## Complete initial setup (submodules + build)
	@echo "✅ Setup complete! You can now run 'make start' or 'make chat'"

init-submodules: ## Initialize git submodules
	@echo "🔧 Initializing git submodules..."
	git submodule update --init --recursive
	@echo "✅ Submodules initialized"

build: init-submodules ## Build all Docker images (one-time setup)
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache
	@echo "✅ Build complete! Now you can use 'make start-chat' for daily usage"

start: ## Start services in background (requires 'make build' first)
	docker-compose up -d
	@echo "🚀 Services started! Use 'make chat' to open chat interface"

chat: ## Open chat interface (requires services running - use 'make start' first)
	docker-compose exec crewai-app python main.py

start-chat: ## Build + Start + Chat (complete workflow - use this for daily usage)
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo "💬 Opening chat interface..."
	docker-compose exec crewai-app python main.py

quick-chat: ## Start services + chat (fast - requires 'make build' first)
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	docker-compose exec crewai-app python main.py

stop: ## Stop all services
	docker-compose down

clean: ## Clean up Docker containers and images
	docker-compose down --rmi all --volumes --remove-orphans

test: ## Run tests
	docker-compose exec crewai-app python -m pytest tests/

lint: ## Run linting and formatting
	uv run pre-commit run --all-files

lint-fix: ## Run linting and auto-fix issues
	uv run pre-commit run --all-files --hook-stage manual

dev: ## Start in development mode with live reload
	docker-compose up --build crewai-app

logs: ## Show logs from all services
	docker-compose logs -f
