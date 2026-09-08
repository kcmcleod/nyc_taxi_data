import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_parquet_files(directory: Path) -> list[Path]:
    """
    Scans the target directory and returns a list of all .parquet files.

    Args:
        directory (Path): Location to look for files.

    Returns:
        List of Path objects each of whih is a file to process
    """
    if not directory.exists():
        logger.error(f"Fail: No such directory {directory}")
        return []

    if not directory.is_dir():
        logger.error(f"Fail: Not a directory {directory}")
        return []

    all_files = directory.glob(pattern="*.parquet")

    return all_files


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    get_parquet_files(Path("/Users/kcm/data/nyc_taxi/"))
