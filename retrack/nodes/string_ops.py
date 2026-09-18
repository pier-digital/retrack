import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# String Ops Metadata Models
###############################################################


class ReplaceMetadataModel(pydantic.BaseModel):
    old: str = ""
    new: str = ""


class ConcatMetadataModel(pydantic.BaseModel):
    separator: typing.Optional[str] = ""


class SubStringMetadataModel(pydantic.BaseModel):
    start: int = 0
    end: typing.Optional[int] = None


###############################################################
# Shared Inputs / Outputs
###############################################################


class SingleValueInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class TwoValueInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class ValueOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


###############################################################
# UpperCase Node
###############################################################


class UpperCase(BaseNode):
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(str).str.upper()}


###############################################################
# Trim Node
###############################################################


class Trim(BaseNode):
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(str).str.strip()}


###############################################################
# Length Node
###############################################################


class Length(BaseNode):
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(str).str.len()}


###############################################################
# Replace Node
###############################################################


class Replace(BaseNode):
    data: ReplaceMetadataModel = ReplaceMetadataModel()
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {
            "output_value": input_value.astype(str).str.replace(
                self.data.old, self.data.new, regex=False
            )
        }


###############################################################
# Concat Node
###############################################################


class Concat(BaseNode):
    data: ConcatMetadataModel = ConcatMetadataModel()
    inputs: TwoValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        separator = self.data.separator if self.data.separator is not None else ""
        return {
            "output_value": input_value_0.astype(str) + separator + input_value_1.astype(str)
        }


###############################################################
# SubString Node
###############################################################


class SubString(BaseNode):
    data: SubStringMetadataModel = SubStringMetadataModel()
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {
            "output_value": input_value.astype(str).str[self.data.start : self.data.end]
        }
