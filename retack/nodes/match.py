import pydantic

from retack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# If Inputs and Outputs
################################################


class IfInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


class IfOutputsModel(pydantic.BaseModel):
    output_then_void: OutputConnectionModel
    output_else_void: OutputConnectionModel


################################################
# If Node
################################################


class If(BaseNode):
    inputs: IfInputsModel
    outputs: IfOutputsModel
