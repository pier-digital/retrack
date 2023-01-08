import typing

import pydantic

from retack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

#######################################################
# Constant Metadata Models
#######################################################


class ConstantMetadataModel(pydantic.BaseModel):
    value: str


class ListMetadataModel(pydantic.BaseModel):
    value: typing.List[str]


class BoolMetadataModel(pydantic.BaseModel):
    value: typing.Optional[bool] = pydantic.Field(False, alias="value")

    @pydantic.validator("value")
    def validate_value(cls, value):
        if value is None:
            return False
        return value


#######################################################
# Constant Inputs and Outputs
#######################################################


class ConstantInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class ConstantOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ListOutputsModel(pydantic.BaseModel):
    output_list: OutputConnectionModel


class BoolOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


#######################################################
# Constant Nodes
#######################################################


class Constant(BaseNode):
    data: ConstantMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ConstantOutputsModel


class List(BaseNode):
    data: ListMetadataModel
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: ListOutputsModel


class Bool(BaseNode):
    data: BoolMetadataModel = BoolMetadataModel(value=False)
    inputs: typing.Optional[ConstantInputsModel] = None
    outputs: BoolOutputsModel
