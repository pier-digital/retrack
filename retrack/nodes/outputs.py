import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, NodeKind
from retrack.utils import constants

################################################
# Output Metadata Models
################################################


class OutputMetadataModel(pydantic.BaseModel):
    message: str = None


################################################
# Output Inputs and Outputs
################################################
class BoolOutputInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


################################################
# Output Node
################################################


class BoolOutput(BaseNode):
    inputs: typing.Optional[BoolOutputInputsModel]
    data: OutputMetadataModel

    def kind(self) -> NodeKind:
        return NodeKind.OUTPUT

    def run(self, input_bool: pd.Series) -> typing.Dict[str, pd.Series]:
        return {
            constants.OUTPUT_REFERENCE_COLUMN: input_bool,
            constants.OUTPUT_MESSAGE_REFERENCE_COLUMN: self.data.message,
        }
