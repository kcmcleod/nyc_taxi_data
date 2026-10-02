from pathlib import Path
from unittest.mock import patch

from nyc_taxi_data import process_data


@patch("pathlib.Path.exists")
def test_get_parquet_files_missing(mock_exists):
    mock_exists.return_value = False
    result = process_data.get_parquet_files(Path("/Users/banana"))
    assert result == []


@patch("pathlib.Path.exists")
@patch("pathlib.Path.is_dir")
def test_get_parquet_files_file(mock_dir, mock_exists):
    mock_exists.return_value = True
    mock_dir.return_value = False
    result = process_data.get_parquet_files(Path("/Users/banana"))
    assert result == []


@patch("pathlib.Path.glob")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_get_parquet_files_works(mock_exists, mock_is_dir, mock_glob):
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    expected_files = [Path("file1"), Path("file2"), Path("file3")]
    mock_glob.return_value = expected_files

    result = process_data.get_parquet_files(Path("/Users/banana"))

    assert result == expected_files
