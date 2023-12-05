import enum
import typing

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
    FLOW = "flow"


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


def cast_int_to_str(v: typing.Any, info: pydantic.ValidationInfo) -> str:
    return str(v)


CastedToStringType = typing.Annotated[
    typing.Any, pydantic.BeforeValidator(cast_int_to_str)
]


class OutputConnectionItemModel(pydantic.BaseModel):
    node: CastedToStringType
    input_: str = pydantic.Field(alias="input")


class InputConnectionItemModel(pydantic.BaseModel):
    node: CastedToStringType
    output: str = pydantic.Field(alias="output")


class OutputConnectionModel(pydantic.BaseModel):
    connections: typing.List[OutputConnectionItemModel]


class InputConnectionModel(pydantic.BaseModel):
    connections: typing.List[InputConnectionItemModel]


###############################################################
# Base Node
###############################################################


class BaseNode(pydantic.BaseModel):
    id: CastedToStringType
    inputs: typing.Optional[
        typing.Dict[CastedToStringType, InputConnectionModel]
    ] = None
    outputs: typing.Optional[
        typing.Dict[CastedToStringType, OutputConnectionModel]
    ] = None

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {}

    def kind(self) -> NodeKind:
        return NodeKind.OTHER

    def memory_type(self) -> NodeMemoryType:
        return NodeMemoryType.STATE

    def generate_input_nodes(self) -> typing.List["BaseNode"]:
        return []
