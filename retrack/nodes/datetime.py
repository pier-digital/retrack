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
# DaysBetweenDates Inputs and Outputs
###############################################################


class DaysBetweenDatesOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class DaysBetweenDatesInputsModel(pydantic.BaseModel):
    input_value_0: InputConnectionModel
    input_value_1: typing.Optional[InputConnectionModel] = None


class DaysBetweenDatesMetadataModel(pydantic.BaseModel):
    format: typing.Optional[str] = "%Y-%m-%d"
    timezone: typing.Optional[str] = "America/Sao_Paulo"


###############################################################
# DaysBetweenDates Node
###############################################################


class DaysBetweenDates(BaseNode):
    inputs: DaysBetweenDatesInputsModel
    outputs: DaysBetweenDatesOutputsModel
    data: DaysBetweenDatesMetadataModel

    def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        format = self.data.format
        timezone = gettz(self.data.timezone)
        timezone_0 = (
            pd.Timestamp(input_value_0.squeeze(), tz=timezone)
            if isinstance(input_value_0.squeeze(), (dt.datetime, pd.Timestamp))
            else pd.Timestamp(
                dt.datetime.strptime(input_value_0.squeeze(), format), tz=timezone
            )
        )
        timezone_1 = (
            pd.Timestamp.now().normalize().tz_localize(timezone)
            if input_value_1.squeeze() is None
            else pd.Timestamp(input_value_1.squeeze(), tz=timezone)
            if isinstance(input_value_1.squeeze(), (dt.datetime, pd.Timestamp))
            else pd.Timestamp(
                dt.datetime.strptime(input_value_1.squeeze(), format), tz=timezone
            )
        )
        days = abs((timezone_0 - timezone_1).days)

        return {"output_value": pd.Series([days])}


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

    def run(
        self,
        input_void: typing.Optional[pd.Series] = None,
    ) -> typing.Dict[str, str]:
        timezone = gettz(self.data.timezone)
        timestamp = dt.datetime.now(tz=timezone).isoformat()
        return {"output_value": timestamp}
