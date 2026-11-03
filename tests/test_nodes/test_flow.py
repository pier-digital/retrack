import pytest

from retrack.nodes.dynamic.flow import FlowV0MetadataModel


@pytest.mark.parametrize("default", ["", None])
def test_flow_empty_default_behaves_like_null(default):
    metadata = FlowV0MetadataModel(value="{}", name="subflow", default=default)

    assert metadata.default is None


def test_flow_keeps_non_empty_default():
    metadata = FlowV0MetadataModel(value="{}", name="subflow", default="0")

    assert metadata.default == "0"
