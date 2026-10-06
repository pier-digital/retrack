import enum
import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# Helpers
###############################################################

MAX_INVALID_SAMPLES = 5


def _to_float(node: BaseNode, input_value: pd.Series) -> pd.Series:
    nulls = input_value.isna()
    if nulls.any():
        raise ValueError(
            f"{node.name} node {node.id}: received {int(nulls.sum())} null value(s)"
        )

    converted = pd.to_numeric(input_value, errors="coerce").astype(float)
    invalid = converted.isna() | ~np.isfinite(converted)
    if invalid.any():
        raise ValueError(
            f"{node.name} node {node.id}: could not convert "
            f"{input_value[invalid].head(MAX_INVALID_SAMPLES).tolist()} to number"
        )

    return converted


def _check_finite(node: BaseNode, output: pd.Series) -> pd.Series:
    invalid = ~np.isfinite(output)
    if invalid.any():
        raise ValueError(
            f"{node.name} node {node.id}: operator {node.data.operator.value} "
            f"produced {int(invalid.sum())} non-finite value(s) (NaN or infinity)"
        )
    return output


###############################################################
# Math Metadata Models
###############################################################


class MathOperator(str, enum.Enum):
    SUM = "+"
    SUB = "-"
    DIVISION = "/"
    MULTIPLY = "*"
    POWER = "**"
    MODULO = "%"


class MathMetadataModel(pydantic.BaseModel):
    operator: typing.Optional[MathOperator] = MathOperator.SUM


###############################################################
# Math Inputs and Outputs
###############################################################


class MathInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: InputConnectionModel


class MathOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


###############################################################
# Math Node
###############################################################


class Math(BaseNode):
    data: MathMetadataModel
    inputs: MathInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        if self.data.operator == MathOperator.SUM:
            return {
                "output_value": input_value_0.astype(float)
                + input_value_1.astype(float)
            }
        elif self.data.operator == MathOperator.SUB:
            return {
                "output_value": input_value_0.astype(float)
                - input_value_1.astype(float)
            }
        elif self.data.operator == MathOperator.MULTIPLY:
            return {
                "output_value": input_value_0.astype(float)
                * input_value_1.astype(float)
            }
        elif self.data.operator == MathOperator.DIVISION:
            return {
                "output_value": input_value_0.astype(float)
                / input_value_1.astype(float)
            }
        elif self.data.operator == MathOperator.POWER:
            output = _to_float(self, input_value_0) ** _to_float(self, input_value_1)
            return {"output_value": _check_finite(self, output)}
        elif self.data.operator == MathOperator.MODULO:
            output = _to_float(self, input_value_0) % _to_float(self, input_value_1)
            return {"output_value": _check_finite(self, output)}
        else:
            raise ValueError("Unknown operator")


###############################################################
# Absolute Value Node
###############################################################


class AbsoluteValueInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class AbsoluteValue(BaseNode):
    inputs: AbsoluteValueInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(float).abs()}


###############################################################
# Round Node
###############################################################


class Round(BaseNode):
    inputs: AbsoluteValueInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": input_value.astype(float).round(0).astype(int)}


###############################################################
# Floor Node
###############################################################


class Floor(BaseNode):
    inputs: AbsoluteValueInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": np.floor(_to_float(self, input_value)).astype(int)}


###############################################################
# Ceil Node
###############################################################


class Ceil(BaseNode):
    inputs: AbsoluteValueInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {"output_value": np.ceil(_to_float(self, input_value)).astype(int)}


###############################################################
# Min Node
###############################################################


class Min(BaseNode):
    inputs: MathInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {
            "output_value": np.minimum(
                _to_float(self, input_value_0), _to_float(self, input_value_1)
            )
        }


###############################################################
# Max Node
###############################################################


class Max(BaseNode):
    inputs: MathInputsModel
    outputs: MathOutputsModel

    async def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        return {
            "output_value": np.maximum(
                _to_float(self, input_value_0), _to_float(self, input_value_1)
            )
        }
