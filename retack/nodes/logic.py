import pandas as pd
import pydantic

from retack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# Logic Inputs and Outputs
################################################


class AndInputsModel(pydantic.BaseModel):
    input_bool_0: InputConnectionModel
    input_bool_1: InputConnectionModel


class AndOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# Logic Nodes
################################################


class And(BaseNode):
    inputs: AndInputsModel
    outputs: AndOutputsModel

    def run(self, input_bool_0: pd.Series, input_bool_1: pd.Series) -> pd.Series:
        return {"output_bool": input_bool_0 & input_bool_1}
