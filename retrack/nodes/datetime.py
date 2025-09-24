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

    def run(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        timezone = gettz(self.data.timezone)
        timezone_0 = pd.to_datetime(input_value_0.squeeze()).tz_localize(timezone)
        timezone_1 = (
            pd.Timestamp.now().normalize().tz_localize(timezone)
            if input_value_1.squeeze() is None
            else pd.to_datetime(input_value_1.squeeze()).tz_localize(timezone)
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
