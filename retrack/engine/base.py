import pydantic
import typing
import pandas as pd
import numpy as np
from retrack.utils import constants


class RuleMetadata(pydantic.BaseModel):
    name: typing.Optional[str] = None
    version: str


class Execution:
    def __init__(self, states: pd.DataFrame, filters: dict = None):
        self.states = states
        self.filters = filters or {}

    def set_state_data(
        self, column: str, value: typing.Any, filter_by: typing.Any = None
    ):
        if filter_by is None:
            self.states[column] = value
        else:
            self.states.loc[filter_by, column] = value

    def get_state_data(
        self, column: str, constants: dict, filter_by: typing.Any = None
    ):
        if column in constants:
            return constants[column]

        if filter_by is None:
            return self.states[column]

        return self.states.loc[filter_by, column]

    def update_filters(self, filter_value, output_connections: typing.List[str] = None):
        for output_connection_id in output_connections:
            if self.filters.get(output_connection_id, None) is None:
                self.filters[output_connection_id] = filter_value
            else:
                self.filters[output_connection_id] = (
                    self.filters[output_connection_id] & filter_value
                )

    @classmethod
    def from_payload(cls, validated_payload: pd.DataFrame, input_columns: dict):
        state_df = pd.DataFrame([])
        for node_id, input_name in input_columns.items():
            state_df[node_id] = validated_payload[input_name]

        state_df[constants.OUTPUT_REFERENCE_COLUMN] = np.nan
        state_df[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] = np.nan

        return cls(state_df)
