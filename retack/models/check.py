import typing

import enum

import pydantic

from retack.models.base import InputConnectionModel, OutputConnectionModel


class CheckOperator(str, enum.Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class CheckMetadataModel(pydantic.BaseModel):
    operator: typing.Optional[CheckOperator] = CheckOperator.EQUAL


class CheckInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class CheckOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


class CheckModel(pydantic.BaseModel):
    id: str
    data: CheckMetadataModel
    inputs: CheckInputsModel
    outputs: CheckOutputsModel
