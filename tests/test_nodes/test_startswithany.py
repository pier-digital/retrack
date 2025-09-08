import pandas as pd
import pytest
from retrack.nodes.startswithany import StartsWithAny


@pytest.fixture
def input_data():
    return {
        "id": 13,
        "data": {},
        "inputs": {
            "input_value": {"connections": []},
            "input_list": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
        "position": [1178.650051545976, 855.8644837700068],
        "name": "StartsWithAny",
    }


def test_starts_with_any_node(input_data):
    starts_with_any_node = StartsWithAny(**input_data)

    assert isinstance(starts_with_any_node, StartsWithAny)

    assert starts_with_any_node.model_dump(by_alias=True) == {
        "id": "13",
        "name": "StartsWithAny",
        "inputs": {
            "input_value": {"connections": []},
            "input_list": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


@pytest.mark.asyncio
async def test_starts_with_any_node_run(input_data):
    starts_with_any_node = StartsWithAny(**input_data)

    output = await starts_with_any_node.run(pd.Series(["100"]), pd.Series(["2", "1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = await starts_with_any_node.run(pd.Series(["100"]), pd.Series(["2", "3"]))
    assert (output["output_bool"] == pd.Series([False])).all()
