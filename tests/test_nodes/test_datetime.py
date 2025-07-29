import pytest

import pandas as pd
import datetime as dt

from retrack.nodes.datetime import CurrentYear, DaysBetweenDates, CurrentTime


@pytest.fixture
def current_year_input_data():
    return {
        "id": 18,
        "data": {},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "CurrentYear",
    }


def test_current_year_node(current_year_input_data):
    current_year_node = CurrentYear(**current_year_input_data)

    assert isinstance(current_year_node, CurrentYear)


def test_current_year_node_run(current_year_input_data, mocker):
    datetime_mock = mocker.patch("retrack.nodes.datetime.dt.datetime")
    datetime_mock.now.return_value = mocker.MagicMock(year=2021)
    current_year_node = CurrentYear(**current_year_input_data)
    output = current_year_node.run()
    assert output["output_value"] == 2021


@pytest.fixture
def days_between_dates_input_data():
    return {
        "id": 9,
        "data": {},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [1597.1904571362154, 628.6495284260166],
        "name": "DaysBetweenDates",
    }


def test_days_between_dates_node(days_between_dates_input_data):
    days_between_dates_node = DaysBetweenDates(**days_between_dates_input_data)

    assert isinstance(days_between_dates_node, DaysBetweenDates)

    assert days_between_dates_node.model_dump(by_alias=True) == {
        "id": "9",
        "name": "DaysBetweenDates",
        "data": {"format": "%Y-%m-%d", "timezone": "America/Sao_Paulo"},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


def test_days_between_dates_node_run(days_between_dates_input_data, mocker):
    days_between_dates_node = DaysBetweenDates(**days_between_dates_input_data)
    timestamp_now = pd.Timestamp("2025-07-01").normalize()

    class TimestampMock(pd.Timestamp):
        @classmethod
        def now(cls, tz=None):
            return timestamp_now

    output = days_between_dates_node.run(
        pd.Series(["2025-07-01"]), pd.Series(["2025-01-01"])
    )
    assert (output["output_value"] == pd.Series([181])).all()
    mocker.patch("retrack.nodes.datetime.pd.Timestamp", TimestampMock)
    output = days_between_dates_node.run(pd.Series(["2025-07-01"]), pd.Series([None]))
    assert (output["output_value"] == pd.Series([0])).all()
    output = days_between_dates_node.run(pd.Series(["2025-01-01"]), pd.Series([None]))
    assert (output["output_value"] == pd.Series([181])).all()
    output = days_between_dates_node.run(pd.Series(["2024-12-31"]), pd.Series([None]))
    assert (output["output_value"] == pd.Series([182])).all()
    output = days_between_dates_node.run(
        pd.Series([dt.datetime.strptime("2024-12-31", "%Y-%m-%d")]), pd.Series([None])
    )
    assert (output["output_value"] == pd.Series([182])).all()


@pytest.fixture
def current_time_input_data():
    return {
        "id": 19,
        "data": {},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "CurrentTime",
    }


def test_current_time_node(current_time_input_data):
    current_time_node = CurrentTime(**current_time_input_data)

    assert isinstance(current_time_node, CurrentTime)

    assert current_time_node.model_dump(by_alias=True) == {
        "id": "19",
        "name": "CurrentTime",
        "data": {"format": None, "timezone": "America/Sao_Paulo"},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


def test_current_time_node_run(current_time_input_data, mocker):
    current_time_node = CurrentTime(**current_time_input_data)
    datetime_now = dt.datetime.strptime("2025-07-01", "%Y-%m-%d")

    class DateTimeMock(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime_now

    mocker.patch("retrack.nodes.datetime.dt.datetime", DateTimeMock)

    output = current_time_node.run()
    assert output["output_value"] == datetime_now.isoformat()

    current_time_input_data["data"] = {
        "format": "%Y-%m-%d",
        "timezone": "America/Sao_Paulo",
    }
    current_time_node = CurrentTime(**current_time_input_data)
    output = current_time_node.run()
    assert output["output_value"] == "2025-07-01"

    current_time_input_data["data"] = {
        "format": "%Y-%d-%m",
        "timezone": "America/Sao_Paulo",
    }
    current_time_node = CurrentTime(**current_time_input_data)
    output = current_time_node.run()
    assert output["output_value"] == "2025-01-07"
