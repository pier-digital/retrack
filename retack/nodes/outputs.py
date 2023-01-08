import typing

import pydantic

from retack.nodes.base import BaseNode, InputConnectionModel

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
