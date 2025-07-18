import datetime as dt
import typing

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

    def run(
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
    format: str = "%Y-%m-%d"


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
        datetime_0 = dt.datetime.strptime(input_value_0.squeeze(), format)
        datetime_1 = (
            dt.datetime.now()
            if input_value_1.squeeze() is None
            else dt.datetime.strptime(input_value_1.squeeze(), format)
        )

        datetime_diff = abs((datetime_0 - datetime_1).days)

        return {"output_value": datetime_diff}
