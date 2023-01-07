import typing

import pydantic

from retack.models.base import (
    ComponentModel,
    InputConnectionModel,
    OutputConnectionModel,
)


class ConstantMetadataModel(pydantic.BaseModel):
    value: str


class ConstantInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class ConstantOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ConstantModel(ComponentModel):
    data: ConstantMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ConstantOutputsModel


class ListMetadataModel(pydantic.BaseModel):
    value: typing.List[str]


class ListOutputsModel(pydantic.BaseModel):
    output_list: OutputConnectionModel


class ListModel(ComponentModel):
    data: ListMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ListOutputsModel


class BoolMetadataModel(pydantic.BaseModel):
    value: typing.Optional[bool] = pydantic.Field(False, alias="value")

    @pydantic.validator("value")
    def validate_value(cls, value):
        if value is None:
            return False
        return value


class BoolOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


class BoolModel(ComponentModel):
    data: BoolMetadataModel = BoolMetadataModel(value=False)
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: BoolOutputsModel
