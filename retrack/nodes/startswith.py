import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# StartsWith Inputs Outputs
################################################


class StartsWithInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class StartsWithOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# StartsWith Nodes
################################################


class StartsWith(BaseNode):
    inputs: StartsWithInputsModel
    outputs: StartsWithOutputsModel

    def run(self, input_value_0: pd.Series, input_value_1: pd.Series) -> pd.Series:
        return {
            "output_bool": input_value_0.str.startswith(
                input_value_1.to_string(index=False)
            )
        }
