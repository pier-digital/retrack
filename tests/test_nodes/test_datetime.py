import pytest
import pandas as pd
import datetime as dt

from retrack.nodes.datetime import CurrentYear, DifferenceBetweenDates, Now, ToISOFormat


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


@pytest.mark.asyncio
async def test_current_year_node_run(current_year_input_data, mocker):
    datetime_mock = mocker.patch("retrack.nodes.datetime.dt.datetime")
    datetime_mock.now.return_value = mocker.MagicMock(year=2021)
    current_year_node = CurrentYear(**current_year_input_data)
    output = await current_year_node.run()
    assert output["output_value"] == 2021


@pytest.fixture
def now_input_data():
    return {
        "id": 19,
        "data": {},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "Now",
    }


def test_now_node(now_input_data):
    now_node = Now(**now_input_data)

    assert isinstance(now_node, Now)

    assert now_node.model_dump(by_alias=True) == {
        "id": "19",
        "name": "Now",
        "data": {"timezone": "America/Sao_Paulo"},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_now_node_run(now_input_data, mocker):
    now_node = Now(**now_input_data)
    datetime_now = dt.datetime.strptime("2025-07-01", "%Y-%m-%d")

    class DateTimeMock(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime_now

    mocker.patch("retrack.nodes.datetime.dt.datetime", DateTimeMock)

    output = await now_node.run()

    assert (output["output_value"] == pd.Series(["2025-07-01T00:00:00"])).all()


@pytest.fixture
def difference_between_dates_input_data():
    return {
        "id": 9,
        "data": {},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [1597.1904571362154, 628.6495284260166],
        "name": "DifferenceBetweenDates",
    }


def test_difference_between_dates_node(difference_between_dates_input_data):
    difference_between_dates_node = DifferenceBetweenDates(
        **difference_between_dates_input_data
    )

    assert isinstance(difference_between_dates_node, DifferenceBetweenDates)

    assert difference_between_dates_node.model_dump(by_alias=True) == {
        "id": "9",
        "name": "DifferenceBetweenDates",
        "data": {"timezone": "America/Sao_Paulo"},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_difference_between_dates_node_run(
    difference_between_dates_input_data, mocker
):
    difference_between_dates_node = DifferenceBetweenDates(
        **difference_between_dates_input_data
    )
    timestamp_now = pd.Timestamp("2025-07-01").normalize()

    class TimestampMock(pd.Timestamp):
        @classmethod
        def now(cls, tz=None):
            return timestamp_now

    mocker.patch("retrack.nodes.datetime.pd.Timestamp", TimestampMock)

    output = await difference_between_dates_node.run(
        pd.Series(["2025-01-01", "2025-07-01"]),
        pd.Series(["2025-07-01", "2025-01-01"]),
    )
    assert (output["output_value"] == pd.Series([181, -181])).all()

    output = await difference_between_dates_node.run(
        pd.Series(["2025-07-01", "2025-01-01"]),
        pd.Series(["2025-07-01", "2025-07-01"]),
    )
    assert (output["output_value"] == pd.Series([0, 181])).all()

    output = await difference_between_dates_node.run(
        pd.Series(["2024-12-31", "2025-07-01"]),
        pd.Series(["2025-07-01", "2024-12-31"]),
    )
    assert (output["output_value"] == pd.Series([182, -182])).all()


@pytest.fixture
def to_iso_format_input_data():
    return {
        "id": 20,
        "data": {},
        "inputs": {
            "input_value": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [300, 400],
        "name": "ToISOFormat",
    }


def test_to_iso_format_node(to_iso_format_input_data):
    to_iso_format_node = ToISOFormat(**to_iso_format_input_data)

    assert isinstance(to_iso_format_node, ToISOFormat)

    assert to_iso_format_node.model_dump(by_alias=True) == {
        "id": "20",
        "name": "ToISOFormat",
        "data": {
            "format": "%Y-%m-%d",
            "timezone": "America/Sao_Paulo",
        },
        "inputs": {
            "input_value": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_to_iso_format_node_run(to_iso_format_input_data):
    to_iso_format_node = ToISOFormat(**to_iso_format_input_data)

    output = await to_iso_format_node.run(pd.Series(["2025-09-24"]))
    assert (output["output_value"] == pd.Series(["2025-09-24T00:00:00-03:00"])).all()

    to_iso_format_input_data["data"]["format"] = "%d/%m/%Y"
    to_iso_format_node = ToISOFormat(**to_iso_format_input_data)
    output = await to_iso_format_node.run(pd.Series(["24/09/2025"]))
    assert (output["output_value"] == pd.Series(["2025-09-24T00:00:00-03:00"])).all()
