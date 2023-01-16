import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# EndsWith Inputs Outputs
################################################


class EndsWithInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class EndsWithOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# EndsWith Nodes
################################################


class EndsWith(BaseNode):
    inputs: EndsWithInputsModel
    outputs: EndsWithOutputsModel

    def run(self, input_value_0: pd.Series, input_value_1: pd.Series) -> pd.Series:
        return {
            "output_bool": input_value_0.str.endswith(
                input_value_1.to_string(index=False)
            )
        }
