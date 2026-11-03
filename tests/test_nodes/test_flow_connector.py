import pytest

from retrack.nodes.dynamic.flow_connector import FlowConnectorMetadataModel


@pytest.mark.parametrize("default", ["", None])
def test_flow_connector_empty_default_behaves_like_null(default):
    metadata = FlowConnectorMetadataModel(
        name="example", flow="flow_name", version="1", default=default
    )

    assert metadata.default is None


def test_flow_connector_keeps_non_empty_default():
    metadata = FlowConnectorMetadataModel(
        name="example", flow="flow_name", version="1", default="0"
    )

    assert metadata.default == "0"
