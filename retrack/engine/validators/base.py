class BaseValidator:
    """Base class for all validators."""

    def validate(self, graph_data: dict) -> bool:
        """Validate the graph data.

        Args:
            graph_data: The graph data to validate.

        Returns:
            True if the graph data is valid, False otherwise.
        """
        raise NotImplementedError
