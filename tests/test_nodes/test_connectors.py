import pytest

from retrack.nodes.connectors import BaseConnector


@pytest.fixture
def connector_dict():
    return {
        "id": 1,
        "data": {"name": "example", "default": "Hello World"},
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

    with pytest.raises(NotImplementedError):
        _ = connector.generate_input_nodes()
