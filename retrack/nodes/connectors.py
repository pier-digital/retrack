import typing

from retrack.nodes.base import NodeKind
from retrack.nodes.inputs import Input


class VirtualConnector(Input):
    def kind(self) -> NodeKind:
        return NodeKind.INPUT

    def generate_input_nodes(self) -> typing.List[Input]:
        return []


class BaseConnector(VirtualConnector):
    def kind(self) -> NodeKind:
        return NodeKind.CONNECTOR

    def generate_input_nodes(self) -> typing.List[Input]:
        raise NotImplementedError()
