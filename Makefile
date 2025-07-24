# ImmoAssist Makefile
# Development and deployment automation

.PHONY: help install install-dev run test lint format clean docker-build docker-run deploy

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
POETRY := poetry
PROJECT_NAME := immoassist
PORT ?= 8000

help: ## Show this help message
	@echo "ImmoAssist Development Commands"
	@echo "=============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(POETRY) install --no-dev

install-dev: ## Install all dependencies including dev
	$(POETRY) install

run: ## Run the ImmoAssist agent locally
	$(POETRY) run python run_agent.py

run-adk: ## Run with ADK CLI
	$(POETRY) run adk run app

test: ## Run tests
	$(POETRY) run pytest

test-coverage: ## Run tests with coverage report
	$(POETRY) run pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linting checks
	$(POETRY) run flake8 app/
	$(POETRY) run mypy app/

format: ## Format code with black and isort
	$(POETRY) run black app/ tests/
	$(POETRY) run isort app/ tests/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

docker-build: ## Build Docker image
	docker build -t $(PROJECT_NAME):latest .

docker-run: ## Run Docker container locally
	docker run -p $(PORT):$(PORT) \
		--env-file .env \
		-e PORT=$(PORT) \
		$(PROJECT_NAME):latest

deploy-cloud-run: ## Deploy to Google Cloud Run
	gcloud run deploy $(PROJECT_NAME) \
		--source . \
		--region europe-west3 \
		--platform managed \
		--allow-unauthenticated \
		--set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_LOCATION=europe-west3"

setup-gcloud: ## Setup Google Cloud SDK
	gcloud auth login
	gcloud config set project $(GOOGLE_CLOUD_PROJECT)
	gcloud services enable aiplatform.googleapis.com
	gcloud services enable cloudbuild.googleapis.com
	gcloud services enable run.googleapis.com

create-service-account: ## Create service account for local development
	gcloud iam service-accounts create immoassist-dev \
		--display-name="ImmoAssist Development Account"
	gcloud projects add-iam-policy-binding $(GOOGLE_CLOUD_PROJECT) \
		--member="serviceAccount:immoassist-dev@$(GOOGLE_CLOUD_PROJECT).iam.gserviceaccount.com" \
		--role="roles/aiplatform.user"
	gcloud iam service-accounts keys create credentials.json \
		--iam-account=immoassist-dev@$(GOOGLE_CLOUD_PROJECT).iam.gserviceaccount.com

env-from-example: ## Create .env from .env.example
	cp .env.example .env
	@echo "Created .env file. Please update it with your values."

check-env: ## Check if required environment variables are set
	@echo "Checking environment variables..."
	@test -n "$(GOOGLE_CLOUD_PROJECT)" || (echo "ERROR: GOOGLE_CLOUD_PROJECT not set" && exit 1)
	@test -n "$(MODEL_NAME)" || (echo "ERROR: MODEL_NAME not set" && exit 1)
	@test -n "$(SPECIALIST_MODEL)" || (echo "ERROR: SPECIALIST_MODEL not set" && exit 1)
	@test -n "$(CHAT_MODEL)" || (echo "ERROR: CHAT_MODEL not set" && exit 1)
	@echo "All required environment variables are set."

update-deps: ## Update dependencies
	$(POETRY) update

lock-deps: ## Lock dependencies
	$(POETRY) lock --no-update

export-requirements: ## Export requirements.txt from poetry
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

init-pre-commit: ## Initialize pre-commit hooks
	$(POETRY) run pre-commit install 