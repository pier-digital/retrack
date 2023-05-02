from retrack.validators.base import BaseValidator


class NodeExistsValidator(BaseValidator):
    """Validator that checks if a node exists in the graph."""

    def __init__(
        self, node_name: str, max_quantity: int = None, min_quantity: int = None
    ) -> None:
        """Initialize the validator.

        Args:
            node_name: The name of the node to validate.
            max_quantity: The maximum quantity of nodes to validate.
            min_quantity: The minimum quantity of nodes to validate.
        """
        self.node_name = node_name.lower()
        self.max_quantity = max_quantity
        self.min_quantity = min_quantity

    def validate(self, graph_data: dict, **kwargs) -> bool:
        """Validate the graph data.

        Args:
            graph_data: The graph data to validate.

        Returns:
            True if the graph data is valid, False otherwise.
        """
        nodes = graph_data.get("nodes", [])
        nodes = [
            node for _, node in nodes.items() if node["name"].lower() == self.node_name
        ]
        if self.max_quantity is not None and len(nodes) > self.max_quantity:
            return False
        if self.min_quantity is not None and len(nodes) < self.min_quantity:
            return False
        return True
