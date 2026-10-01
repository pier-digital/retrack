import numpy as np
import pandas as pd
import pydantic
import pytest

from retrack.nodes.convert import ToBool, ToNumber, ToString


def _input_data(name: str, data=None):
    output_name = "output_bool" if name == "ToBool" else "output_value"
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


###############################################################
# ToBool
###############################################################


@pytest.mark.asyncio
async def test_to_bool_run():
    node = ToBool(**_input_data("ToBool"))
    output = await node.run(pd.Series(["true", "1", "yes", "y", " T "]))
    assert output["output_bool"].tolist() == [True] * 5

    output = await node.run(pd.Series(["false", "0", "no", "n", "F"]))
    assert output["output_bool"].tolist() == [False] * 5


@pytest.mark.asyncio
async def test_to_bool_accepts_bools_and_numbers():
    node = ToBool(**_input_data("ToBool"))
    output = await node.run(pd.Series([True, False, 1, 0, 1.0, 0.0], dtype=object))
    assert output["output_bool"].tolist() == [True, False, True, False, True, False]

    output = await node.run(pd.Series([1.0, 0.0]))
    assert output["output_bool"].tolist() == [True, False]


@pytest.mark.asyncio
async def test_to_bool_invalid_value_raises():
    node = ToBool(**_input_data("ToBool"))
    with pytest.raises(ValueError, match="could not convert"):
        await node.run(pd.Series(["true", "sim", "anything"]))

    with pytest.raises(ValueError, match="could not convert"):
        await node.run(pd.Series([2]))


@pytest.mark.asyncio
async def test_to_bool_null_without_default_raises():
    node = ToBool(**_input_data("ToBool"))
    with pytest.raises(ValueError, match="no default is configured"):
        await node.run(pd.Series(["true", None]))


@pytest.mark.asyncio
async def test_to_bool_null_uses_default():
    node = ToBool(**_input_data("ToBool", {"default": "true"}))
    output = await node.run(pd.Series([None, np.nan, "false"]))
    assert output["output_bool"].tolist() == [True, True, False]
    assert output["output_bool"].dtype == bool


@pytest.mark.parametrize("default", [True, 1, "yes"])
def test_to_bool_default_accepts_bool_like(default):
    node = ToBool(**_input_data("ToBool", {"default": default}))
    assert node.data.default is True


def test_to_bool_invalid_default_raises():
    with pytest.raises(pydantic.ValidationError):
        ToBool(**_input_data("ToBool", {"default": "sim"}))


def test_to_bool_empty_default_is_unset():
    node = ToBool(**_input_data("ToBool", {"default": ""}))
    assert node.data.default is None


###############################################################
# ToNumber
###############################################################


@pytest.mark.asyncio
async def test_to_number_run():
    node = ToNumber(**_input_data("ToNumber"))
    output = await node.run(pd.Series(["1", "2.5", "-3", 4]))
    assert output["output_value"].tolist() == [1.0, 2.5, -3.0, 4.0]


@pytest.mark.asyncio
async def test_to_number_invalid_value_raises():
    node = ToNumber(**_input_data("ToNumber", {"default": 9}))
    with pytest.raises(ValueError, match="could not convert"):
        await node.run(pd.Series(["abc", "5"]))

    with pytest.raises(ValueError, match="could not convert"):
        await node.run(pd.Series(["inf"]))

    with pytest.raises(ValueError, match="could not convert"):
        await node.run(pd.Series([True], dtype=object))


@pytest.mark.asyncio
async def test_to_number_null_without_default_raises():
    node = ToNumber(**_input_data("ToNumber"))
    with pytest.raises(ValueError, match="no default is configured"):
        await node.run(pd.Series(["1", None]))


@pytest.mark.asyncio
async def test_to_number_null_uses_default():
    node = ToNumber(**_input_data("ToNumber", {"default": "9"}))
    output = await node.run(pd.Series([None, np.nan, "5"]))
    assert output["output_value"].tolist() == [9.0, 9.0, 5.0]


@pytest.mark.parametrize("default", [0, 9, "9", 1.5])
def test_to_number_default_accepts_numbers(default):
    node = ToNumber(**_input_data("ToNumber", {"default": default}))
    assert node.data.default == float(default)


@pytest.mark.parametrize("default", ["abc", True, "nan", "inf"])
def test_to_number_invalid_default_raises(default):
    with pytest.raises(pydantic.ValidationError):
        ToNumber(**_input_data("ToNumber", {"default": default}))


###############################################################
# ToString
###############################################################


@pytest.mark.asyncio
async def test_to_string_run():
    node = ToString(**_input_data("ToString"))
    output = await node.run(pd.Series([1, 2.5, "x", True], dtype=object))
    assert output["output_value"].tolist() == ["1", "2.5", "x", "True"]


@pytest.mark.asyncio
async def test_to_string_null_without_default_raises():
    node = ToString(**_input_data("ToString"))
    with pytest.raises(ValueError, match="no default is configured"):
        await node.run(pd.Series(["x", None]))


@pytest.mark.asyncio
async def test_to_string_null_uses_default():
    node = ToString(**_input_data("ToString", {"default": "N/A"}))
    output = await node.run(pd.Series([None, np.nan, "x"]))
    assert output["output_value"].tolist() == ["N/A", "N/A", "x"]


def test_to_string_default_is_cast_to_string():
    node = ToString(**_input_data("ToString", {"default": 0}))
    assert node.data.default == "0"


def test_to_string_empty_default_is_unset():
    node = ToString(**_input_data("ToString", {"default": ""}))
    assert node.data.default is None


@pytest.mark.asyncio
async def test_to_string_whitespace_default_is_kept():
    node = ToString(**_input_data("ToString", {"default": " "}))
    output = await node.run(pd.Series([None, "x"]))
    assert output["output_value"].tolist() == [" ", "x"]


@pytest.mark.parametrize("node_class", [ToBool, ToNumber])
def test_whitespace_default_is_invalid_for_bool_and_number(node_class):
    with pytest.raises(pydantic.ValidationError):
        node_class(**_input_data(node_class.__name__, {"default": " "}))
