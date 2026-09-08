import datetime
import logging
import os
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def read_config():
    """
    Returns config values. Assumes saved in 'config.toml' at top level.

    Returns:
        dict: config params

    Raises:
        FileNotFoundError: If 'config.toml' is missing from the project root.
        tomllib.TOMLDecodeError: If the config file contains invalid TOML syntax.
    """
    env_root = os.getenv("PROJECT_ROOT")

    if env_root:
        project_root = Path(env_root)
    else:
        logger.warning(
            "PROJECT_ROOT environment variable missing. Falling back to relative pathing."
        )
        project_root = Path(__file__).parents[2]

    config_path = project_root / "config.toml"

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        logger.error(f"Cannot proceed: The file {config_path} is missing.")
        raise
    except tomllib.TOMLDecodeError as e:
        logger.error(f"The file is corrupt or invalid TOML. Details: {e}")
        raise
    except Exception:
        logger.exception("An unexpected error occurred")
        raise
    logger.info(f"Config read from {config_path}")
    return config


def get_file_date(
    num_months_to_go_back: int = 4, reference_date: datetime.date | None = None
):
    """
    Get month and year of files to download.

    By default 4 months before today.
    So if today is September 2026, the date returned will be 2026-05-01

    If 'reference_date' specified it will be 4 months before that.

    Args:
        num_months_to_go_back (int): number of months to go back. If the value
            is 4 and today is the 2026-09-07, then 2026-05-01 will be returned.
        reference_date (datetime.date, optional): Baseline to calculate date from.
            Defaults to today.
    Returns:
        datetime.date: The exact date to get the files for. Will always be the 1st
            of the selected month-year.
    """

    if reference_date is None:
        uk_tz = ZoneInfo("Europe/London")
        reference_date = datetime.datetime.now(tz=uk_tz).date()

    start_of_month = reference_date.replace(day=1)
    target_date = start_of_month - relativedelta(months=num_months_to_go_back)

    logger.info(f"Target date for file download is {target_date}")

    return target_date


def download_file(url: str, raw_data_dir: Path) -> tuple[str, Path | None]:
    """
    Downloads file at given url, if it exists.

    Args:
        url (str): The URL is file is to be downloaded from

    Returns:
        boolean: Tuple
    """
    file_name = url.split("/")[-1]
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    file_path = raw_data_dir / file_name

    if file_path.is_file():
        logger.info(f"Skipped: we already have the file {file_name}")
        return "skipped", file_path

    try:
        response = requests.get(url, stream=True, timeout=10)
        status_code = response.status_code
        if status_code == 403:
            logger.warning(f"Sorry! File isn't available at {url}")
            return "failed", None
        elif status_code == 200:
            with open(file_path, mode="wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
        else:
            logger.error(
                f"Sorry! Can't handle this error code: {status_code} for {file_name}"
            )
            return "failed", None
    except requests.exceptions.ReadTimeout as e:
        logger.error(f"Time Out Error: {e}")
        return "failed", None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
        return "failed", None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {e}")
        return "failed", None
    except FileNotFoundError:
        logger.error(f"Cannot write the file: {file_name}")
        return "failed", None
    except Exception:
        logger.exception("An unexpected error occurred")
        return "failed", None

    logger.info(f"File saved to {file_path}")
    return "success", file_path


def monthly_run(execution_date: datetime.date | None = None) -> None:
    """
    Main function to trigger download of all relevant files each month.

    Args:
        execution_date (datetime.date, optional) Can specify a starting date that
        is not the start of today's month. Useful for Airflow & failed jobs

    """
    target_date = get_file_date(reference_date=execution_date)

    # throws error if failure - will be caught by Airflow
    config = read_config()

    raw_data_dir = Path(config["downloads"]["raw_folder"])

    template_url = config["downloads"]["url_template"]

    urls = [
        template_url.format(
            type="yellow", year=target_date.year, month=target_date.strftime("%m")
        ),
        template_url.format(
            type="green", year=target_date.year, month=target_date.strftime("%m")
        ),
    ]

    results = []
    valid_paths = []
    for url in urls:
        # silent failures
        status, saved_path = download_file(url, raw_data_dir)
        results.append(status)

        if status in ("success", "skipped"):
            valid_paths.append(saved_path)

    logger.info(
        f"Download process finished! {results.count('success')} files were downloaded. {results.count('skipped')} were skipped. "
        + f"{results.count('failed')} were NOT downloaded due to an error."
    )


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    monthly_run()
