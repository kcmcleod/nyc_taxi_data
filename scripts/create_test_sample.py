import os
from pathlib import Path

import duckdb as db
from dotenv import load_dotenv

"""
Creates fixtures for dbt testing
"""

if __name__ == "__main__":  # pragma: no cover
    load_dotenv()

    raw_data_path = os.getenv("TAXI_DATA_RAW_PATH")
    if not raw_data_path:
        raise ValueError(
            "TAXI_DATA_RAW_PATH environment variable is not set. Cannot locate parquet files."
        )

    raw_data_dir = Path(raw_data_path)
    project_root = Path(__file__).parents[1]
    output_dir = project_root / "taxi_transforms" / "tests" / "fixtures" / "raw_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    for colour in ["green", "yellow"]:
        all_files = list(raw_data_dir.glob(pattern=f"*{colour}*.parquet"))

        if not all_files:
            print(f"No {colour} parquet files found in {raw_data_dir}. Skipping.")
            continue

        all_files = sorted(all_files, reverse=True)

        file_one = all_files[0]
        print(f"Reading {file_one}...")

        df = db.sql(f"SELECT * FROM read_parquet('{file_one}') LIMIT 25").df()

        sample_df = df.head(n=25)

        output_file = output_dir / f"{colour}_sample.parquet"

        if output_file.exists():
            overwrite_permission = "z"
            while overwrite_permission not in ("y", "Y", "n", "N"):
                overwrite_permission = input("File exists... overwrite? Y / N  ")

            if overwrite_permission in ("n", "N"):
                print(f"Skipping {colour} file")
                continue

        db.sql("SELECT * FROM sample_df").write_parquet(str(output_file))

        print(
            f"Saved {sample_df.shape[0]} rows and {sample_df.shape[1]} columns to {output_file}"
        )
