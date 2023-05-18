import pandas as pd
import pytest

from retrack.nodes.math import AbsoluteValue, Math, MathOperator


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

    assert math_node.dict(by_alias=True) == {
        "id": "18",
        "data": {"operator": MathOperator.SUM},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


def test_math_node_run(math_operator_input_data):
    math_node = Math(**math_operator_input_data)
    output = math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([3])).all()

    math_operator_input_data["data"]["operator"] = "-"
    math_node = Math(**math_operator_input_data)
    output = math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([-1])).all()

    math_operator_input_data["data"]["operator"] = "*"
    math_node = Math(**math_operator_input_data)
    output = math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([2])).all()

    math_operator_input_data["data"]["operator"] = "/"
    math_node = Math(**math_operator_input_data)
    output = math_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series([0.5])).all()


def test_absolute_value_node_run(absolute_value_input_data):
    absolute_value_node = AbsoluteValue(**absolute_value_input_data)
    output = absolute_value_node.run(pd.Series(["-1", "1", "0", "-2"]))
    assert (output["output_value"] == pd.Series([1, 1, 0, 2])).all()
