import typing

import pydantic

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

    @property
    def node_type(self) -> str:
        raise NotImplementedError
