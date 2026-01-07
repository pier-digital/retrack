import typing

import numpy as np
import pandas as pd

from retrack.utils import constants, registry
from retrack.engine.schemas import ExecutionSchema
from retrack.utils.transformers import to_normalized_dict


class Execution:
    def __init__(
        self,
        payload: pd.DataFrame,
        states: pd.DataFrame,
        filters: dict = None,
        context: registry.Registry = None,
        child_executions: dict = None,
        aliases: dict = None,
    ):
        self.payload = payload
        self.states = states
        self.filters = filters or {}
        self.child_executions = child_executions or {}
        self.context = context
        self.aliases = aliases or {}

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

    def add_alias(self, node_id: str, alias: str):
        self.aliases[node_id] = alias

    def add_child_execution(self, node_id: str, execution: "Execution"):
        if node_id not in self.child_executions:
            self.child_executions[node_id] = []
        self.child_executions[node_id].append(execution)

    def update_filters(self, filter_value, output_connections: typing.List[str] = None):
        for output_connection_id in output_connections:
            if self.filters.get(output_connection_id, None) is None:
                self.filters[output_connection_id] = filter_value
            else:
                self.filters[output_connection_id] = (
                    self.filters[output_connection_id] & filter_value
                )

    @classmethod
    def from_payload(
        cls,
        validated_payload: pd.DataFrame,
        input_columns: dict,
        context: registry.Registry = None,
    ):
        state_df = pd.DataFrame([])
        for node_id, input_name in input_columns.items():
            state_df[node_id] = validated_payload[input_name].copy()

        state_df[constants.OUTPUT_REFERENCE_COLUMN] = np.nan
        state_df[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] = np.nan

        return cls(
            payload=validated_payload,
            states=state_df,
            context=context,
        )

    @property
    def result(self) -> pd.DataFrame:
        return self.states[
            [
                constants.OUTPUT_REFERENCE_COLUMN,
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN,
            ]
        ]

    def has_ended(self) -> bool:
        return self.states[constants.OUTPUT_REFERENCE_COLUMN].isna().sum() == 0

    def to_dict(self) -> dict:
        return {
            "payload": self.payload.to_dict(),
            "states": self.states.to_dict(),
            "filters": {k: v.to_dict() for k, v in self.filters.items()},
            "result": self.result.to_dict(),
            "has_ended": self.has_ended(),
            "child_executions": {
                k: [ce.to_dict() for ce in v] for k, v in self.child_executions.items()
            },
        }

    def to_model(self) -> ExecutionSchema:
        return ExecutionSchema(**self.to_dict())

    def to_normalized_dict(self) -> dict:
        inputs = to_normalized_dict(df=self.payload, key_name="name")

        filtered_states = self.states.drop(
            [
                constants.OUTPUT_REFERENCE_COLUMN,
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN,
            ],
            axis=1,
            errors="ignore",
        )
        outputs = [
            {
                "node_id": k.split("@")[0],
                "alias": self.aliases.get(k.split("@")[0]),
                "values": list(v.values()),
            }
            for k, v in filtered_states.to_dict(orient="dict").items()
        ]
        child_executions = [
            {
                "node_id": node_id,
                "executions": [
                    execution.to_normalized_dict() for execution in executions
                ],
            }
            for node_id, executions in getattr(self, "child_executions", {}).items()
        ]
        results = to_normalized_dict(df=self.result, key_name="name")

        return {
            "inputs": inputs,
            "outputs": outputs,
            "executions": child_executions,
            "results": results,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            payload=pd.DataFrame(data["payload"]),
            states=pd.DataFrame(data["states"]),
            filters={k: pd.DataFrame(v) for k, v in data["filters"].items()},
        )

    def __repr__(self) -> str:
        return f"Execution({self.to_dict()})"

    def __str__(self) -> str:
        return self.__repr__()
