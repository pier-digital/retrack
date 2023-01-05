import typing

import pydantic

from retack.models.base import InputConnectionModel, OutputConnectionModel


class ConstantMetadataModel(pydantic.BaseModel):
    value: str


class ConstantInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class ConstantOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ConstantModel(pydantic.BaseModel):
    id: str
    data: ConstantMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ConstantOutputsModel


class ListMetadataModel(pydantic.BaseModel):
    value: typing.List[str]


class ListOutputsModel(pydantic.BaseModel):
    output_list: OutputConnectionModel


class ListModel(pydantic.BaseModel):
    id: str
    data: ListMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ListOutputsModel
