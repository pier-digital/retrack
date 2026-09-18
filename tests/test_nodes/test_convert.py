import numpy as np
import pandas as pd
import pytest

from retrack.nodes.convert import ToBool, ToNumber, ToString


def _input_data(name: str, output_name: str, data=None):
    return {
        "id": 18,
        "data": data or {},
        "inputs": {
            "input_value": {"connections": []},
        },
        "outputs": {output_name: {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": name,
    }


@pytest.fixture
def to_bool_input_data():
    return _input_data("ToBool", "output_bool")


@pytest.fixture
def to_number_input_data():
    return _input_data("ToNumber", "output_value")


@pytest.fixture
def to_string_input_data():
    return _input_data("ToString", "output_value")


###############################################################
# ToBool
###############################################################


@pytest.mark.asyncio
async def test_to_bool_run(to_bool_input_data):
    node = ToBool(**to_bool_input_data)
    output = await node.run(pd.Series(["true", "1", "yes", "y", "t"]))
    assert (output["output_bool"] == pd.Series([True, True, True, True, True])).all()

    output = await node.run(pd.Series(["false", "0", "no", "anything"]))
    assert (output["output_bool"] == pd.Series([False, False, False, False])).all()


@pytest.mark.asyncio
async def test_to_bool_null_uses_default(to_bool_input_data):
    node = ToBool(**to_bool_input_data)
    output = await node.run(pd.Series([None, np.nan]))
    # no default set -> fixed fallback False
    assert (output["output_bool"] == pd.Series([False, False])).all()

    node = ToBool(**_input_data("ToBool", "output_bool", {"default": "true"}))
    output = await node.run(pd.Series([None, np.nan]))
    assert (output["output_bool"] == pd.Series([True, True])).all()


@pytest.mark.asyncio
async def test_to_bool_never_returns_nan(to_bool_input_data):
    node = ToBool(**to_bool_input_data)
    output = await node.run(pd.Series([None, "x", np.nan, "1"]))
    assert not output["output_bool"].isna().any()
    assert output["output_bool"].dtype == bool


###############################################################
# ToNumber
###############################################################


@pytest.mark.asyncio
async def test_to_number_run(to_number_input_data):
    node = ToNumber(**to_number_input_data)
    output = await node.run(pd.Series(["1", "2.5", "-3"]))
    assert (output["output_value"] == pd.Series([1.0, 2.5, -3.0])).all()


@pytest.mark.asyncio
async def test_to_number_invalid_uses_default(to_number_input_data):
    node = ToNumber(**to_number_input_data)
    output = await node.run(pd.Series(["abc", None, "5"]))
    # no default -> fixed fallback 0
    assert (output["output_value"] == pd.Series([0.0, 0.0, 5.0])).all()

    node = ToNumber(**_input_data("ToNumber", "output_value", {"default": "9"}))
    output = await node.run(pd.Series(["abc", None, "5"]))
    assert (output["output_value"] == pd.Series([9.0, 9.0, 5.0])).all()


@pytest.mark.asyncio
async def test_to_number_non_numeric_default_falls_back_to_zero(to_number_input_data):
    node = ToNumber(**_input_data("ToNumber", "output_value", {"default": "abc"}))
    output = await node.run(pd.Series(["x"]))
    assert (output["output_value"] == pd.Series([0.0])).all()


@pytest.mark.asyncio
async def test_to_number_never_returns_nan(to_number_input_data):
    node = ToNumber(**to_number_input_data)
    output = await node.run(pd.Series(["abc", None, np.nan, "5"]))
    assert not output["output_value"].isna().any()


###############################################################
# ToString
###############################################################


@pytest.mark.asyncio
async def test_to_string_run(to_string_input_data):
    node = ToString(**to_string_input_data)
    output = await node.run(pd.Series([1, 2.5, "x"]))
    assert (output["output_value"] == pd.Series(["1", "2.5", "x"])).all()


@pytest.mark.asyncio
async def test_to_string_null_uses_default(to_string_input_data):
    node = ToString(**to_string_input_data)
    output = await node.run(pd.Series([None, np.nan]))
    # no default -> fixed fallback "" (never the literal "nan")
    assert (output["output_value"] == pd.Series(["", ""])).all()

    node = ToString(**_input_data("ToString", "output_value", {"default": "N/A"}))
    output = await node.run(pd.Series([None, np.nan]))
    assert (output["output_value"] == pd.Series(["N/A", "N/A"])).all()


@pytest.mark.asyncio
async def test_to_string_never_returns_nan(to_string_input_data):
    node = ToString(**to_string_input_data)
    output = await node.run(pd.Series([None, np.nan, "x", 1]))
    assert not output["output_value"].isna().any()
    assert not (output["output_value"] == "nan").any()
