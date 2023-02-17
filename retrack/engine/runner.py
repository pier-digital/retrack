import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.engine.parser import Parser
from retrack.engine.request_manager import RequestManager
from retrack.nodes.base import NodeKind
from retrack.utils import constants, graph


class Runner:
    def __init__(self, parser: Parser):
        self._parser = parser

        input_nodes = self._parser.get_nodes_by_kind(NodeKind.INPUT)
        self._input_new_columns = {
            f"{node.id}@{constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME}": node.data.name
            for node in input_nodes
        }
        self._request_manager = RequestManager(input_nodes)

        self._execution_order = graph.get_execution_order(self._parser)
        self._state_df = None

        self._filters = {}

    @property
    def request_manager(self) -> RequestManager:
        return self._request_manager

    @property
    def request_model(self) -> pydantic.BaseModel:
        return self._request_manager.model

    @property
    def state_df(self) -> pd.DataFrame:
        return self._state_df

    @property
    def states(self) -> list:
        return self._state_df.to_dict(orient="records")

    @property
    def filters(self) -> dict:
        return self._filters

    @property
    def filter_df(self) -> pd.DataFrame:
        return pd.DataFrame(self._filters)

    def __get_initial_state_df(self, payload: typing.Union[dict, list]) -> pd.DataFrame:
        validated_payload = self.request_manager.validate(payload)
        validated_payload = pd.DataFrame([p.dict() for p in validated_payload])

        state_df = pd.DataFrame([])
        for node_id, input_name in self._input_new_columns.items():
            state_df[node_id] = validated_payload[input_name]

        state_df[constants.OUTPUT_REFERENCE_COLUMN] = np.nan
        state_df[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] = np.nan

        return state_df

    @staticmethod
    def __get_output_state_df(state_df: pd.DataFrame) -> pd.DataFrame:
        output_state_df = state_df[
            [
                constants.OUTPUT_REFERENCE_COLUMN,
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN,
            ]
        ].copy()

        output_state_df = output_state_df.rename(
            columns={
                constants.OUTPUT_REFERENCE_COLUMN: "output",
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN: "message",
            }
        )

        return output_state_df

    def __set_output_connection_filters(
        self, node, value: typing.Any, filter_by_connector=None
    ):
        output_connections = graph.get_node_connections(
            node, is_input=False, filter_by_connector=filter_by_connector
        )
        for output_connection_id in output_connections:
            if self._filters.get(output_connection_id, None) is None:
                self._filters[output_connection_id] = value
            else:
                self._filters[output_connection_id] = (
                    self._filters[output_connection_id] & value
                )

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

    def __get_state_data(self, column: str, filter_by: typing.Any = None):
        if filter_by is None:
            return self._state_df[column]
        else:
            return self._state_df.loc[filter_by, column]

    def __set_state_data(
        self, column: str, value: typing.Any, filter_by: typing.Any = None
    ):
        if filter_by is None:
            self._state_df[column] = value
        else:
            self._state_df.loc[filter_by, column] = value

    def __run_node(self, node_id: str):
        node = self._parser.get_node_by_id(node_id)
        current_node_filter = self._filters.get(node_id, None)

        input_params = self.__get_input_params(
            node.dict(by_alias=True), current_node_filter
        )

        if (
            current_node_filter is not None
        ):  # if there is a filter, we need to set the children nodes to receive filtered data
            self.__set_output_connection_filters(node, current_node_filter)

        output = node.run(**input_params)
        for output_name, output_value in output.items():
            if (
                output_name == constants.OUTPUT_REFERENCE_COLUMN
                or output_name == constants.OUTPUT_MESSAGE_REFERENCE_COLUMN
            ):  # Setting output values
                self.__set_state_data(output_name, output_value, current_node_filter)
            elif output_name.endswith(constants.FILTER_SUFFIX):  # Setting filters
                self.__set_output_connection_filters(node, output_value, output_name)
            else:  # Setting node outputs to be used as inputs by other nodes
                self.__set_state_data(
                    f"{node_id}@{output_name}", output_value, current_node_filter
                )

    def __call__(
        self, payload: typing.Union[dict, list], to_dict: bool = True
    ) -> pd.DataFrame:
        self._state_df = self.__get_initial_state_df(payload)
        self._filters = {}

        for node_id in self._execution_order:
            try:
                self.__run_node(node_id)
            except Exception as e:
                raise e  # TODO: Handle errors
            if self._state_df[constants.OUTPUT_REFERENCE_COLUMN].isna().sum() == 0:
                break

        if to_dict:
            return self.__get_output_state_df(self._state_df).to_dict(orient="records")

        return Runner.__get_output_state_df(self._state_df)
