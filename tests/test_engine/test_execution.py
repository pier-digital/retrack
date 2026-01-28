import json
import pytest
import pandas as pd

from retrack import from_json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filename, in_values",
    [
        ("multiple-ifs", [{"number": 1}, {"number": 2}]),
    ],
)
async def test_to_normalized_dict(filename, in_values):
    graph_path = f"tests/resources/{filename}.json"
    expected_path = f"tests/resources/executions/{filename}.json"

    with open(graph_path, "r") as f:
        graph_data = json.load(f)

    runner = from_json(graph_data)
    execution, exception = await runner.execute(
        pd.DataFrame(in_values), debug_mode=True
    )
    assert exception is None
    normalized_records = execution.to_normalized_dict()

    with open(expected_path, "r") as f:
        expected_out_values = json.load(f)

    assert isinstance(normalized_records, list)
    assert normalized_records == expected_out_values
