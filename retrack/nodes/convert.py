import math
import numbers
import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# Helpers
###############################################################

_TRUE_VALUES = {"true", "1", "yes", "y", "t"}
_FALSE_VALUES = {"false", "0", "no", "n", "f"}

MAX_INVALID_SAMPLES = 5


def _parse_bool(value: typing.Any) -> typing.Optional[bool]:
    """Returns the bool for value, or None when it is not a recognized bool."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, numbers.Number):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
    return None


def _samples(values: pd.Series) -> list:
    return values.head(MAX_INVALID_SAMPLES).tolist()


def _check_nulls(node: BaseNode, nulls: pd.Series) -> None:
    if nulls.any() and node.data.default is None:
        raise ValueError(
            f"{node.name} node {node.id}: received {int(nulls.sum())} null value(s) "
            "and no default is configured"
        )


def _fill_nulls(
    converted: pd.Series, nulls: pd.Series, default: typing.Any
) -> pd.Series:
    output = pd.Series(default, index=converted.index, dtype=object)
    output[~nulls] = converted[~nulls]
    return output


def _empty_string_to_none(value: typing.Any) -> typing.Any:
    if value == "":
        return None
    return value


###############################################################
# Convert Metadata Models
###############################################################


class ToBoolMetadataModel(pydantic.BaseModel):
    default: typing.Optional[bool] = None

    @pydantic.field_validator("default", mode="before")
    @classmethod
    def validate_default(cls, value: typing.Any) -> typing.Optional[bool]:
        value = _empty_string_to_none(value)
        if value is None:
            return None
        parsed = _parse_bool(value)
        if parsed is None:
            raise ValueError(f"default {value!r} is not a valid bool")
        return parsed


class ToNumberMetadataModel(pydantic.BaseModel):
    default: typing.Optional[float] = None

    @pydantic.field_validator("default", mode="before")
    @classmethod
    def validate_default(cls, value: typing.Any) -> typing.Optional[float]:
        value = _empty_string_to_none(value)
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError(f"default {value!r} is not a valid number")
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"default {value!r} is not a valid number")
        if not math.isfinite(parsed):
            raise ValueError(f"default {value!r} is not a finite number")
        return parsed


class ToStringMetadataModel(pydantic.BaseModel):
    default: typing.Optional[str] = None

    @pydantic.field_validator("default", mode="before")
    @classmethod
    def validate_default(cls, value: typing.Any) -> typing.Optional[str]:
        value = _empty_string_to_none(value)
        if value is None:
            return None
        return str(value)


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
# ToBool Node
###############################################################


class ToBool(BaseNode):
    data: ToBoolMetadataModel = ToBoolMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertBoolOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        nulls = input_value.isna()
        _check_nulls(self, nulls)

        converted = input_value.apply(_parse_bool)
        invalid = converted.isna() & ~nulls
        if invalid.any():
            raise ValueError(
                f"{self.name} node {self.id}: could not convert "
                f"{_samples(input_value[invalid])} to bool"
            )

        output = _fill_nulls(converted, nulls, self.data.default)

        return {"output_bool": output.astype(bool)}


###############################################################
# ToNumber Node
###############################################################


class ToNumber(BaseNode):
    data: ToNumberMetadataModel = ToNumberMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        nulls = input_value.isna()
        _check_nulls(self, nulls)

        is_bool = input_value.apply(lambda value: isinstance(value, (bool, np.bool_)))
        converted = pd.to_numeric(input_value.where(~is_bool), errors="coerce")
        invalid = ~nulls & (converted.isna() | ~np.isfinite(converted))
        if invalid.any():
            raise ValueError(
                f"{self.name} node {self.id}: could not convert "
                f"{_samples(input_value[invalid])} to number"
            )

        output = _fill_nulls(converted, nulls, self.data.default)

        return {"output_value": output.astype(float)}


###############################################################
# ToString Node
###############################################################


class ToString(BaseNode):
    data: ToStringMetadataModel = ToStringMetadataModel()
    inputs: ConvertInputsModel
    outputs: ConvertValueOutputsModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        nulls = input_value.isna()
        _check_nulls(self, nulls)

        output = _fill_nulls(input_value.astype(str), nulls, self.data.default)

        return {"output_value": output.astype(str)}
