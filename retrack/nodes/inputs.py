import typing

import pydantic

from retrack.nodes.base import (
    BaseNode,
    InputConnectionModel,
    NodeKind,
    OutputConnectionModel,
)

################################################
# Input Metadata Models
################################################


class InputMetadataModel(pydantic.BaseModel):
    name: str
    default: typing.Optional[str] = None


################################################
# Input Inputs and Outputs
################################################


class InputInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class InputOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


################################################
# Input Node
################################################


class Input(BaseNode):
    data: InputMetadataModel
    inputs: typing.Optional[InputInputsModel] = None
    outputs: InputOutputsModel

    def kind(self) -> NodeKind:
        return NodeKind.INPUT
