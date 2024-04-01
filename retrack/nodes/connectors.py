import typing

from retrack.nodes.base import NodeKind
from retrack.nodes.inputs import Input, InputMetadataModel


class ConnectorMetadataModel(InputMetadataModel):
    service: str
    identifier: str


class BaseConnector(Input):
    data: ConnectorMetadataModel

    def kind(self) -> NodeKind:
        return NodeKind.CONNECTOR

    def generate_input_nodes(self) -> typing.List[Input]:
        return [Input(**self.model_dump(by_alias=True))]
