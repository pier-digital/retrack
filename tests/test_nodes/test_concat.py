import pandas as pd
from retrack.nodes.concat import Concat


import pytest


@pytest.fixture
def input_data():
    return {
        "id": 9,
        "data": {"separator": ""},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [1597.1904571362154, 628.6495284260166],
        "name": "Concat",
    }


def test_concat_node(input_data):
    concat_node = Concat(**input_data)

    assert isinstance(concat_node, Concat)

    assert concat_node.model_dump(by_alias=True) == {
        "id": "9",
        "name": "Concat",
        "data": {"separator": ""},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
    }


def test_concat_node_run(input_data):
    concat_node = Concat(**input_data)

    output = concat_node.run(pd.Series(["one"]), pd.Series(["two"]))
    assert (output["output_value"] == pd.Series(["onetwo"])).all()
    output = concat_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_value"] == pd.Series(["12"])).all()
