import pandas as pd
import pytest

from retrack.nodes.math import AbsoluteValue, Ceil, Floor, Math, MathOperator, Max, Min, Round


@pytest.fixture
def math_operator_input_data():
    return {
        "id": 18,
        "data": {"operator": "+"},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "Math",
    }


@pytest.fixture
def absolute_value_input_data():
    return {
        "id": 18,
        "data": {},
        "inputs": {
            "input_value": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "AbsoluteValue",
    }


def test_math_node(math_operator_input_data):
    math_node = Math(**math_operator_input_data)

    assert isinstance(math_node, Math)
    assert isinstance(math_node.data.operator, MathOperator)

    assert math_node.model_dump(by_alias=True) == {
        "id": "18",
        "name": "Math",
        "data": {"operator": MathOperator.SUM},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_math_node_run(math_operator_input_data):
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([3])).all()

    math_operator_input_data["data"]["operator"] = "-"
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([-1])).all()

    math_operator_input_data["data"]["operator"] = "*"
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([2])).all()

    math_operator_input_data["data"]["operator"] = "/"
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([0.5])).all()


@pytest.mark.asyncio
async def test_absolute_value_node_run(absolute_value_input_data):
    absolute_value_node = AbsoluteValue(**absolute_value_input_data)
    output = await absolute_value_node.run(pd.Series(["-1", "1", "0", "-2"]))
    assert (output["output_value"] == pd.Series([1, 1, 0, 2])).all()


@pytest.mark.asyncio
async def test_round_node_run(absolute_value_input_data):
    round_node = Round(**absolute_value_input_data)
    output = await round_node.run(pd.Series(["-1.5", "1.5", "0", "-2.5"]))
    assert (output["output_value"] == pd.Series([-2, 2, 0, -2])).all()


@pytest.mark.asyncio
async def test_math_node_power_and_modulo(math_operator_input_data):
    math_operator_input_data["data"]["operator"] = "**"
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["2"]), pd.Series(["3"]))
    assert (output["output_value"] == pd.Series([8.0])).all()

    math_operator_input_data["data"]["operator"] = "%"
    math_node = Math(**math_operator_input_data)
    output = await math_node.run(pd.Series(["10"]), pd.Series(["3"]))
    assert (output["output_value"] == pd.Series([1.0])).all()


@pytest.mark.asyncio
async def test_floor_node_run(absolute_value_input_data):
    floor_node = Floor(**absolute_value_input_data)
    output = await floor_node.run(pd.Series(["1.9", "2.1", "-1.1", "0"]))
    assert (output["output_value"] == pd.Series([1, 2, -2, 0])).all()


@pytest.mark.asyncio
async def test_ceil_node_run(absolute_value_input_data):
    ceil_node = Ceil(**absolute_value_input_data)
    output = await ceil_node.run(pd.Series(["1.1", "2.9", "-1.9", "0"]))
    assert (output["output_value"] == pd.Series([2, 3, -1, 0])).all()


@pytest.mark.asyncio
async def test_min_node_run(math_operator_input_data):
    min_node = Min(**math_operator_input_data)
    output = await min_node.run(pd.Series(["3", "1", "5"]), pd.Series(["2", "4", "5"]))
    assert (output["output_value"] == pd.Series([2.0, 1.0, 5.0])).all()


@pytest.mark.asyncio
async def test_max_node_run(math_operator_input_data):
    max_node = Max(**math_operator_input_data)
    output = await max_node.run(pd.Series(["3", "1", "5"]), pd.Series(["2", "4", "5"]))
    assert (output["output_value"] == pd.Series([3.0, 4.0, 5.0])).all()
