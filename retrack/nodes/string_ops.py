import typing

import pandas as pd
import pydantic

from retrack.nodes.base import (
    BaseNode,
    InputConnectionModel,
    OptionalCastedToNoneStringType,
    OutputConnectionModel,
)

###############################################################
# Helpers
###############################################################


def _check_nulls(node: BaseNode, *input_values: pd.Series) -> None:
    nulls = sum(int(input_value.isna().sum()) for input_value in input_values)
    if nulls:
        raise ValueError(f"{node.name} node {node.id}: received {nulls} null value(s)")


def _empty_string_to_none(value: typing.Any) -> typing.Any:
    if value == "":
        return None
    return value


###############################################################
# String Ops Metadata Models
###############################################################


class ReplaceMetadataModel(pydantic.BaseModel):
    old: str
    new: OptionalCastedToNoneStringType = None

    @pydantic.field_validator("old")
    @classmethod
    def validate_old(cls, value: str) -> str:
        if value == "":
            raise ValueError("old must not be empty")
        return value


class ConcatMetadataModel(pydantic.BaseModel):
    separator: typing.Optional[str] = ""


class SubStringMetadataModel(pydantic.BaseModel):
    """1-based positions, like GetChar. Both start and end are inclusive."""

    start: typing.Optional[int] = None
    end: typing.Optional[int] = None

    @pydantic.field_validator("start", "end", mode="before")
    @classmethod
    def validate_empty(cls, value: typing.Any) -> typing.Any:
        return _empty_string_to_none(value)

    @pydantic.model_validator(mode="after")
    def validate_positions(self) -> "SubStringMetadataModel":
        if self.start is not None and self.start < 1:
            raise ValueError(f"start must be >= 1, got {self.start}")
        if self.end is not None and self.end < 1:
            raise ValueError(f"end must be >= 1, got {self.end}")
        if self.start is not None and self.end is not None and self.end < self.start:
            raise ValueError(
                f"end ({self.end}) must be greater than or equal to start ({self.start})"
            )
        return self


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
        _check_nulls(self, input_value)
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
        _check_nulls(self, input_value)
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
        _check_nulls(self, input_value)
        return {"output_value": input_value.astype(str).str.len()}


###############################################################
# Replace Node
###############################################################


class Replace(BaseNode):
    data: ReplaceMetadataModel
    inputs: SingleValueInputsModel
    outputs: ValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        _check_nulls(self, input_value)
        return {
            "output_value": input_value.astype(str).str.replace(
                self.data.old, self.data.new or "", regex=False
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
        _check_nulls(self, input_value_0, input_value_1)
        separator = self.data.separator if self.data.separator is not None else ""
        return {
            "output_value": input_value_0.astype(str)
            + separator
            + input_value_1.astype(str)
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
        _check_nulls(self, input_value)
        start = self.data.start - 1 if self.data.start is not None else None
        return {"output_value": input_value.astype(str).str[start : self.data.end]}
