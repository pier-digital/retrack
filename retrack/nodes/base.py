import typing

import enum

import pydantic

###############################################################
# Node Kind
###############################################################


class NodeKind(str, enum.Enum):
    INPUT = "input"
    CONSTANT = "constant"
    OUTPUT = "output"
    FILTER = "filter"
    CONNECTOR = "connector"
    START = "start"
    OTHER = "other"


###############################################################
# Node Memory Types
###############################################################


class NodeMemoryType(str, enum.Enum):
    STATE = "state"
    FILTER = "filter"
    CONSTANT = "constant"


###############################################################
# Connection Models
###############################################################


class OutputConnectionItemModel(pydantic.BaseModel):
    node: str
    input_: str = pydantic.Field(alias="input")


class InputConnectionItemModel(pydantic.BaseModel):
    node: str
    output: str = pydantic.Field(alias="output")


class OutputConnectionModel(pydantic.BaseModel):
    connections: typing.List[OutputConnectionItemModel]


class InputConnectionModel(pydantic.BaseModel):
    connections: typing.List[InputConnectionItemModel]


###############################################################
# Base Node
###############################################################


class BaseNode(pydantic.BaseModel):
    id: str
    inputs: typing.Optional[typing.Dict[str, InputConnectionModel]] = None
    outputs: typing.Optional[typing.Dict[str, OutputConnectionModel]] = None

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {}

    def kind(self) -> NodeKind:
        return NodeKind.OTHER

    def memory_type(self) -> NodeMemoryType:
        return NodeMemoryType.STATE
