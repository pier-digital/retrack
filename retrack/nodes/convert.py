import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# Convert Metadata Models
###############################################################


class ConvertMetadataModel(pydantic.BaseModel):
    default: typing.Optional[str] = None


###############################################################
# Convert Inputs and Outputs
###############################################################


class ConvertInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class ConvertBoolOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


class ConvertValueOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


###############################################################
# Helpers
###############################################################

_TRUE_VALUES = {"true", "1", "yes", "y", "t"}


def _to_bool(value: typing.Any) -> bool:
    if pd.isna(value):
        return False
    return str(value).lower() in _TRUE_VALUES


###############################################################
# ToBool Node
###############################################################


class ToBool(BaseNode):
    data: ConvertMetadataModel = ConvertMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertBoolOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        default = _to_bool(self.data.default) if self.data.default is not None else False

        output = input_value.apply(
            lambda value: _to_bool(value) if not pd.isna(value) else default
        )

        return {"output_bool": output.astype(bool)}


###############################################################
# ToNumber Node
###############################################################


class ToNumber(BaseNode):
    data: ConvertMetadataModel = ConvertMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        default = pd.to_numeric(self.data.default, errors="coerce")
        if pd.isna(default):
            default = 0

        output = pd.to_numeric(input_value, errors="coerce").fillna(default)

        return {"output_value": output}


###############################################################
# ToString Node
###############################################################


class ToString(BaseNode):
    data: ConvertMetadataModel = ConvertMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        default = self.data.default if self.data.default is not None else ""

        output = input_value.apply(
            lambda value: str(value) if not pd.isna(value) else default
        )

        return {"output_value": output.astype(str)}
