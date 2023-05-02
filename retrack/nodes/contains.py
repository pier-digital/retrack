import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel
from retrack.utils import transformers

################################################
# Contains Inputs Outputs
################################################


class ContainsInputsModel(pydantic.BaseModel):
    input_list: InputConnectionModel
    input_value: InputConnectionModel


class ContainsOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# Contains Nodes
################################################


class Contains(BaseNode):
    inputs: ContainsInputsModel
    outputs: ContainsOutputsModel

    def run(self, input_list: pd.Series, input_value: pd.Series) -> pd.Series:
        return {"output_bool": input_value.isin(transformers.to_list(input_list))}
