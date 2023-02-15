import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# And Or Inputs and Outputs
################################################


class AndOrInputsModel(pydantic.BaseModel):
    input_bool_0: InputConnectionModel
    input_bool_1: InputConnectionModel


class AndOrOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# Not Inputs and Outputs
################################################


class NotInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


class NotOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# And Or Nodes
################################################


class And(BaseNode):
    inputs: AndOrInputsModel
    outputs: AndOrOutputsModel

    def run(self, input_bool_0: pd.Series, input_bool_1: pd.Series) -> pd.Series:
        return {"output_bool": input_bool_0 & input_bool_1}


class Or(BaseNode):
    inputs: AndOrInputsModel
    outputs: AndOrOutputsModel

    def run(self, input_bool_0: pd.Series, input_bool_1: pd.Series) -> pd.Series:
        return {"output_bool": input_bool_0 | input_bool_1}


################################################
# Not Nodes
################################################


class Not(BaseNode):
    inputs: NotInputsModel
    outputs: NotOutputsModel

    def run(self, input_bool: pd.Series) -> pd.Series:
        return {"output_bool": ~input_bool}
