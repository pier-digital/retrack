import typing

import pydantic

from retrack import validators
from retrack.engine.schemas import RuleMetadata
from retrack.engine.executor import RuleExecutor
from retrack.utils import graph
from retrack.utils.component_registry import ComponentRegistry
from retrack.utils.registry import Registry


class Rule(RuleMetadata):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    components_registry: ComponentRegistry
    execution_order: typing.List[str]
    _executor: RuleExecutor = None

    @property
    def executor(self) -> RuleExecutor:
        if self._executor is None:
            self._executor = RuleExecutor(
                self.components_registry,
                self.execution_order,
                self.as_metadata(),
            )
        return self._executor

    def as_metadata(self) -> RuleMetadata:
        return RuleMetadata(**self.model_dump())

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
        components_registry = Rule.create_component_registry(
            graph_data, nodes_registry, dynamic_nodes_registry, validator_registry
        )
        version = graph.validate_version(
            graph_data, raise_if_null_version, validate_version, name
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

    @staticmethod
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

            components_registry.register(node_id, validation_model(**node_metadata))

            for input_node in component.generate_input_nodes():
                components_registry.register(input_node.id, input_node, overwrite=True)

        return components_registry
