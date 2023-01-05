import typing

import pydantic


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
