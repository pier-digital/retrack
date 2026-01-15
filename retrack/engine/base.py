import typing

import numpy as np
import pandas as pd

from retrack.nodes.base import BaseNode
from retrack.utils import constants, registry
from retrack.engine.schemas import ExecutionSchema
from retrack.utils.transformers import to_normalized_dict, process_node_connections


class Execution:
    def __init__(
        self,
        payload: pd.DataFrame,
        states: pd.DataFrame,
        filters: dict = None,
        context: registry.Registry = None,
        child_executions: dict = None,
        nodes: dict = None,
        constants: dict = None,
    ):
        self.payload = payload
        self.states = states
        self.filters = filters or {}
        self.child_executions = child_executions or {}
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

    def add_child_execution(self, node_id: str, execution: "Execution"):
        if node_id not in self.child_executions:
            self.child_executions[node_id] = []
        self.child_executions[node_id].append(execution)

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
        inputs = to_normalized_dict(df=self.payload, key_name="name")

        nodes = []
        flat_values = {}

        for id, node in self.nodes.items():
            current_node_filter = self.filters.get(node.id, None)

            node_inputs_dict = (
                node.inputs
                if isinstance(node.inputs, dict)
                else node.inputs.dict()
                if hasattr(node.inputs, "dict")
                else {}
            )
            node_inputs = process_node_connections(
                connections_dict=node_inputs_dict,
                get_state_data_func=self.get_state_data,
                constants=self.constants,
                filter_by=current_node_filter,
                name_field="to",
                target_field="from",
                target_key="output",
            )

            node_outputs_dict = (
                node.outputs
                if isinstance(node.outputs, dict)
                else node.outputs.dict()
                if hasattr(node.outputs, "dict")
                else {}
            )
            node_outputs = process_node_connections(
                connections_dict=node_outputs_dict,
                get_state_data_func=self.get_state_data,
                constants=self.constants,
                filter_by=current_node_filter,
                name_field="from",
                target_field="to",
                target_key="input",
                node_id=node.id,
                use_node_id_for_values=True,
            )

            for node_input in node_inputs:
                key = (id, node.alias(), "input", node_input["to"])
                if key not in flat_values:
                    flat_values[key] = []
                flat_values[key].extend(node_input.get("values", []))

            for node_output in node_outputs:
                key = (id, node.alias(), "output", node_output["to"])
                if key not in flat_values:
                    flat_values[key] = []
                flat_values[key].extend(node_output.get("values", []))

            nodes.append(
                {
                    "id": id,
                    "type": node.name,
                    "name": node.alias(),
                    "default": node.default(),
                }
            )

        values = [
            {
                "node_id": key[0],
                "node_type": self.nodes[key[0]].name,
                "node_name": self.nodes[key[0]].alias(),
                "connection_type": key[2],
                "connection_name": key[3],
                "values": vals,
            }
            for key, vals in flat_values.items()
        ]

        results = to_normalized_dict(df=self.result, key_name="name")

        return {
            "inputs": inputs,
            "nodes": nodes,
            "connections": values,
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
