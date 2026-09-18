import pandas as pd
import pytest

from retrack.nodes.string_ops import (
    Concat,
    Length,
    Replace,
    SubString,
    Trim,
    UpperCase,
)


def _single_input_data(name: str, data=None):
    return {
        "id": 18,
        "data": data or {},
        "inputs": {
            "input_value": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": name,
    }


def _two_input_data(name: str, data=None):
    return {
        "id": 18,
        "data": data or {},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": name,
    }


###############################################################
# UpperCase
###############################################################


@pytest.mark.asyncio
async def test_upper_case_run():
    node = UpperCase(**_single_input_data("UpperCase"))
    output = await node.run(pd.Series(["abc", "Def", "g"]))
    assert (output["output_value"] == pd.Series(["ABC", "DEF", "G"])).all()


###############################################################
# Trim
###############################################################


@pytest.mark.asyncio
async def test_trim_run():
    node = Trim(**_single_input_data("Trim"))
    output = await node.run(pd.Series(["  abc  ", "def ", " g"]))
    assert (output["output_value"] == pd.Series(["abc", "def", "g"])).all()


###############################################################
# Length
###############################################################


@pytest.mark.asyncio
async def test_length_run():
    node = Length(**_single_input_data("Length"))
    output = await node.run(pd.Series(["abc", "de", ""]))
    assert (output["output_value"] == pd.Series([3, 2, 0])).all()


###############################################################
# Replace
###############################################################


@pytest.mark.asyncio
async def test_replace_run():
    node = Replace(**_single_input_data("Replace", {"old": "a", "new": "X"}))
    output = await node.run(pd.Series(["banana", "abc"]))
    assert (output["output_value"] == pd.Series(["bXnXnX", "Xbc"])).all()


@pytest.mark.asyncio
async def test_replace_is_literal_not_regex():
    node = Replace(**_single_input_data("Replace", {"old": ".", "new": "_"}))
    output = await node.run(pd.Series(["a.b.c", "abc"]))
    assert (output["output_value"] == pd.Series(["a_b_c", "abc"])).all()


###############################################################
# Concat
###############################################################


@pytest.mark.asyncio
async def test_concat_run():
    node = Concat(**_two_input_data("Concat"))
    output = await node.run(pd.Series(["a", "b"]), pd.Series(["1", "2"]))
    assert (output["output_value"] == pd.Series(["a1", "b2"])).all()


@pytest.mark.asyncio
async def test_concat_with_separator():
    node = Concat(**_two_input_data("Concat", {"separator": "-"}))
    output = await node.run(pd.Series(["a", "b"]), pd.Series(["1", "2"]))
    assert (output["output_value"] == pd.Series(["a-1", "b-2"])).all()


###############################################################
# SubString
###############################################################


@pytest.mark.asyncio
async def test_substring_run():
    node = SubString(**_single_input_data("SubString", {"start": 0, "end": 3}))
    output = await node.run(pd.Series(["abcdef", "12345"]))
    assert (output["output_value"] == pd.Series(["abc", "123"])).all()


@pytest.mark.asyncio
async def test_substring_without_end():
    node = SubString(**_single_input_data("SubString", {"start": 2}))
    output = await node.run(pd.Series(["abcdef"]))
    assert (output["output_value"] == pd.Series(["cdef"])).all()
