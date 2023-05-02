import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.engine.parser import Parser
from retrack.engine.request_manager import RequestManager
from retrack.nodes.base import NodeKind, NodeMemoryType
from retrack.utils import constants


class Runner:
    def __init__(self, parser: Parser):
        self._parser = parser
        self.reset()
        self._set_constants()
        self._set_input_columns()
        self._request_manager = RequestManager(self._parser.get_by_kind(NodeKind.INPUT))

    @property
    def parser(self) -> Parser:
        return self._parser

    @property
    def request_manager(self) -> RequestManager:
        return self._request_manager

    @property
    def request_model(self) -> pydantic.BaseModel:
        return self._request_manager.model

    @property
    def states(self) -> pd.DataFrame:
        return self._states

    @property
    def filters(self) -> dict:
        return self._filters

    @property
    def constants(self) -> dict:
        return self._constants

    def _set_constants(self):
        constant_nodes = self.parser.get_by_memory_type(NodeMemoryType.CONSTANT)
        self._constants = {}
        for node in constant_nodes:
            for output_connector_name, _ in node.outputs:
                self._constants[f"{node.id}@{output_connector_name}"] = node.data.value

    @property
    def input_columns(self) -> dict:
        return self._input_columns

    def _set_input_columns(self):
        input_nodes = self._parser.get_by_kind(NodeKind.INPUT)
        self._input_columns = {
            f"{node.id}@{constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME}": node.data.name
            for node in input_nodes
        }

    def reset(self):
        self._states = None
        self._filters = {}

    def __set_output_connection_filters(
        self, node_id: str, filter: typing.Any, filter_by_connector=None
    ):
        if filter is not None:
            output_connections = self.parser.get_node_connections(
                node_id, is_input=False, filter_by_connector=filter_by_connector
            )
            for output_connection_id in output_connections:
                if self._filters.get(output_connection_id, None) is None:
                    self._filters[output_connection_id] = filter
                else:
                    self._filters[output_connection_id] = (
                        self._filters[output_connection_id] & filter
                    )

    def _create_initial_state_from_payload(
        self, payload: typing.Union[dict, list]
    ) -> pd.DataFrame:
        """Create initial state from payload. This is the first step of the runner."""
        validated_payload = self.request_manager.validate(payload)
        validated_payload = pd.DataFrame([p.dict() for p in validated_payload])

        state_df = pd.DataFrame([])
        for node_id, input_name in self.input_columns.items():
            state_df[node_id] = validated_payload[input_name]

        state_df[constants.OUTPUT_REFERENCE_COLUMN] = np.nan
        state_df[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] = np.nan

        return state_df

    def __get_input_params(
        self, node_dict: dict, current_node_filter: pd.Series
    ) -> dict:
        input_params = {}

        for connector_name, connections in node_dict.get("inputs", {}).items():
            if connector_name.endswith(constants.NULL_SUFFIX):
                continue

            for connection in connections["connections"]:
                input_params[connector_name] = self.__get_state_data(
                    f"{connection['node']}@{connection['output']}", current_node_filter
                )

        return input_params

    def __set_state_data(
        self, column: str, value: typing.Any, filter_by: typing.Any = None
    ):
        if filter_by is None:
            self._states[column] = value
        else:
            self._states.loc[filter_by, column] = value

    def __get_state_data(self, column: str, filter_by: typing.Any = None):
        if column in self._constants:
            return self._constants[column]

        if filter_by is None:
            return self._states[column]

        return self._states.loc[filter_by, column]

    def __run_node(self, node_id: str):
        current_node_filter = self._filters.get(node_id, None)
        # if there is a filter, we need to set the children nodes to receive filtered data
        self.__set_output_connection_filters(node_id, current_node_filter)

        node = self.parser.get_by_id(node_id)

        if node.memory_type == NodeMemoryType.CONSTANT:
            return

        input_params = self.__get_input_params(
            node.dict(by_alias=True), current_node_filter
        )
        output = node.run(**input_params)

        for output_name, output_value in output.items():
            if (
                output_name == constants.OUTPUT_REFERENCE_COLUMN
                or output_name == constants.OUTPUT_MESSAGE_REFERENCE_COLUMN
            ):  # Setting output values
                self.__set_state_data(output_name, output_value, current_node_filter)
            elif output_name.endswith(constants.FILTER_SUFFIX):  # Setting filters
                self.__set_output_connection_filters(node_id, output_value, output_name)
            else:  # Setting node outputs to be used as inputs by other nodes
                self.__set_state_data(
                    f"{node_id}@{output_name}", output_value, current_node_filter
                )

    def __get_output_states(self) -> pd.DataFrame:
        """Returns a dataframe with the final states of the flow"""
        return pd.DataFrame(
            {
                "output": self.states[constants.OUTPUT_REFERENCE_COLUMN],
                "message": self.states[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN],
            }
        )

    def execute(self, payload: typing.Union[dict, list]) -> pd.DataFrame:
        """Executes the flow with the given payload"""
        self.reset()
        self._states = self._create_initial_state_from_payload(payload)

        for node_id in self.parser.execution_order:
            try:
                self.__run_node(node_id)
            except Exception as e:
                print(f"Error running node {node_id}")
                raise e
            if self.states[constants.OUTPUT_REFERENCE_COLUMN].isna().sum() == 0:
                break

        return self.__get_output_states()
