import pydantic
from retrack.utils.component_registry import ComponentRegistry
from retrack.utils.registry import Registry

from retrack.utils import graph
from retrack import validators
import typing


import numpy as np
import pandas as pd

from retrack.engine.request_manager import RequestManager
from retrack.nodes.base import NodeKind, NodeMemoryType
from retrack.utils import constants


class RuleExecutor:
    def __init__(self, rule: "Rule"):
        self._rule = rule
        self._validated_payload = None
        self.reset()
        self._set_constants()
        self._set_input_columns()
        self._request_manager = RequestManager(
            self._rule.components_registry.get_by_kind(NodeKind.INPUT)
        )

    @property
    def rule(self) -> "Rule":
        return self._rule

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
        constant_nodes = self.rule.components_registry.get_by_memory_type(
            NodeMemoryType.CONSTANT
        )
        self._constants = {}
        for node in constant_nodes:
            for output_connector_name, _ in node.outputs:
                self._constants[f"{node.id}@{output_connector_name}"] = node.data.value

    @property
    def input_columns(self) -> dict:
        return self._input_columns

    def _set_input_columns(self):
        input_nodes = self._rule.components_registry.get_by_kind(NodeKind.INPUT)
        self._input_columns = {
            f"{node.id}@{constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME}": node.data.name
            for node in input_nodes
        }

    def reset(self):
        self._states = None
        self._filters = {}

    def __set_output_connection_filters(
        self, node_id: str, filter: typing.Any, connector_filter=None
    ):
        if filter is not None:
            output_connections = (
                self.rule.components_registry.get_node_output_connections(
                    node_id, connector_filter=connector_filter
                )
            )
            for output_connection_id in output_connections:
                if self._filters.get(output_connection_id, None) is None:
                    self._filters[output_connection_id] = filter
                else:
                    self._filters[output_connection_id] = (
                        self._filters[output_connection_id] & filter
                    )

    def _create_initial_state_from_payload(
        self, payload_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Create initial state from payload. This is the first step of the runner."""
        self._validated_payload = self.request_manager.validate(
            payload_df.reset_index(drop=True)
        )

        state_df = pd.DataFrame([])
        for node_id, input_name in self.input_columns.items():
            state_df[node_id] = self._validated_payload[input_name]

        state_df[constants.OUTPUT_REFERENCE_COLUMN] = np.nan
        state_df[constants.OUTPUT_MESSAGE_REFERENCE_COLUMN] = np.nan

        return state_df

    def __get_input_params(
        self, node_id: str, node_dict: dict, current_node_filter: pd.Series
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

        node = self.rule.components_registry.get(node_id)

        if node.memory_type == NodeMemoryType.CONSTANT:
            return

        input_params = self.__get_input_params(
            node_id, node.model_dump(by_alias=True), current_node_filter
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

    def execute(
        self,
        payload_df: pd.DataFrame,
        return_all_states: bool = False,
    ) -> pd.DataFrame:
        """Executes the flow with the given payload.

        Args:
            payload_df (pd.DataFrame): The payload to be used as input.
            return_all_states (bool, optional): If True, returns all states. Defaults to False.

        Returns:
            pd.DataFrame: The output of the flow.
        """
        if not isinstance(payload_df, pd.DataFrame):
            raise ValueError("payload_df must be a pandas.DataFrame")

        self.reset()
        self._states = self._create_initial_state_from_payload(payload_df)

        for node_id in self.rule.execution_order:
            try:
                self.__run_node(node_id)
            except Exception as e:
                raise Exception(
                    f"Error running node {node_id} in {self.rule.name} with version {self.rule.version}"
                ) from e

            if self.states[constants.OUTPUT_REFERENCE_COLUMN].isna().sum() == 0:
                break

        if return_all_states:
            return self.states

        return self.states[
            [
                constants.OUTPUT_REFERENCE_COLUMN,
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN,
            ]
        ]


class Rule(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    name: typing.Optional[str] = None
    version: str
    components_registry: ComponentRegistry
    execution_order: typing.List[str]
    _executor: RuleExecutor = None

    @property
    def executor(self) -> RuleExecutor:
        if self._executor is None:
            self._executor = RuleExecutor(self)
        return self._executor

    @classmethod
    def create(
        cls,
        graph_data: dict,
        nodes_registry: Registry,
        dynamic_nodes_registry: Registry,
        validator_registry: Registry = validators.registry(),
        raise_if_null_version: bool = False,
        validate_version: bool = True,
        name: str = None,
    ):
        components_registry = create_component_registry(
            graph_data, nodes_registry, dynamic_nodes_registry, validator_registry
        )
        version = graph.validate_version(
            graph_data, raise_if_null_version, validate_version
        )
        graph_data = graph_data

        graph.validate_with_validators(
            graph_data,
            components_registry.calculate_edges(),
            validator_registry,
        )

        execution_order = graph.get_execution_order(components_registry)

        return cls(
            version=version,
            components_registry=components_registry,
            execution_order=execution_order,
            name=name,
        )


def create_component_registry(
    graph_data: dict,
    nodes_registry: Registry,
    dynamic_nodes_registry: Registry,
    validator_registry: Registry,
) -> ComponentRegistry:
    components_registry = ComponentRegistry()
    graph_data = graph.validate_data(graph_data)
    for node_id, node_metadata in graph_data["nodes"].items():
        if node_id in components_registry:
            raise ValueError(f"Duplicate node id: {node_id}")

        node_name = node_metadata.get("name", None)
        graph.check_node_name(node_name, node_id)

        node_name = node_name.lower()

        node_factory = dynamic_nodes_registry.get(node_name)

        if node_factory is not None:
            validation_model = node_factory(
                **node_metadata,
                nodes_registry=nodes_registry,
                dynamic_nodes_registry=dynamic_nodes_registry,
                validator_registry=validator_registry,
                rule_class=Rule,
            )
        else:
            validation_model = nodes_registry.get(node_name)

        if validation_model is None:
            raise ValueError(f"Unknown node name: {node_name}")

        component = validation_model(**node_metadata)

        for input_node in component.generate_input_nodes():
            components_registry.register(input_node.id, input_node)

        components_registry.register(node_id, validation_model(**node_metadata))

    return components_registry
