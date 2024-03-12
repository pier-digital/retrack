import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel


class GetCharOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class GetCharInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class GetCharMetadataModel(pydantic.BaseModel):
    index: int


class GetChar(BaseNode):
    inputs: GetCharInputsModel
    outputs: GetCharOutputsModel
    data: GetCharMetadataModel

    def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.apply(lambda x: str(x)[self.data.index - 1])}
