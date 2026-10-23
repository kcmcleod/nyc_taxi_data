# use env or fallback
-include .env

export DBT_TARGET ?= demo
export DBT_DUCKDB_PATH ?= $(CURDIR)/data/taxi_data.duckdb
export OBT_TABLE_NAME ?= obt_nyc_taxi__trips
export TAXI_DATA_RAW_PATH ?= $(CURDIR)/taxi_transforms/tests/fixtures/raw_data

.PHONY: help demo quickstart ingest debug test coverage db_run db_test db_docs db_deps db_view app code_tree


##@ Onboarding & Quickstart

demo: ## Quick build & launch using committed sample fixtures (zero download)
	@echo "Building demo warehouse from committed sample fixtures..."
	@mkdir -p data
	DBT_TARGET=demo \
	DBT_DUCKDB_PATH=$(CURDIR)/data/demo_taxi.duckdb \
	TAXI_DATA_RAW_PATH=$(CURDIR)/taxi_transforms/tests/fixtures/raw_data \
	uv run dbt deps --project-dir taxi_transforms --profiles-dir taxi_transforms
	DBT_TARGET=demo \
	DBT_DUCKDB_PATH=$(CURDIR)/data/demo_taxi.duckdb \
	TAXI_DATA_RAW_PATH=$(CURDIR)/taxi_transforms/tests/fixtures/raw_data \
	uv run dbt build --project-dir taxi_transforms --profiles-dir taxi_transforms
	DBT_DUCKDB_PATH=$(CURDIR)/data/demo_taxi.duckdb \
	OBT_TABLE_NAME=obt_nyc_taxi__trips \
	uv run streamlit run dashboard/app.py

# ingest: ## Download 1 month of real NYC TLC Parquet files into TAXI_DATA_RAW_PATH
# 	@mkdir -p $(TAXI_DATA_RAW_PATH)
# 	uv run python -m nyc_taxi_data.download_data

# quickstart: ingest db_deps db_build app ## E2E pipeline: download 1 month of data, build dbt, and launch app

##@ Testing & Quality

debug: ## run dbt debug
	uv run  dbt debug --project-dir taxi_transforms --profiles-dir taxi_transforms

test: ## run python tests
	uv run pytest src/ dashboard/

coverage: ## run python coverage
	uv run pytest src/ dashboard/ --cov=nyc_taxi_data --cov=dashboard --cov-report=term-missing

db_run: ## build dbt models
	uv run  dbt run --project-dir taxi_transforms --profiles-dir taxi_transforms

db_test: ## run dbt tests
	uv run  dbt test --project-dir taxi_transforms --profiles-dir taxi_transforms

db_seed: ## create dbt seeds
	uv run  dbt seed --project-dir taxi_transforms --profiles-dir taxi_transforms

db_build: ## Run seeds, models, and tests in DAG order
	uv run dbt build --project-dir taxi_transforms --profiles-dir taxi_transforms

db_docs: ## build then run dbt docs
	uv run  dbt docs generate --project-dir taxi_transforms --profiles-dir taxi_transforms
	uv run  dbt docs serve --project-dir taxi_transforms --profiles-dir taxi_transforms

db_deps: ## install dbt dependencies
	uv run  dbt deps --project-dir taxi_transforms --profiles-dir taxi_transforms

db_view: ## connect to db in terminal
	harlequin --read-only data/taxi_data.duckdb

app: ## run the streamlit dashboard locally
	streamlit run dashboard/app.py 

code_tree: ## code files as a directory tree
	tree -I ".git|__pycache__|.venv|venv|node_modules|.pytest_cache|dbt_packages|logs|target|.ruff_cache|.pytest_cache" | pbcopy

help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
