import typing

import numpy as np
import pandas as pd

from retrack.nodes.base import BaseNode
from retrack.utils import constants, registry
from retrack.engine.schemas import ExecutionSchema
from retrack.utils.transformers import (
    serialize_connections,
    explode_nodes_by_values,
    normalize_execution_for_debug,
    to_metadata,
)


class Execution:
    def __init__(
        self,
        payload: pd.DataFrame,
        states: pd.DataFrame,
        filters: dict = None,
        context: registry.Registry = None,
        nodes: dict = None,
        constants: dict = None,
    ):
        self.payload = payload
        self.states = states
        self.filters = filters or {}
        self.context = context
        self.nodes = nodes or {}
        self.constants = constants or {}

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

    def set_constants_data(self, constants: dict):
        self.constants.update(constants)

    def add_node(self, node: BaseNode):
        self.nodes[node.id] = node

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
        }

    def to_model(self) -> ExecutionSchema:
        return ExecutionSchema(**self.to_dict())

    def to_normalized_dict(self) -> dict:
        nodes_normalized = []
        for node in self.nodes.values():
            nodes_normalized.append(
                {
                    "id": node.id,
                    "name": node.alias(),
                    "type": node.type(),
                    "inputs": serialize_connections(
                        node.inputs,
                        node_id=node.id,
                        connection_type="input",
                        execution=self,
                    ),
                    "outputs": serialize_connections(
                        node.outputs,
                        node_id=node.id,
                        connection_type="output",
                        execution=self,
                    ),
                    "default": node.default(),
                    "data": to_metadata(node),
                }
            )

        exploded_nodes = explode_nodes_by_values(nodes_normalized)
        normalized_records = normalize_execution_for_debug(exploded_nodes)

        return normalized_records

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
