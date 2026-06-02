import pandas as pd
import pydantic
import pytest

from retrack.nodes import dynamic_nodes_registry
from retrack.nodes.base import NodeKind
from retrack.nodes.dynamic.multiple_outputs import (
    MultipleOutputsMetadataModel,
    multiple_outputs_factory,
)
from retrack.utils import constants


# ---------------------------------------------------------------------------
# MultipleOutputsMetadataModel — unit tests
# ---------------------------------------------------------------------------


def test_metadata_valid():
    m = MultipleOutputsMetadataModel(headers_map=["basic_7", "basic_15"])
    assert m.headers_map == ["basic_7", "basic_15"]
    assert m.message is None


def test_metadata_with_message():
    m = MultipleOutputsMetadataModel(headers_map=["x"], message="cobertura")
    assert m.message == "cobertura"


def test_metadata_empty_string_message_becomes_none():
    m = MultipleOutputsMetadataModel(headers_map=["x"], message="")
    assert m.message is None


def test_metadata_rejects_empty_headers_map():
    with pytest.raises(pydantic.ValidationError, match="headers_map must not be empty"):
        MultipleOutputsMetadataModel(headers_map=[])


def test_metadata_rejects_duplicate_keys():
    with pytest.raises(pydantic.ValidationError, match="duplicate"):
        MultipleOutputsMetadataModel(headers_map=["a", "a"])


# ---------------------------------------------------------------------------
# Factory — registration and construction
# ---------------------------------------------------------------------------


@pytest.fixture
def node_metadata():
    return {
        "id": 10,
        "data": {
            "headers_map": ["basic_7", "basic_15", "basic_30"],
            "message": "cobertura",
        },
        "inputs": {
            "basic_7":  {"connections": [{"node": 2, "output": "output_value", "data": {}}]},
            "basic_15": {"connections": [{"node": 3, "output": "output_value", "data": {}}]},
            "basic_30": {"connections": [{"node": 4, "output": "output_value", "data": {}}]},
        },
        "name": "MultipleOutputs",
    }


def test_factory_is_registered_in_dynamic_registry():
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    assert callable(factory)


def test_factory_creates_valid_pydantic_model(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)

    assert issubclass(NodeClass, pydantic.BaseModel)

    node = NodeClass(**node_metadata)
    assert hasattr(node, "run")
    assert node.kind() == NodeKind.OUTPUT


def test_factory_creates_inputs_dynamically(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    input_fields = node.inputs.model_fields
    assert set(input_fields.keys()) == {"basic_7", "basic_15", "basic_30"}


def test_factory_node_has_no_outputs(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    assert node.outputs is None


# ---------------------------------------------------------------------------
# run() — output contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_returns_series_of_lists(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    result = await node.run(
        basic_7=pd.Series([3028, 2000]),
        basic_15=pd.Series([7194, 5000]),
        basic_30=pd.Series([15720, 8000]),
    )

    output = result[constants.OUTPUT_REFERENCE_COLUMN]
    assert isinstance(output, pd.Series)
    assert len(output) == 2

    assert output.iloc[0] == [
        {"key": "basic_7", "value": 3028},
        {"key": "basic_15", "value": 7194},
        {"key": "basic_30", "value": 15720},
    ]
    assert output.iloc[1] == [
        {"key": "basic_7", "value": 2000},
        {"key": "basic_15", "value": 5000},
        {"key": "basic_30", "value": 8000},
    ]


@pytest.mark.asyncio
async def test_run_preserves_index(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    idx = pd.Index([10, 20, 30])
    result = await node.run(
        basic_7=pd.Series([1, 2, 3], index=idx),
        basic_15=pd.Series([4, 5, 6], index=idx),
        basic_30=pd.Series([7, 8, 9], index=idx),
    )

    assert list(result[constants.OUTPUT_REFERENCE_COLUMN].index) == [10, 20, 30]


@pytest.mark.asyncio
async def test_run_message_is_replicated(node_metadata):
    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    result = await node.run(
        basic_7=pd.Series([1]),
        basic_15=pd.Series([2]),
        basic_30=pd.Series([3]),
    )

    assert result[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] == "cobertura"


@pytest.mark.asyncio
async def test_run_single_key():
    single_key_metadata = {
        "id": 99,
        "data": {"headers_map": ["only_key"], "message": None},
        "inputs": {
            "only_key": {"connections": [{"node": 1, "output": "output_value", "data": {}}]},
        },
        "name": "MultipleOutputs",
    }
    factory = multiple_outputs_factory(**single_key_metadata)
    node = factory(**single_key_metadata)

    result = await node.run(only_key=pd.Series([42]))

    output = result[constants.OUTPUT_REFERENCE_COLUMN]
    assert output.iloc[0] == [{"key": "only_key", "value": 42}]


@pytest.mark.asyncio
async def test_run_output_column_is_not_nan(node_metadata):
    """has_ended() depends on output not being NaN after run."""
    import numpy as np

    factory = dynamic_nodes_registry().get("MultipleOutputs")
    NodeClass = factory(**node_metadata)
    node = NodeClass(**node_metadata)

    result = await node.run(
        basic_7=pd.Series([100]),
        basic_15=pd.Series([200]),
        basic_30=pd.Series([300]),
    )

    output_series = result[constants.OUTPUT_REFERENCE_COLUMN]
    assert not output_series.isna().any(), "output must not be NaN so has_ended() returns True"
