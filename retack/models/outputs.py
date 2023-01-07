import typing

import pydantic

from retack.models.base import ComponentModel, InputConnectionModel


class BoolOutputInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


class OutputMetadataModel(pydantic.BaseModel):
    message: str = None


class BoolOutputModel(ComponentModel):
    inputs: typing.Optional[BoolOutputInputsModel]
    data: OutputMetadataModel
