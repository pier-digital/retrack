import typing

import pydantic

from retack.models.base import InputConnectionModel, OutputConnectionModel


class InputMetadataModel(pydantic.BaseModel):
    name: str
    default: typing.Optional[str] = None


class InputInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class InputOutputsModel(pydantic.BaseModel):
    output_0: OutputConnectionModel


class InputModel(pydantic.BaseModel):
    id: str
    data: InputMetadataModel
    inputs: typing.Optional[InputInputsModel] = None
    outputs: InputOutputsModel
