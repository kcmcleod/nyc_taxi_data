import datetime
import os
import tomllib
from pathlib import Path
from unittest.mock import ANY, call, mock_open, patch
from zoneinfo import ZoneInfo

import pytest
import requests
from dateutil.relativedelta import relativedelta

from nyc_taxi_data import download_data


def test_get_file_date_default():
    uk_tz = ZoneInfo("Europe/London")
    today = datetime.datetime.now(tz=uk_tz).date()
    today = today.replace(day=1)
    default_date = download_data.get_file_date()
    new_date = default_date + relativedelta(months=4)
    assert today == new_date


def test_get_file_date_date_specified():
    start = datetime.date(2026, 1, 12)
    result = download_data.get_file_date(reference_date=start)

    assert result == datetime.date(2025, 9, 1)


def test_get_file_date_date_and_months_specified():
    start = datetime.date(2026, 1, 12)
    result = download_data.get_file_date(reference_date=start, num_months_to_go_back=1)

    assert result == datetime.date(2025, 12, 1)


###########################################################################################


def test_read_config_default():
    config = download_data.read_config()
    assert config.__class__ is dict


def test_read_config_missing():
    project_root = Path(__file__).parents[3]
    config_path = project_root / "config.toml"
    config_path_moved = project_root / "config.toml_bk"

    os.rename(config_path, config_path_moved)

    try:
        with pytest.raises(FileNotFoundError):
            download_data.read_config()

    finally:
        os.rename(config_path_moved, config_path)


def test_read_config_corrupt():
    project_root = Path(__file__).parents[3]
    config_path = project_root / "config.toml"
    config_path_moved = project_root / "config.toml_bk"
    os.rename(config_path, config_path_moved)

    try:
        with open(config_path, mode="w") as file:
            file.writelines("bananananananan")

        with pytest.raises(tomllib.TOMLDecodeError):
            download_data.read_config()

    finally:
        os.rename(config_path_moved, config_path)


@patch("tomllib.load")
def test_read_config_exception(mock_open):
    error_message = "A totally unexpected system error"
    mock_open.side_effect = Exception("A totally unexpected system error")

    with pytest.raises(Exception, match=error_message):
        download_data.read_config()


##########################################################################################


@patch("pathlib.Path.is_file")
@patch("pathlib.Path.mkdir")
def test_download_file_mock_skipped(mock_mkdir, mock_is_file):
    mock_is_file.return_value = True

    result = download_data.download_file("https://none.com/banana")
    assert result == "skipped"

    mock_mkdir.assert_called_once()
    mock_is_file.assert_called_once()


@patch("requests.get")
def test_download_file_mock_request_403(mock_get):

    mock_get.return_value.status_code = 403
    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


@patch("requests.get")
def test_download_file_mock_request_503(mock_get):

    mock_get.return_value.status_code = 503
    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.mkdir")
@patch("requests.get")
def test_download_file_mock_request_200(mock_get, mock_mkdir, mock_file):

    mock_get.return_value.status_code = 200
    mock_get.return_value.iter_content.return_value = [b"fake_data_chunk"]
    result = download_data.download_file("https://none.com/banana")
    assert result == "success"

    mock_file.assert_called_once_with(ANY, mode="wb")
    mock_file().writelines.assert_called_once_with([b"fake_data_chunk"])


@patch("requests.get")
def test_download_file_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.ReadTimeout("Server took too long")

    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


@patch("requests.get")
def test_download_file_connection(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


@patch("requests.get")
def test_download_file_request(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Request error")

    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


@patch("builtins.open")
@patch("requests.get")
def test_download_file_fnf(mock_get, mock_open):
    mock_get.return_value.status_code = 200
    mock_get.return_value.iter_content.return_value = [b"fake_data_chunk"]

    mock_open.side_effect = FileNotFoundError

    result = download_data.download_file("https://none.com/banana")

    assert result == "failed"


########################################################################################


@patch("nyc_taxi_data.download_data.download_file")
@patch("nyc_taxi_data.download_data.read_config")
@patch("nyc_taxi_data.download_data.get_file_date")
def test_monthly_run(mock_get_file_date, mock_read_config, mock_download_file):
    uk_tz = ZoneInfo("Europe/London")
    mock_get_file_date.return_value = datetime.datetime(2020, 5, 17, tzinfo=uk_tz)

    mock_read_config.return_value = {
        "downloads": {"url_template": "https://fake.com/{type}_{year}_{month}.parquet"}
    }

    mock_download_file.return_value = False

    download_data.monthly_run()

    assert mock_download_file.call_count == 2

    expected_calls = [
        call("https://fake.com/yellow_2020_05.parquet"),
        call("https://fake.com/green_2020_05.parquet"),
    ]
    mock_download_file.assert_has_calls(expected_calls)
