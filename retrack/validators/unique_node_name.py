from typing import Optional
from retrack.validators.base import BaseValidator


class UniqueNodeNameValidator(BaseValidator):
    """Validator that checks if node name is unique across the graph."""

    def validate(self, graph_data: dict, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate that all node name values are unique in the graph.

        Args:
            graph_data: The graph data to validate.

        Returns:
            A tuple (is_valid, error_message). is_valid is True if all node names are unique,
            False otherwise. error_message contains details about duplicate names.
        """
        nodes = graph_data.get("nodes", {})

        names_count = {}
        node_ids_by_name = {}

        for node_id, node in nodes.items():
            node_name = node.get("name")
            if node_name in ("Input", "Output"):
                continue

            data = node.get("data", {})
            name = data.get("name")

            if name is not None:
                if name not in names_count:
                    names_count[name] = 0
                    node_ids_by_name[name] = []

                names_count[name] += 1
                node_ids_by_name[name].append(node_id)

        duplicates = {
            name: node_ids
            for name, node_ids in node_ids_by_name.items()
            if names_count[name] > 1
        }

        if duplicates:
            duplicate_details = ", ".join(
                f"'{name}' (nodes: {', '.join(map(str, node_ids))})"
                for name, node_ids in duplicates.items()
            )
            return False, f"Duplicate node names found: {duplicate_details}"

        return True, None
