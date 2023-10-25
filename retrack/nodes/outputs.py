import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, NodeKind
from retrack.utils import constants

################################################
# Output Metadata Models
################################################


class OutputMetadataModel(pydantic.BaseModel):
    message: typing.Optional[str] = None


################################################
# Output Inputs and Outputs
################################################
class OutputInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


################################################
# Output Node
################################################


class Output(BaseNode):
    inputs: typing.Optional[OutputInputsModel]
    data: OutputMetadataModel

    def kind(self) -> NodeKind:
        return NodeKind.OUTPUT

    def run(self, input_value: pd.Series) -> typing.Dict[str, pd.Series]:
        return {
            constants.OUTPUT_REFERENCE_COLUMN: input_value,
            constants.OUTPUT_MESSAGE_REFERENCE_COLUMN: self.data.message,
        }
