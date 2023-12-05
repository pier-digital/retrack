import enum
import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

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

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return self.value


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

    def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        if self.data.operator == CheckOperator.EQUAL:
            return {
                "output_bool": input_value_0.astype(str) == input_value_1.astype(str)
            }
        elif self.data.operator == CheckOperator.NOT_EQUAL:
            return {
                "output_bool": input_value_0.astype(str) != input_value_1.astype(str)
            }
        elif self.data.operator == CheckOperator.GREATER_THAN:
            return {
                "output_bool": input_value_0.astype(float) > input_value_1.astype(float)
            }
        elif self.data.operator == CheckOperator.LESS_THAN:
            return {
                "output_bool": input_value_0.astype(float) < input_value_1.astype(float)
            }
        elif self.data.operator == CheckOperator.GREATER_THAN_OR_EQUAL:
            return {
                "output_bool": input_value_0.astype(float)
                >= input_value_1.astype(float)
            }
        elif self.data.operator == CheckOperator.LESS_THAN_OR_EQUAL:
            return {
                "output_bool": input_value_0.astype(float)
                <= input_value_1.astype(float)
            }
        else:
            raise ValueError("Unknown operator")
