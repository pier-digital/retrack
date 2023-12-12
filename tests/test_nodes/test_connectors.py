import pytest

from retrack.nodes.connectors import BaseConnector


@pytest.fixture
def connector_dict():
    return {
        "id": 1,
        "data": {
            "name": "example_name",
            "default": "Hello World",
            "service": "example_service",
            "identifier": "example_identifier",
        },
        "inputs": {},
        "outputs": {
            "output_value": {
                "connections": [{"node": 0, "input": "input_void", "data": {}}]
            }
        },
        "position": [-444.37109375, 175.50390625],
        "name": "Connector",
    }


def test_create_base_connector(connector_dict):
    connector = BaseConnector(**connector_dict)

    assert isinstance(connector, BaseConnector)
    assert connector.kind() == "connector"

    assert connector.data.name == "example_name"
    assert connector.data.default == "Hello World"
    assert connector.data.service == "example_service"
    assert connector.data.identifier == "example_identifier"

    with pytest.raises(NotImplementedError):
        _ = connector.generate_input_nodes()
