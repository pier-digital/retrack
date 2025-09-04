import pandas as pd
import pytest
from retrack.nodes.endswithany import EndsWithAny

input_data = {
    "id": 13,
    "data": {},
    "inputs": {"input_value": {"connections": []}, "input_list": {"connections": []}},
    "outputs": {"output_bool": {"connections": []}},
    "position": [1178.650051545976, 855.8644837700068],
    "name": "EndsWithAny",
}


def test_ends_with_any_node():
    ends_with_any_node = EndsWithAny(**input_data)

    assert isinstance(ends_with_any_node, EndsWithAny)


@pytest.mark.asyncio
async def test_ends_with_any_node_run():
    ends_with_any_node = EndsWithAny(**input_data)

    output = await ends_with_any_node.run(pd.Series(["100"]), pd.Series(["2", "1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await ends_with_any_node.run(pd.Series(["100"]), pd.Series(["2", "0"]))
    assert (output["output_bool"] == pd.Series([True])).all()
