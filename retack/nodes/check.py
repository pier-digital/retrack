import typing

import enum

import pydantic

from retack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# Check Metadata Models
###############################################################


class CheckOperator(str, enum.Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class CheckMetadataModel(pydantic.BaseModel):
    operator: typing.Optional[CheckOperator] = CheckOperator.EQUAL


###############################################################
# Check Inputs and Outputs
###############################################################


class CheckInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class CheckOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


###############################################################
# Check Node
###############################################################


class Check(BaseNode):
    data: CheckMetadataModel
    inputs: CheckInputsModel
    outputs: CheckOutputsModel
