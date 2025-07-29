import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel


class ConcatOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ConcatInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class ConcatMetadataModel(pydantic.BaseModel):
    separator: str = ""


class Concat(BaseNode):
    inputs: ConcatInputsModel
    outputs: ConcatOutputsModel
    data: ConcatMetadataModel

    def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": self.data.separator.join(input_value_0 + input_value_1)}
