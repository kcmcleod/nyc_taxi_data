.PHONY: debug test coverage db_run db_test db_docs help

debug: ## run dbt debug
	uv run --env-file .env dbt debug --project-dir taxi_transforms --profiles-dir taxi_transforms

test: ## run python tests
	uv run pytest src/ dashboard/

coverage: ## run python coverage
	uv run pytest src/ dashboard/ --cov=nyc_taxi_data --cov-report=term-missing

db_run: ## build dbt models
	uv run --env-file .env dbt run --project-dir taxi_transforms --profiles-dir taxi_transforms

db_test: ## run dbt tests
	uv run --env-file .env dbt test --project-dir taxi_transforms --profiles-dir taxi_transforms

db_seed: ## create dbt seeds
	uv run --env-file .env dbt seed --project-dir taxi_transforms --profiles-dir taxi_transforms

db_docs: ## build then run dbt docs
	uv run --env-file .env dbt docs generate --project-dir taxi_transforms --profiles-dir taxi_transforms
	uv run --env-file .env dbt docs serve --project-dir taxi_transforms --profiles-dir taxi_transforms

help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)