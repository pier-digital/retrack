import typing

from retrack.nodes.base import BaseNode
from retrack.utils.registry import Registry


class ComponentRegistry(Registry):
    """A registry to store instances of BaseNode (aka Components).

    It also provides indexes to access the data by name, kind and memory type."""

    def __init__(self, case_sensitive: bool = False):
        super().__init__(case_sensitive=case_sensitive)
        self._indexes_by_name_map = {}
        self._indexes_by_kind_map = {}
        self._indexes_by_memory_type_map = {}

    @property
    def indexes_by_name_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._indexes_by_name_map

    @property
    def indexes_by_kind_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._indexes_by_kind_map

    @property
    def indexes_by_memory_type_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._indexes_by_memory_type_map

    def __register_in_indexes_by_name_map(self, name: str, data: BaseNode) -> None:
        node_name = data.__class__.__name__.lower()
        if node_name not in self._indexes_by_name_map:
            self._indexes_by_name_map[node_name] = []

        self._indexes_by_name_map[node_name].append(name)

    def __register_in_indexes_by_kind_map(self, name: str, data: BaseNode) -> None:
        node_kind = data.kind()
        if node_kind not in self._indexes_by_kind_map:
            self._indexes_by_kind_map[node_kind] = []

        self._indexes_by_kind_map[node_kind].append(name)

    def __register_in_indexes_by_memory_type_map(
        self, name: str, data: BaseNode
    ) -> None:
        memory_type = data.memory_type()

        if memory_type not in self._indexes_by_memory_type_map:
            self._indexes_by_memory_type_map[memory_type] = []

        self._indexes_by_memory_type_map[memory_type].append(name)

    def __unregister_from_indexes_by_name_map(self, name: str, data: BaseNode) -> None:
        node_name = data.__class__.__name__.lower()
        self._indexes_by_name_map[node_name].remove(name)

    def __unregister_from_indexes_by_kind_map(self, name: str, data: BaseNode) -> None:
        node_kind = data.kind()
        self._indexes_by_kind_map[node_kind].remove(name)

    def __unregister_from_indexes_by_memory_type_map(
        self, name: str, data: BaseNode
    ) -> None:
        memory_type = data.memory_type()
        self._indexes_by_memory_type_map[memory_type].remove(name)

    def register(self, name: str, data: BaseNode, overwrite: bool = False) -> None:
        """Register an entry."""
        if not isinstance(data, BaseNode):
            raise ValueError("data must be a BaseNode instance.")

        super().register(name, data, overwrite=overwrite)

        self.__register_in_indexes_by_name_map(name, data)
        self.__register_in_indexes_by_kind_map(name, data)
        self.__register_in_indexes_by_memory_type_map(name, data)

    def unregister(self, name: str) -> None:
        """Unregister an entry."""
        if not self._case_sensitive:
            name = name.lower()

        data = self._data.pop(name, None)

        if data is None:
            return

        self.__unregister_from_indexes_by_name_map(name, data)
        self.__unregister_from_indexes_by_kind_map(name, data)
        self.__unregister_from_indexes_by_memory_type_map(name, data)

    def get_by_name(self, name: str) -> typing.List[BaseNode]:
        name = name.lower()
        return [self.get(id_) for id_ in self.indexes_by_name_map.get(name, [])]

    def get_by_kind(self, kind: str) -> typing.List[BaseNode]:
        return [self.get(id_) for id_ in self.indexes_by_kind_map.get(kind, [])]

    def get_by_memory_type(self, memory_type: str) -> typing.List[BaseNode]:
        return [
            self.get(id_)
            for id_ in self.indexes_by_memory_type_map.get(memory_type, [])
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

        for node_id, node in self.data.items():
            for _, output_connection in node.outputs:
                for c in output_connection.connections:
                    edges.append((node_id, c.node))

        return edges
