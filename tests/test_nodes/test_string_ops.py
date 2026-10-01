import pandas as pd
import pydantic
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
    node = SubString(**_single_input_data("SubString", {"start": 1, "end": 3}))
    output = await node.run(pd.Series(["abcdef", "12345"]))
    assert output["output_value"].tolist() == ["abc", "123"]


@pytest.mark.asyncio
async def test_substring_is_one_based_and_inclusive():
    node = SubString(**_single_input_data("SubString", {"start": 2, "end": 4}))
    output = await node.run(pd.Series(["abcdef"]))
    assert output["output_value"].tolist() == ["bcd"]

    node = SubString(**_single_input_data("SubString", {"start": 3, "end": 3}))
    output = await node.run(pd.Series(["abcdef"]))
    assert output["output_value"].tolist() == ["c"]


@pytest.mark.asyncio
async def test_substring_without_end():
    node = SubString(**_single_input_data("SubString", {"start": 3}))
    output = await node.run(pd.Series(["abcdef"]))
    assert output["output_value"].tolist() == ["cdef"]


@pytest.mark.asyncio
async def test_substring_without_start():
    node = SubString(**_single_input_data("SubString", {"end": 2}))
    output = await node.run(pd.Series(["abcdef"]))
    assert output["output_value"].tolist() == ["ab"]


def test_substring_empty_positions_are_unset():
    node = SubString(**_single_input_data("SubString", {"start": "", "end": ""}))
    assert node.data.start is None
    assert node.data.end is None


@pytest.mark.parametrize(
    "data",
    [{"start": 0}, {"end": 0}, {"start": -1}, {"start": 4, "end": 3}],
)
def test_substring_invalid_positions_raise(data):
    with pytest.raises(pydantic.ValidationError):
        SubString(**_single_input_data("SubString", data))


###############################################################
# Validation
###############################################################


def test_replace_requires_old():
    with pytest.raises(pydantic.ValidationError):
        Replace(**_single_input_data("Replace"))

    with pytest.raises(pydantic.ValidationError):
        Replace(**_single_input_data("Replace", {"old": "", "new": "x"}))


@pytest.mark.asyncio
async def test_replace_without_new_removes_old():
    node = Replace(**_single_input_data("Replace", {"old": "a", "new": ""}))
    output = await node.run(pd.Series(["banana"]))
    assert output["output_value"].tolist() == ["bnn"]


@pytest.mark.asyncio
async def test_non_string_values_are_cast_to_string():
    node = UpperCase(**_single_input_data("UpperCase"))
    output = await node.run(pd.Series([42.0, True, "a"], dtype=object))
    assert output["output_value"].tolist() == ["42.0", "TRUE", "A"]

    node = Length(**_single_input_data("Length"))
    output = await node.run(pd.Series([12345]))
    assert output["output_value"].tolist() == [5]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "node_class,data",
    [
        (UpperCase, None),
        (Trim, None),
        (Length, None),
        (Replace, {"old": "a"}),
        (SubString, {"start": 1}),
    ],
)
async def test_single_input_nodes_raise_on_null(node_class, data):
    node = node_class(**_single_input_data(node_class.__name__, data))
    with pytest.raises(ValueError, match="null value"):
        await node.run(pd.Series(["a", None]))


@pytest.mark.asyncio
async def test_concat_raises_on_null():
    node = Concat(**_two_input_data("Concat"))
    with pytest.raises(ValueError, match="null value"):
        await node.run(pd.Series(["a", "b"]), pd.Series(["1", None]))
