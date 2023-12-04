import json

import pytest

from retrack.engine.parser import Parser
from retrack import nodes


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

    parser = Parser(
        input_data,
        nodes_registry=nodes.registry(),
        dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
    )
    assert parser.components_registry.indexes_by_name_map == expected_tokens


def test_parser_with_unknown_node():
    with pytest.raises(ValueError):
        Parser(
            {"nodes": {"1": {"name": "Unknown"}}},
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )


def test_parser_invalid_input_data():
    with pytest.raises(TypeError):
        Parser(
            "invalid data",
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )


def test_parser_no_nodes():
    with pytest.raises(ValueError):
        Parser(
            {},
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )


def test_parser_invalid_nodes():
    with pytest.raises(TypeError):
        Parser(
            {"nodes": "invalid nodes"},
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )


def test_parser_node_no_name():
    with pytest.raises(ValueError):
        Parser(
            {"nodes": {"1": {}}},
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )


def test_parser_node_invalid_name():
    with pytest.raises(TypeError):
        Parser(
            {"nodes": {"1": {"name": 1}}},
            nodes_registry=nodes.registry(),
            dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
        )
