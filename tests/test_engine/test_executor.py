import json

import pandas as pd
import pytest

from retrack import Rule, from_json, nodes, RuleExecutor
from retrack.utils.exceptions import ExecutionException


@pytest.mark.asyncio
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
        (
            "glm",
            {"a": 1, "b": 4},
            [
                {"message": None, "output": 5},
            ],
        ),
    ],
)
async def test_flows_with_single_element(filename, in_values, expected_out_values):
    with open(f"tests/resources/{filename}.json", "r") as f:
        graph_data = json.load(f)

    executor = Rule.create(
        graph_data,
        nodes_registry=nodes.registry(),
        dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
    ).executor

    out_values = await executor.execute(pd.DataFrame([in_values]))

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


@pytest.mark.asyncio
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
        (
            "age-categorizer",
            [
                {"age": 0},
                {"age": 17},
                {"age": 18},
                {"age": 23},
                {"age": 24},
                {"age": 39},
                {"age": 40},
                {"age": 99},
            ],
            [
                {"message": None, "output": "invalid"},
                {"message": None, "output": "invalid"},
                {"message": None, "output": "group 1"},
                {"message": None, "output": "group 1"},
                {"message": None, "output": "group 2"},
                {"message": None, "output": "group 2"},
                {"message": None, "output": "group 3"},
                {"message": None, "output": "group 3"},
            ],
        ),
        (
            "rule-with-version",
            [{"variable": 0}, {"variable": 100}, {"variable": 200}],
            [
                {"message": None, "output": False},
                {"message": None, "output": True},
                {"message": None, "output": False},
            ],
        ),
        (
            "to-lowercase",
            [{"var": "EXAMPLE"}, {"var": "test with numbers 120"}, {"var": 200}],
            [
                {"message": None, "output": "example"},
                {"message": None, "output": "test with numbers 120"},
                {"message": None, "output": "200"},
            ],
        ),
        (
            "issubstringof",
            [
                {"input_var": "EXAMPLE"},
                {"input_var": "test foo numbers 120"},
                {"input_var": "foodsadsafoodsadas"},
            ],
            [
                {"message": None, "output": False},
                {"message": None, "output": True},
                {"message": None, "output": True},
            ],
        ),
        (
            "cpf-digit",
            [
                {"cpf": "53154432770"},
                {"cpf": "22222224122"},
            ],
            [
                {"message": None, "output": "2"},
                {"message": None, "output": "4"},
            ],
        ),
        (
            "glm",
            [
                {"a": 1, "b": 4},
                {"a": 2, "b": 3},
                {"a": -1, "b": -1},
            ],
            [
                {"message": None, "output": 5},
                {"message": None, "output": 6.5},
                {"message": None, "output": -1.5},
            ],
        ),
    ],
)
async def test_flows(filename, in_values, expected_out_values):
    with open(f"tests/resources/{filename}.json", "r") as f:
        graph_data = json.load(f)

    executor = Rule.create(
        graph_data,
        nodes_registry=nodes.registry(),
        dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
    ).executor

    out_values = await executor.execute(pd.DataFrame(in_values))

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


@pytest.mark.asyncio
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
        (
            "round-node",
            [{"var_a": 1.1, "var_b": 1.5}, {"var_a": 3.6, "var_b": 2.1}],
            [
                {"output": 2, "message": None},
                {"output": 8, "message": None},
            ],
        ),
        (
            "rule-of-rules",
            [
                {"example_a": 1, "var_b": 2},
                {"example_a": 3, "var_b": 2},
                {"example_a": 4, "var_b": 2},
                {"example_a": 5, "var_b": 5},
            ],
            [
                {"output": 2, "message": None},
                {"output": 6, "message": None},
                {"output": 8, "message": None},
                {"output": 25, "message": None},
            ],
        ),
        (
            "connector-rule",
            [
                {"prediction": "1", "multiplier": "1"},
                {"prediction": "2", "multiplier": "1"},
                {"prediction": "3", "multiplier": "1"},
                {"prediction": "4", "multiplier": "1"},
            ],
            [
                {"output": 1.0, "message": None},
                {"output": 2.0, "message": None},
                {"output": 3.0, "message": None},
                {"output": 4.0, "message": None},
            ],
        ),
        (
            "rule-of-rules-with-different-names",
            [
                {"first_name": "1"},
                {"first_name": "2"},
                {"first_name": "3"},
                {"first_name": "4"},
                {"first_name": "example"},
            ],
            [
                {"output": True, "message": None},
                {"output": True, "message": None},
                {"output": True, "message": None},
                {"output": True, "message": None},
                {"output": True, "message": None},
            ],
        ),
    ],
)
async def test_create_from_json(filename, in_values, expected_out_values):
    runner = from_json(f"tests/resources/{filename}.json")
    out_values = await runner.execute(pd.DataFrame(in_values))

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


def test_create_from_json_with_invalid_type():
    with pytest.raises(ValueError):
        from_json(1)


@pytest.mark.asyncio
async def test_subflow_with_connector():
    _input_df = pd.DataFrame(
        {
            "sepal_length": [1, 2, 3],
            "sepal_width": [1, 2, 3],
            "petal_length": [1, 2, 3],
            "petal_width": [1, 2, 3],
        }
    )
    filename = "tests/resources/subrule-with-connector.json"
    rule = from_json(filename)

    with pytest.raises(ExecutionException):
        _ = await rule.execute(_input_df)

    _input_df["prediction"] = [1, 2, 3]
    out_df = await rule.execute(_input_df)
    assert isinstance(out_df, pd.DataFrame)
    assert len(out_df) == len(_input_df)
    assert out_df["output"].values.tolist() == ["1", "2", "3"]


@pytest.mark.asyncio
async def test_csv_table_with_if():
    runner = from_json("tests/resources/csv-table-with-if.json")

    in_values = [
        {"in_a": 0, "in_b": 0, "in_d": 0, "in_e": 0},
        {"in_a": 0, "in_b": 1, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 0, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": 0, "in_e": 1},
        {"in_a": 1, "in_b": 1, "in_d": 1, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": 0, "in_e": 0},
        {"in_a": 1, "in_b": 1, "in_d": -1, "in_e": 0},
    ]

    out_values = await runner.execute(pd.DataFrame(in_values))

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


def test_create_from_json_with_dict():
    with open("tests/resources/multiple-ifs.json", "r") as f:
        graph_data = json.load(f)

    assert isinstance(from_json(graph_data), RuleExecutor)
    assert isinstance(from_json(graph_data, return_executor=False), Rule)


@pytest.mark.asyncio
async def test_rules_with_subrules_with_conditions():
    with open("tests/resources/rules-with-subrules-with-conditions.json", "r") as f:
        graph_data = json.load(f)

    executor = Rule.create(
        graph_data,
        nodes_registry=nodes.registry(),
        dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
    ).executor

    in_values = [
        {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
        }
    ]

    out_values = await executor.execute(pd.DataFrame(in_values))

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == [
        {"message": "< ten", "output": "10"},
    ]
