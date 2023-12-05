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
