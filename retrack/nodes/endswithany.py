import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel
from retrack.utils import transformers

################################################
# EndsWithAny Inputs Outputs
################################################


class EndsWithAnyInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel
    input_list: InputConnectionModel


class EndsWithAnyOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# EndsWithAny Nodes
################################################


class EndsWithAny(BaseNode):
    inputs: EndsWithAnyInputsModel
    outputs: EndsWithAnyOutputsModel

    def run(self, input_value: pd.Series, input_list: pd.Series) -> pd.Series:
        input_list = transformers.to_list(input_list)
        return {"output_bool": input_value.str.endswith(tuple(input_list))}
