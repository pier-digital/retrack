from retrack.nodes import dynamic_nodes_registry
import pytest
import pydantic
from retrack.nodes.base import NodeKind


@pytest.fixture
def conditional_connector_metadata():
    return {
        "id": "8c699de048472225",
        "name": "BureauConnector",
        "data": {
            "name": "example",
            "source": "source_name",
            "resource": "resource_name",
            "headers": ["example_input_name", "another_input_name"],
            "headers_map": ["input_value_0", "input_value_1"],
        },
        "outputs": {
            "output_value": {
                "connections": [{"node": "c455f4437c0bb74d", "input": "input_value_0"}]
            }
        },
        "inputs": {
            "input_value_0": {
                "connections": [{"node": "77799551f097b7d3", "output": "output_value"}]
            },
            "input_value_1": {
                "connections": [{"node": "77799551f097bsda", "output": "output_value"}]
            },
        },
    }


def test_get_conditional_connector_factory():
    conditional_connector_factory = dynamic_nodes_registry().get("ConditionalConnector")

    assert callable(conditional_connector_factory)


def test_create_model_from_factory(conditional_connector_metadata):
    conditional_connector_factory = dynamic_nodes_registry().get("ConditionalConnector")
    ConditionalConnector = conditional_connector_factory(
        **conditional_connector_metadata
    )

    assert issubclass(ConditionalConnector, pydantic.BaseModel)

    model = ConditionalConnector(**conditional_connector_metadata)

    assert isinstance(model, ConditionalConnector)
    assert hasattr(model, "kind")

    assert model.kind() == NodeKind.CONNECTOR
