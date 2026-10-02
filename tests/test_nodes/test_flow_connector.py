import json

import pandas as pd
import pytest

from retrack import nodes
from retrack.engine.rule import Rule
from retrack.nodes.base import NodeKind
from retrack.nodes.dynamic.flow_connector import (
    connector_header,
    flow_connector_factory,
)

CHILD_NODE_ID = "a1b2c3d4"


@pytest.fixture
def single_output_metadata():
    return {
        "id": "5",
        "name": "FlowConnector",
        "data": {
            "name": "child_value",
            "flow": "child-flow",
            "version": "latest",
        },
        "inputs": {
            "input_void": {"connections": [{"node": "1", "output": "output_up_void"}]}
        },
        "outputs": {
            "output_value": {"connections": [{"node": "10", "input": "input_value"}]}
        },
    }


@pytest.fixture
def multi_output_metadata():
    return {
        "id": "5",
        "name": "FlowConnector",
        "data": {
            "name": "child_values",
            "flow": "child-flow",
            "version": "latest",
        },
        "inputs": {
            "input_void": {"connections": [{"node": "1", "output": "output_up_void"}]}
        },
        "outputs": {
            f"first_output@{CHILD_NODE_ID}": {
                "connections": [{"node": "10", "input": "first_output"}]
            },
            f"second_output@{CHILD_NODE_ID}": {
                "connections": [{"node": "10", "input": "second_output"}]
            },
        },
    }


def test_connector_header():
    assert connector_header(f"first_output@{CHILD_NODE_ID}") == "first_output"
    assert connector_header("first_output") == "first_output"


def test_single_output_payload_columns(single_output_metadata):
    node_class = flow_connector_factory(**single_output_metadata)
    node = node_class(**single_output_metadata)

    assert node.kind() == NodeKind.CONNECTOR
    assert node.payload_columns() == {"output_value": "child_value"}


def test_multi_output_accepts_dynamic_outputs(multi_output_metadata):
    node_class = flow_connector_factory(**multi_output_metadata)
    node = node_class(**multi_output_metadata)

    assert node.kind() == NodeKind.CONNECTOR
    assert [name for name, _ in node.outputs] == [
        f"first_output@{CHILD_NODE_ID}",
        f"second_output@{CHILD_NODE_ID}",
    ]


def test_multi_output_payload_columns(multi_output_metadata):
    node_class = flow_connector_factory(**multi_output_metadata)
    node = node_class(**multi_output_metadata)

    assert node.payload_columns() == {
        f"first_output@{CHILD_NODE_ID}": "child_values.first_output",
        f"second_output@{CHILD_NODE_ID}": "child_values.second_output",
    }


@pytest.fixture
def multi_output_executor():
    with open("tests/resources/flow-connector-multiple-outputs.json", "r") as f:
        graph_data = json.load(f)

    return Rule.create(
        graph_data,
        nodes_registry=nodes.registry(),
        dynamic_nodes_registry=nodes.dynamic_nodes_registry(),
    ).executor


def test_multi_output_request_columns(multi_output_executor):
    assert set(multi_output_executor.request_manager.dataframe_model.keys()) == {
        "value",
        "child_values.first_output",
        "child_values.second_output",
    }
    assert multi_output_executor.input_columns == {
        "2@output_value": "value",
        f"5@first_output@{CHILD_NODE_ID}": "child_values.first_output",
        f"5@second_output@{CHILD_NODE_ID}": "child_values.second_output",
    }


@pytest.mark.asyncio
async def test_multi_output_mock_fills_each_output_from_payload(
    multi_output_executor,
):
    payload = pd.DataFrame(
        [
            {
                "value": "a",
                "child_values.first_output": "4269",
                "child_values.second_output": "450000",
            },
            {
                "value": "b",
                "child_values.first_output": "100",
                "child_values.second_output": "200",
            },
        ]
    )

    result = await multi_output_executor.execute(payload)
    records = result.to_dict(orient="records")

    assert records[0]["output"] == [
        {"key": "first_output", "value": "4269"},
        {"key": "second_output", "value": "450000"},
    ]
    assert records[1]["output"] == [
        {"key": "first_output", "value": "100"},
        {"key": "second_output", "value": "200"},
    ]


@pytest.mark.asyncio
async def test_multi_output_mock_requires_each_output_column(multi_output_executor):
    payload = pd.DataFrame(
        [{"value": "a", "child_values.first_output": "4269"}]
    )

    with pytest.raises(Exception):
        await multi_output_executor.execute(payload)
