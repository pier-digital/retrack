import pandas as pd

from retrack.nodes.startswith import StartsWith

import pytest


@pytest.fixture
def input_data():
    return {
        "id": 10,
        "data": {},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
        "position": [1321.9899743354695, 255.18171516041082],
        "name": "StartsWith",
    }


def test_starts_with_node(input_data):
    starts_with_node = StartsWith(**input_data)

    assert isinstance(starts_with_node, StartsWith)

    assert starts_with_node.model_dump(by_alias=True) == {
        "id": "10",
        "name": "StartsWith",
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_starts_with_node_run(input_data):
    starts_with_node = StartsWith(**input_data)

    output = await starts_with_node.run(pd.Series(["100"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await starts_with_node.run(pd.Series(["100"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
