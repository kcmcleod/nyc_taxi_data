.PHONY: debug test coverage db_run db_test db_docs

debug:
	uv run --env-file .env dbt debug --project-dir taxi_transforms --profiles-dir taxi_transforms
test:
	uv run pytest
coverage:
	uv run pytest --cov=nyc_taxi_data --cov-report=term-missing

db_run:
	uv run --env-file .env dbt run --project-dir taxi_transforms --profiles-dir taxi_transforms

db_test:
	uv run --env-file .env dbt test --project-dir taxi_transforms --profiles-dir taxi_transforms

db_seed:
	uv run --env-file .env dbt seed --project-dir taxi_transforms --profiles-dir taxi_transforms

db_docs:
	uv run --env-file .env dbt docs generate --project-dir taxi_transforms --profiles-dir taxi_transforms
	uv run --env-file .env dbt docs serve --project-dir taxi_transforms --profiles-dir taxi_transforms
