import pandas as pd
from retrack.nodes.contains import Contains


import pytest


@pytest.fixture
def input_data():
    return {
        "id": 9,
        "data": {},
        "inputs": {
            "input_list": {"connections": []},
            "input_value": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
        "position": [1597.1904571362154, 628.6495284260166],
        "name": "Contains",
    }


def test_contains_node(input_data):
    contains_node = Contains(**input_data)

    assert isinstance(contains_node, Contains)

    assert contains_node.model_dump(by_alias=True) == {
        "id": "9",
        "name": "Contains",
        "inputs": {
            "input_list": {"connections": []},
            "input_value": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_contains_node_run(input_data):
    contains_node = Contains(**input_data)

    output = await contains_node.run(pd.Series(["1", "2"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = await contains_node.run(pd.Series(["1", "2"]), pd.Series(["3"]))
    assert (output["output_bool"] == pd.Series([False])).all()
