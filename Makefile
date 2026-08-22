# ==============================================================================
# Judge Calibration Kit - Workflow Automation Makefile
# ==============================================================================

.PHONY: help setup prepare eval analyze test report clean check-env docker-build docker-run docker-eval docker-analyze docker-shell docker-clean docker-view

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PROMPTFOO := npx promptfoo

help:
	@echo "Judge Calibration Kit - CLI Automation"
	@echo "======================================="
	@echo "make setup       : Create virtualenv and install dependencies"
	@echo "make prepare     : Download & sample 150 ground-truth items from RAGTruth"
	@echo "make eval        : Run Promptfoo judge evaluations (requires API keys)"
	@echo "make analyze     : Compute Cohen's kappa, weighted kappa, and confusion matrices"
	@echo "make run-all     : Execute end-to-end pipeline (prepare -> eval -> analyze)"
	@echo "make clean       : Clean temporary build files, cached results, and virtualenv"
	@echo "make docker-build: Build the Docker image"
	@echo "make docker-run  : Run the full pipeline in Docker (mounts data/, configs/, reports/)"
	@echo "make docker-eval : Run just the Promptfoo eval step in Docker (no analyze step)"
	@echo "make docker-analyze: Run just extract_scores.py + compute_agreement.py in Docker (no eval step)"
	@echo "make docker-shell: Open a shell inside the Docker image for debugging"
	@echo "make docker-clean: Remove Docker containers, image, and volumes for this project"
	@echo "make docker-view : Launch the Promptfoo browser UI at http://localhost:15500"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Checking Node.js & Promptfoo availability..."
	@which npx > /dev/null || (echo "Error: npx/Node.js is required for Promptfoo." && exit 1)
	@echo "Setup complete. Activate environment with: source $(VENV)/bin/activate"

check-env:
	@if [ ! -f .env ]; then \
		echo "Warning: .env file not found. Copying from .env.example..."; \
		cp .env.example .env; \
	fi

prepare: setup
	@echo "Preparing 150-sample evaluation dataset from RAGTruth..."
	$(BIN)/python scripts/prepare_dataset.py

eval: check-env
	@echo "Executing Promptfoo LLM Judge Evaluations..."
	$(PROMPTFOO) eval -c configs/promptfooconfig.yaml -o reports/results.json

analyze:
	@echo "Computing Calibration Metrics & Generating Confusion Matrices..."
	$(PYTHON) scripts/extract_scores.py
	$(PYTHON) scripts/compute_agreement.py

run-all: prepare eval analyze
	@echo "Full calibration pipeline execution complete!"

test:
	$(BIN)/pytest tests/

clean:
	rm -rf $(VENV)
	rm -rf reports/results.json
	rm -rf reports/figures/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker compose build

docker-run: check-env docker-build
	docker compose run --rm eval

docker-eval: check-env docker-build
	docker compose run --rm eval make eval

docker-analyze: check-env docker-build
	docker compose run --rm eval make analyze

docker-shell: check-env docker-build
	docker compose run --rm eval bash

docker-clean:
	docker compose down --rmi local -v

docker-view: check-env docker-build
	docker compose run --rm --service-ports eval npx promptfoo view -n