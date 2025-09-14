.PHONY: help start stop build clean test setup init-submodules

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: init-submodules ## Initial setup (initialize submodules)
	@echo "✅ Setup complete! You can now run 'make start'"

init-submodules: ## Initialize git submodules
	@echo "🔧 Initializing git submodules..."
	git submodule update --init --recursive
	@echo "✅ Submodules initialized"

start: init-submodules ## Start the entire system (CrewAI + Playwright MCP)
	docker-compose up --build

stop: ## Stop all services
	docker-compose down

build: ## Build the Docker images
	docker-compose build

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
