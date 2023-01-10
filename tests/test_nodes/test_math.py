import pandas as pd

from retack.nodes.math import Math, MathOperator


def test_math_node():
    input_data = {
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

    math_node = Math(**input_data)

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


def test_math_node_run():
    input_data = {
        "id": 18,
        "data": {"operator": "+"},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "name": "Math",
    }

    math_node = Math(**input_data)
    output = math_node.run(pd.Series(["1"]), pd.Series(["2"]))

    assert (output["output_value"] == pd.Series([3])).all()
