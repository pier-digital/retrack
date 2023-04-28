import json

import pytest

from retrack import Parser, Runner


@pytest.mark.parametrize(
    "filename, in_values, expected_out_values",
    [
        (
            "multiple-ifs",
            [{"number": 1}, {"number": 2}, {"number": 3}, {"number": 4}],
            [
                {"message": "first", "output": "1"},
                {"message": "second", "output": "2"},
                {"message": "third", "output": "3"},
                {"message": "other", "output": "0"},
            ],
        ),
        (
            "age-negative",
            [{"age": 10}, {"age": -10}, {"age": 18}, {"age": 19}, {"age": 100}],
            [
                {"message": "underage", "output": False},
                {"message": "invalid age", "output": False},
                {"message": "valid age", "output": True},
                {"message": "valid age", "output": True},
                {"message": "valid age", "output": True},
            ],
        ),
    ],
)
def test_flows(filename, in_values, expected_out_values):
    with open(f"tests/resources/{filename}.json", "r") as f:
        rule = json.load(f)

    runner = Runner(Parser(rule))
    out_values = runner(in_values)

    assert out_values == expected_out_values
