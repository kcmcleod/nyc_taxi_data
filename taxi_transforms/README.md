# 🚖 NYC Taxi Data Pipeline: dbt & DuckDB

**Status:** 🚧 *Active Development - Staging (Silver) Layer in Progress*

## 1. Project Overview & Architecture
This project is an end-to-end, locally executed ELT pipeline designed to ingest, clean, and model raw New York City TLC Taxi data (Yellow and Green cabs) into a reliable dimensional model for downstream analytics.

Rather than relying on cloud infrastructure, this pipeline leverages **DuckDB** as a highly performant, local in-process OLAP database, orchestrated by **dbt (Data Build Tool)** to execute SQL transformations.

**Architecture Strategy (Medallion):**
*   **Bronze (Raw):** Direct ingestion of TLC Parquet files into DuckDB external tables.
*   **Silver (Staging):** Cleansing, standardising, and type-casting the raw data.
*   **Gold (Core):** Dimensional modelling (Facts & Dimensions) for reporting.

## 2. Current Development Status
This repository is currently in active development, mirroring Agile software delivery phases. 
*   ✅ **Bronze Layer (Ingestion):** Complete. Raw Parquet files for Yellow and Green taxis are successfully mapped into DuckDB.
*   🚧 **Silver Layer (Staging):** Currently engineering the staging models (`stg_nyc_taxi__yellow`, `stg_nyc_taxi__green`). Current focus areas include:
    *   Standardising column names and resolving schema disparities (e.g., Parquet type inference quirks) between Yellow and Green datasets.
    *   Handling real-world temporal anomalies by filtering 0-second trips and selectively nullifying negative-duration timestamps to protect downstream time-series metrics.
    *   Implementing `dbt seeds` to map TLC Location IDs to explicit borough and zone names, with strict primary key testing.

## 3. Engineering & Testing Standards
Coming from a Lead Data Science Engineer background, this project applies strict software engineering principles to the modern data stack:
*   **Test-Driven Data (TDD):** Leveraging dbt's native testing capabilities, alongside custom-authored macros, to enforce data quality contracts before models are built—applying the same rigour used in traditional software unit testing (e.g., R's `testthat`).
*   **Modular SQL:** Following strict DRY principles by separating base staging logic from downstream aggregations.
*   **Version Control:** Atomic, descriptive Git commits ensuring a clean, traceable project history.

## 4. Roadmap & Next Steps
*   **Gold Layer (Dimensional Modelling):** Build the final fact table (`fact_trips`) and denormalised views to prepare the data for downstream consumption.
*   **Dashboard Integration:** Connect the final DuckDB core model to an interactive dashboard application to render spatial heatmaps of pickup and dropoff locations.
*   **Advanced Data Quality:** Implement `dbt-expectations` for more complex anomaly detection.
*   **Orchestration:** Containerise the environment and orchestrate the dbt execution schedules using **Apache Airflow**.
*   **Documentation:** Auto-generate and host the dbt documentation site.