import typing

import pydantic

from retrack.nodes.base import (
    BaseNode,
    InputConnectionModel,
    NodeKind,
    NodeMemoryType,
    OutputConnectionModel,
)

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


class BaseConstant(BaseNode):
    inputs: typing.Optional[ConstantInputsModel] = None

    def kind(self) -> NodeKind:
        return NodeKind.CONSTANT


class Constant(BaseConstant):
    data: ConstantMetadataModel
    outputs: ConstantOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_value": self.data.value}


class List(BaseConstant):
    data: ListMetadataModel
    outputs: ListOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {}  # {"output_list": self.data.value}

    def memory_type(self) -> NodeMemoryType:
        return NodeMemoryType.CONSTANT


class Bool(BaseConstant):
    data: BoolMetadataModel = BoolMetadataModel(value=False)
    outputs: BoolOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_bool": self.data.value}
