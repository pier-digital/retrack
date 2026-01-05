import datetime as dt
import typing
from dateutil.tz import gettz

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, InputConnectionModel, OutputConnectionModel

###############################################################
# CurrentYear Inputs and Outputs
###############################################################


class CurrentYearInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class CurrentYearOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


###############################################################
# CurrentYear Node
###############################################################


class CurrentYear(BaseNode):
    inputs: CurrentYearInputsModel
    outputs: CurrentYearOutputsModel

    async def run(
        self,
        input_void: typing.Optional[pd.Series] = None,
    ) -> typing.Dict[str, str]:
        return {"output_value": dt.datetime.now().year}


###############################################################
# DifferenceBetweenDates Inputs and Outputs
###############################################################


class DifferenceBetweenDatesOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class DifferenceBetweenDatesInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: typing.Optional[InputConnectionModel] = None


class DifferenceBetweenDatesMetadataModel(pydantic.BaseModel):
    timezone: typing.Optional[str] = "America/Sao_Paulo"


###############################################################
# DifferenceBetweenDates Node
###############################################################


class DifferenceBetweenDates(BaseNode):
    inputs: DifferenceBetweenDatesInputsModel
    outputs: DifferenceBetweenDatesOutputsModel
    data: DifferenceBetweenDatesMetadataModel

    async def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        timezone = gettz(self.data.timezone)

        def replace_invalid(value):
            if pd.isna(value):
                return pd.Timestamp.now(tz=timezone)
            timestamp = pd.to_datetime(value)
            if timestamp.tzinfo is None:
                return (
                    timestamp.tz_localize(
                        timezone, ambiguous="NaT", nonexistent="shift_forward"
                    )
                )
            return timestamp.tz_convert(timezone)

        timestamp_0 = input_value_0.apply(replace_invalid)
        timestamp_1 = input_value_1.apply(replace_invalid)

        differences = timestamp_1.sub(timestamp_0)

        if differences.empty:
            return {"output_value": pd.Series()}
        
        days = differences.dt.days

        return {"output_value": days}


###############################################################
# Now Inputs and Outputs
###############################################################


class NowOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class NowInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class NowMetadataModel(pydantic.BaseModel):
    timezone: typing.Optional[str] = "America/Sao_Paulo"


###############################################################
# Now Node
###############################################################


class Now(BaseNode):
    inputs: NowInputsModel
    outputs: NowOutputsModel
    data: NowMetadataModel

    async def run(
        self,
        input_void: typing.Optional[pd.Series] = None,
    ) -> typing.Dict[str, str]:
        timezone = gettz(self.data.timezone)
        date = dt.datetime.now(tz=timezone).replace(microsecond=0)
        return {"output_value": pd.Series([date.isoformat()])}


###############################################################
# ToISOFormat Inputs and Outputs
###############################################################


class ToISOFormatOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ToISOFormatInputsModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class ToISOFormatMetadataModel(pydantic.BaseModel):
    format: typing.Optional[str] = "%Y-%m-%d"
    timezone: typing.Optional[str] = "America/Sao_Paulo"


###############################################################
# ToISOFormat Node
###############################################################


class ToISOFormat(BaseNode):
    inputs: ToISOFormatInputsModel
    outputs: ToISOFormatOutputsModel
    data: ToISOFormatMetadataModel

    async def run(
        self,
        input_value: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        format = self.data.format or "%Y-%m-%d"
        format = format.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
        timezone = gettz(self.data.timezone)

        def convert_to_iso(value):
            timestamp = pd.to_datetime(value)
            if timestamp.tzinfo is None:
                return (
                    timestamp.tz_localize(
                        timezone, ambiguous="NaT", nonexistent="shift_forward"
                    )
                    .isoformat()
                )
            return timestamp.tz_convert(timezone).isoformat()

        output_series = input_value.apply(convert_to_iso)
        return {"output_value": output_series}
