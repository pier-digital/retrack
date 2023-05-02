class BaseValidator:
    """Base class for all validators."""

    def validate(self, **kwargs) -> bool:
        """Validate the graph data.

        Returns:
            True if the graph data is valid, False otherwise.
        """
        raise NotImplementedError
