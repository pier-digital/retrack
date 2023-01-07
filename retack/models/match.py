import typing

import pydantic

from retack.models.base import (
    ComponentModel,
    InputConnectionModel,
    OutputConnectionModel,
)


class IfInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


class IfOutputsModel(pydantic.BaseModel):
    output_then_void: OutputConnectionModel
    output_else_void: OutputConnectionModel


class IfModel(ComponentModel):
    inputs: IfInputsModel
    outputs: IfOutputsModel
