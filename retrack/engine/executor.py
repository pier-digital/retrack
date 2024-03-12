import typing

import pandas as pd
import pydantic

from retrack.engine.base import Execution
from retrack.engine.schemas import RuleMetadata
from retrack.engine.request_manager import RequestManager
from retrack.nodes.base import NodeKind, NodeMemoryType
from retrack.utils import constants, exceptions
from retrack.utils.component_registry import ComponentRegistry


class RuleExecutor:
    def __init__(
        self,
        components_registry: ComponentRegistry,
        execution_order: typing.List[str],
        metadata: RuleMetadata,
    ):
        """Class that executes a rule.

        Args:
            components_registry (ComponentRegistry): Components registry.
            execution_order (typing.List[str]): Execution order.
            metadata (RuleMetadata): Rule metadata.

        Raises:
            exceptions.ExecutionException: If there is an error during execution.
            exceptions.ValidationException: If there is an error during validation.
        """
        self._components_registry = components_registry
        self._execution_order = execution_order
        self._metadata = metadata

        input_nodes = self._components_registry.get_by_kind(NodeKind.INPUT)
        self._input_columns = {
            f"{node.id}@{constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME}": node.data.name
            for node in input_nodes
        }
        self._request_manager = RequestManager(input_nodes)

        self._set_constants()

    @property
    def execution_order(self) -> typing.List[str]:
        return self._execution_order

    @property
    def metadata(self) -> RuleMetadata:
        return self._metadata

    @property
    def request_manager(self) -> RequestManager:
        return self._request_manager

    @property
    def request_model(self) -> pydantic.BaseModel:
        return self._request_manager.model

    @property
    def constants(self) -> dict:
        return self._constants

    def _set_constants(self):
        constant_nodes = self._components_registry.get_by_memory_type(
            NodeMemoryType.CONSTANT
        )
        self._constants = {}
        for node in constant_nodes:
            for output_connector_name, _ in node.outputs:
                self._constants[f"{node.id}@{output_connector_name}"] = node.data.value

    @property
    def input_columns(self) -> dict:
        return self._input_columns

    def __set_output_connection_filters(
        self,
        node_id: str,
        filter_value: typing.Any,
        execution: Execution,
        connector_filter=None,
    ):
        if filter_value is None:
            return

        output_connections = self._components_registry.get_node_output_connections(
            node_id, connector_filter=connector_filter
        )
        execution.update_filters(filter_value, output_connections=output_connections)

    def __get_input_params(
        self,
        node_dict: dict,
        current_node_filter: pd.Series,
        execution: Execution,
        include_payload: bool = False,
    ) -> dict:
        input_params = {}

        for connector_name, connections in node_dict.get("inputs", {}).items():
            if connector_name.endswith(constants.NULL_SUFFIX):
                continue

            for connection in connections["connections"]:
                input_params[connector_name] = execution.get_state_data(
                    f"{connection['node']}@{connection['output']}",
                    constants=self.constants,
                    filter_by=current_node_filter,
                )

        if include_payload:
            for input_column in execution.payload.columns:
                input_params[input_column] = execution.payload[input_column]

        return input_params

    def __run_node(self, node_id: str, execution: Execution):
        current_node_filter = execution.filters.get(node_id, None)
        # if there is a filter, we need to set the children nodes to receive filtered data
        self.__set_output_connection_filters(
            node_id, current_node_filter, execution=execution
        )

        node = self._components_registry.get(node_id)

        if node.memory_type == NodeMemoryType.CONSTANT:
            return

        input_params = self.__get_input_params(
            node.model_dump(by_alias=True),
            current_node_filter,
            execution=execution,
            include_payload=node.kind() == NodeKind.CONNECTOR
            or node.kind() == NodeKind.FLOW,
        )
        output = node.run(**input_params)

        for output_name, output_value in output.items():
            if (
                output_name == constants.OUTPUT_REFERENCE_COLUMN
                or output_name == constants.OUTPUT_MESSAGE_REFERENCE_COLUMN
            ):  # Setting output values
                execution.set_state_data(output_name, output_value, current_node_filter)
            elif output_name.endswith(constants.FILTER_SUFFIX):  # Setting filters
                self.__set_output_connection_filters(
                    node_id,
                    output_value,
                    execution=execution,
                    connector_filter=output_name,
                )
            else:  # Setting node outputs to be used as inputs by other nodes
                execution.set_state_data(
                    f"{node_id}@{output_name}",
                    output_value,
                    filter_by=current_node_filter,
                )

    def validate_payload(self, payload_df: pd.DataFrame):
        """Validates the payload.

        Args:
            payload_df (pd.DataFrame): The payload to be validated.

        Raises:
            exceptions.ValidationException: If there is an error during validation.

        Returns:
            pd.DataFrame: The validated payload.
        """
        if not isinstance(payload_df, pd.DataFrame):
            raise exceptions.ValidationException(
                rule_metadata=self.metadata,
                payload_df=payload_df,
                raised_exception=TypeError("Payload must be a DataFrame"),
                msg="Payload must be a DataFrame",
            )

        try:
            validated = self.request_manager.validate(payload_df.reset_index(drop=True))
        except Exception as e:
            raise exceptions.ValidationException(
                rule_metadata=self.metadata, payload_df=payload_df, raised_exception=e
            )

        return validated

    def execute(
        self,
        payload_df: pd.DataFrame,
        debug_mode: bool = False,
    ) -> typing.Union[
        pd.DataFrame, typing.Tuple[Execution, typing.Optional[Exception]]
    ]:
        """Executes the rule.

        Args:
            payload_df (pd.DataFrame): The payload to be executed.
            debug_mode (bool, optional): If True, runs the rule in debug mode and returns the exception, if any. Defaults to False.

        Raises:
            exceptions.ExecutionException: If there is an error during execution.
            exceptions.ValidationException: If there is an error during validation.

        Returns:
            typing.Union[pd.DataFrame, typing.Tuple[Execution, typing.Optional[Exception]]]: The result of the execution or a tuple with the execution and the exception, if any.
        """
        try:
            validated_payload = self.validate_payload(payload_df)
        except exceptions.ValidationException as e:
            if debug_mode:
                return None, e

            raise e

        execution = Execution.from_payload(
            validated_payload=validated_payload,
            input_columns=self.input_columns,
        )

        for node_id in self.execution_order:
            try:
                self.__run_node(node_id, execution=execution)
            except Exception as e:
                msg = None
                if isinstance(e, exceptions.ExecutionException):
                    msg = "Error executing a sub-rule node {} from rule {} version {}".format(
                        node_id, self.metadata.name, self.metadata.version
                    )

                exception = exceptions.ExecutionException(
                    rule_metadata=self.metadata,
                    execution_data=execution.to_model(),
                    node_id=node_id,
                    raised_exception=e,
                    msg=msg,
                )
                if debug_mode:
                    return execution, exception

                raise exception

            if execution.has_ended():
                break

        if debug_mode:
            return execution, None

        return execution.result
