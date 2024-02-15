import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

################################################
# IsSubStringOf Inputs Outputs
################################################


class IsSubStringOfInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class IsSubStringOfOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


################################################
# IsSubStringOf Nodes
################################################


class IsSubStringOf(BaseNode):
    inputs: IsSubStringOfInputsModel
    outputs: IsSubStringOfOutputsModel

    def run(self, input_value_0: pd.Series, input_value_1: pd.Series) -> pd.Series:
        tmp_df = pd.DataFrame(
            {"input_value_0": input_value_0, "input_value_1": input_value_1}
        )

        return {
            "output_bool": tmp_df.apply(
                lambda x: x["input_value_0"] in x["input_value_1"], axis=1
            )
        }
