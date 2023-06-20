import json

import pandas as pd
import pytest

from retrack import Parser, Runner


@pytest.mark.parametrize(
    "filename, in_values, expected_out_values",
    [
        (
            "multiple-ifs",
            {"number": 1},
            [
                {"message": "first", "output": "1"},
            ],
        ),
        (
            "age-negative",
            {"age": 10},
            [
                {"message": "underage", "output": False},
            ],
        ),
    ],
)
def test_flows_with_single_element(filename, in_values, expected_out_values):
    with open(f"tests/resources/{filename}.json", "r") as f:
        rule = json.load(f)

    runner = Runner(Parser(rule))
    out_values = runner.execute(in_values)

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


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
    out_values = runner.execute(in_values)

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


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
def test_create_from_json(filename, in_values, expected_out_values):
    runner = Runner.from_json(f"tests/resources/{filename}.json")
    out_values = runner.execute(in_values)

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


def test_create_from_json_with_invalid_type():
    with pytest.raises(ValueError):
        Runner.from_json(1)


def test_csv_table_with_if():
    runner = Runner.from_json("tests/resources/csv-table-with-if.json")

    in_values = [
        {"in_a": 0, "in_b": 0, "in_d": 0, "in_e": 0},
        {"in_a": 0, "in_b": 1, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 0, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": 0, "in_e": 1},
        {"in_a": 1, "in_b": 1, "in_d": 1, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": -1, "in_e": 0},
    ]

    out_values = runner.execute(in_values)

    assert isinstance(out_values, pd.DataFrame)
    assert len(out_values) == len(in_values)
    assert out_values["output"].astype(int).values.tolist() == [-1, -1, -1, 1, 1, 0, 3]
    assert out_values["message"].values.tolist() == [
        "else",
        "else",
        "else",
        "then",
        "then",
        "then",
        "then",
    ]
