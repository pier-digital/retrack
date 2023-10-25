import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel


class LowerCaseOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class LowerCaseInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class LowerCase(BaseNode):
    inputs: LowerCaseInputsModel
    outputs: LowerCaseOutputsModel

    def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(str).str.lower()}
