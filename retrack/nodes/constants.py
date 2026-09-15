import io
import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.nodes.base import (
    BaseNode,
    InputConnectionModel,
    NodeKind,
    NodeMemoryType,
    OutputConnectionModel,
)

#######################################################
# Constant Metadata Models
#######################################################


class ConstantMetadataModel(pydantic.BaseModel):
    value: str
    name: typing.Optional[str] = None


class ListMetadataModel(pydantic.BaseModel):
    value: typing.List[str]


class BoolMetadataModel(pydantic.BaseModel):
    value: typing.Optional[bool] = pydantic.Field(False, alias="value")

    @pydantic.field_validator("value")
    def validate_value(cls, value):
        if value is None:
            return False

        value = str(value).lower()

        if value in ["true", "1", "yes", "y", "t"]:
            return True

        return False


class IntervalCatMetadataModel(pydantic.BaseModel):
    value: typing.List[str]
    start_interval_column: str
    end_interval_column: str
    category_column: str
    headers: typing.List[str]
    separator: typing.Optional[str] = pydantic.Field(",")
    default: typing.Optional[str] = None

    def df(self) -> pd.DataFrame:
        csv_str = "\n".join(self.value[1:])
        buffer = io.StringIO(csv_str)

        df = pd.read_csv(
            buffer,
            header=None,
            names=self.headers,
            sep=self.separator,
            dtype={
                self.start_interval_column: "float64",
                self.end_interval_column: "float64",
            },
        )

        return df


#######################################################
# Constant Inputs and Outputs
#######################################################


class ConstantInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class ConstantInputsValueModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class ConstantOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ListOutputsModel(pydantic.BaseModel):
    output_list: OutputConnectionModel


class BoolOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


#######################################################
# Constant Nodes
#######################################################


class BaseConstant(BaseNode):
    inputs: typing.Optional[ConstantInputsModel] = None

    def kind(self) -> NodeKind:
        return NodeKind.CONSTANT


class Constant(BaseConstant):
    data: ConstantMetadataModel
    outputs: ConstantOutputsModel

    async def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_value": self.data.value}


class List(BaseConstant):
    data: ListMetadataModel
    outputs: ListOutputsModel

    async def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {}  # {"output_list": self.data.value}

    def memory_type(self) -> NodeMemoryType:
        return NodeMemoryType.CONSTANT


class Bool(BaseConstant):
    data: BoolMetadataModel = BoolMetadataModel(value=False)
    outputs: BoolOutputsModel

    async def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_bool": self.data.value}


class IntervalCatV0(BaseConstant):
    data: IntervalCatMetadataModel
    inputs: ConstantInputsValueModel
    outputs: ConstantOutputsModel

    async def run(self, input_value: pd.Series) -> typing.Dict[str, typing.Any]:
        values = pd.to_numeric(input_value, errors="coerce").to_numpy()

        df = self.data.df()
        starts = pd.to_numeric(
            df[self.data.start_interval_column], errors="coerce"
        ).to_numpy()
        ends = pd.to_numeric(
            df[self.data.end_interval_column], errors="coerce"
        ).to_numpy()
        cats_s = df[self.data.category_column]
        intervals = pd.IntervalIndex.from_arrays(starts, ends, closed="left")
        idx = intervals.get_indexer(values)
        cats = cats_s.to_numpy(dtype=object)
        out = np.full(values.shape, np.nan, dtype=object)

        found_mask = idx != -1
        if found_mask.any():
            mapped = cats[idx[found_mask]]
            out[found_mask] = mapped

            pass_mask = mapped == "{value}"
            if pass_mask.any():
                ii = np.where(found_mask)[0][pass_mask]
                out[ii] = input_value.iloc[ii]

        if self.data.default is not None:
            nan_mask = pd.isna(out)
            if nan_mask.any():
                out[nan_mask] = self.data.default

        output = pd.Series(out, index=input_value.index, dtype="object")

        return {"output_value": output}
