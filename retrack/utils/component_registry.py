import typing

from retrack.nodes.base import BaseNode
from retrack.utils.registry import Registry


class ComponentRegistry(Registry):
    """A registry to store instances of BaseNode (aka Components).

    It also provides indexes to access the value by name, class, kind and memory type."""

    def __init__(self, case_sensitive: bool = False):
        super().__init__(case_sensitive=case_sensitive)
        self._keys_by_name_map = {}
        self._keys_by_class_map = {}
        self._keys_by_kind_map = {}
        self._keys_by_memory_type_map = {}

    ##################
    ### Properties ###
    ##################

    @property
    def keys_by_name_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._keys_by_name_map

    @property
    def keys_by_class_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._keys_by_class_map

    @property
    def keys_by_kind_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._keys_by_kind_map

    @property
    def keys_by_memory_type_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._keys_by_memory_type_map

    ####################
    ### Registration ###
    ####################

    def __register_in_keys_by_name_map(self, key: str, value: BaseNode) -> None:
        name = value.name.lower()
        if name not in self._keys_by_name_map:
            self._keys_by_name_map[name] = []

        self._keys_by_name_map[name].append(key)

    def __register_in_keys_by_class_map(self, key: str, value: BaseNode) -> None:
        class_name = value.__class__.__name__.lower()
        if class_name not in self._keys_by_class_map:
            self._keys_by_class_map[class_name] = []

        self._keys_by_class_map[class_name].append(key)

    def __register_in_keys_by_kind_map(self, key: str, value: BaseNode) -> None:
        node_kind = value.kind()
        if node_kind not in self._keys_by_kind_map:
            self._keys_by_kind_map[node_kind] = []

        self._keys_by_kind_map[node_kind].append(key)

    def __register_in_keys_by_memory_type_map(self, key: str, value: BaseNode) -> None:
        memory_type = value.memory_type()

        if memory_type not in self._keys_by_memory_type_map:
            self._keys_by_memory_type_map[memory_type] = []

        self._keys_by_memory_type_map[memory_type].append(key)

    ######################
    ### Unregistration ###
    ######################

    def __unregister_from_keys_by_name_map(self, key: str, value: BaseNode) -> None:
        name = value.name.lower()
        self._keys_by_name_map[name].remove(key)

    def __unregister_from_keys_by_class_map(self, key: str, value: BaseNode) -> None:
        class_name = value.__class__.__name__.lower()
        self._keys_by_class_map[class_name].remove(key)

    def __unregister_from_keys_by_kind_map(self, key: str, value: BaseNode) -> None:
        node_kind = value.kind()
        self._keys_by_kind_map[node_kind].remove(key)

    def __unregister_from_keys_by_memory_type_map(
        self, key: str, value: BaseNode
    ) -> None:
        memory_type = value.memory_type()
        self._keys_by_memory_type_map[memory_type].remove(key)

    ####################
    ### Public API #####
    ####################

    def register(self, key: str, value: BaseNode, overwrite: bool = False) -> None:
        """Register an entry."""
        if not isinstance(value, BaseNode):
            raise ValueError("value must be a BaseNode instance.")

        super().register(key, value, overwrite=overwrite)

        self.__register_in_keys_by_name_map(key, value)
        self.__register_in_keys_by_class_map(key, value)
        self.__register_in_keys_by_kind_map(key, value)
        self.__register_in_keys_by_memory_type_map(key, value)

    def unregister(self, key: str) -> None:
        """Unregister an entry."""
        if not self._case_sensitive:
            key = key.lower()

        value = self._value.pop(key, None)

        if value is None:
            return

        self.__unregister_from_keys_by_name_map(key, value)
        self.__unregister_from_keys_by_class_map(key, value)
        self.__unregister_from_keys_by_kind_map(key, value)
        self.__unregister_from_keys_by_memory_type_map(key, value)

    #####################
    ### Query methods ###
    #####################

    def get_by_name(self, name: str) -> typing.List[BaseNode]:
        name = name.lower()
        return [self.get(id_) for id_ in self.keys_by_name_map.get(name, [])]

    def get_by_class(self, class_name: str) -> typing.List[BaseNode]:
        class_name = class_name.lower()
        return [self.get(id_) for id_ in self.keys_by_class_map.get(class_name, [])]

    def get_by_kind(self, kind: str) -> typing.List[BaseNode]:
        return [self.get(id_) for id_ in self.keys_by_kind_map.get(kind, [])]

    def get_by_memory_type(self, memory_type: str) -> typing.List[BaseNode]:
        return [
            self.get(id_) for id_ in self.keys_by_memory_type_map.get(memory_type, [])
        ]

    def _filter_connectors(self, connectors, connector_filter) -> typing.List[str]:
        result = []

        for connector_name, value in connectors.items():
            if connector_filter is not None and connector_name != connector_filter:
                continue

            for connection in value["connections"]:
                result.append(connection["node"])
        return result

    def get_node_input_connections(
        self, node_id: str, connector_filter=None
    ) -> typing.List[str]:
        node_dict = self.get(node_id).model_dump(by_alias=True)

        connectors = node_dict.get("inputs", {})
        return self._filter_connectors(connectors, connector_filter)

    def get_node_output_connections(
        self, node_id: str, connector_filter=None
    ) -> typing.List[str]:
        node_dict = self.get(node_id).model_dump(by_alias=True)

        connectors = node_dict.get("outputs", {})
        return self._filter_connectors(connectors, connector_filter)

    def calculate_edges(self) -> typing.List[typing.Tuple[str, str]]:
        edges = []

        for node_id, node in self.memory.items():
            for _, output_connection in node.outputs:
                for c in output_connection.connections:
                    edges.append((node_id, c.node))

        return edges
