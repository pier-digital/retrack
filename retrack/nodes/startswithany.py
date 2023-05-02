import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel
from retrack.utils import transformers

################################################
# StartsWithAny Inputs Outputs
################################################


class StartsWithAnyInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel
    input_list: InputConnectionModel


class StartsWithAnyOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# StartsWithAny Nodes
################################################


class StartsWithAny(BaseNode):
    inputs: StartsWithAnyInputsModel
    outputs: StartsWithAnyOutputsModel

    def run(self, input_value: pd.Series, input_list: pd.Series) -> pd.Series:
        input_list = transformers.to_list(input_list)
        return {"output_bool": input_value.str.startswith(tuple(input_list))}
