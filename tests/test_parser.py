import json

import pytest

from retrack.engine.parser import Parser


@pytest.mark.parametrize(
    "data_filename,expected_tokens",
    [
        (
            "tests/resources/age-negative.json",
            {
                "start": ["0"],
                "input": ["2", "13"],
                "constant": ["3", "14"],
                "check": ["4", "15"],
                "if": ["6", "16"],
                "bool": ["9", "17", "18"],
                "output": ["10", "19", "20"],
            },
        )
    ],
)
def test_parser_extract(data_filename, expected_tokens):
    with open(data_filename) as f:
        input_data = json.load(f)

    parser = Parser(input_data)
    assert parser.components_registry.indexes_by_name_map == expected_tokens


def test_parser_with_unknown_node():
    with pytest.raises(ValueError):
        Parser({"nodes": {"1": {"name": "Unknown"}}})


def test_parser_invalid_input_data():
    with pytest.raises(TypeError):
        Parser("invalid data")


def test_parser_no_nodes():
    with pytest.raises(ValueError):
        Parser({})


def test_parser_invalid_nodes():
    with pytest.raises(TypeError):
        Parser({"nodes": "invalid nodes"})


def test_parser_node_no_name():
    with pytest.raises(ValueError):
        Parser({"nodes": {"1": {}}})


def test_parser_node_invalid_name():
    with pytest.raises(TypeError):
        Parser({"nodes": {"1": {"name": 1}}})
