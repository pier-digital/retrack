from retrack.nodes.base import NodeKind
from retrack.nodes.inputs import Input, InputMetadataModel


class ConnectorMetadataModel(InputMetadataModel):
    service: str
    identifier: str


class BaseConnector(Input):
    data: ConnectorMetadataModel

    def kind(self) -> NodeKind:
        return NodeKind.CONNECTOR

    def run(self, **kwargs):
        return {}
