debug:
	uv run --env-file .env dbt debug --project-dir taxi_transforms --profiles-dir taxi_transforms
test:
	uv run pytest
coverage:
	uv run pytest --cov=nyc_taxi_data --cov-report=term-missing