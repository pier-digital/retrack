import typing

from retrack.nodes.base import NodeKind
from retrack.nodes.inputs import Input, InputMetadataModel


class ConnectorMetadataModel(InputMetadataModel):
    service: str
    identifier: str


class VirtualConnector(Input):
    def kind(self) -> NodeKind:
        return NodeKind.CONNECTOR

    def generate_input_nodes(self) -> typing.List[Input]:
        return [Input(**self.model_dump(by_alias=True))]


class BaseConnector(VirtualConnector):
    data: ConnectorMetadataModel

    def generate_input_nodes(self) -> typing.List[Input]:
        raise NotImplementedError()

    def run(self, **kwargs):  # Keep the kwargs in the signature
        raise NotImplementedError()
