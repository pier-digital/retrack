from typing import Optional


class BaseValidator:
    """Base class for all validators."""

    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate the graph data.

        Returns:
            A tuple (is_valid, error_message). is_valid is True if the graph data is valid, False otherwise.
            error_message contains details about the validation failure, or None if validation passed.
        """
        raise NotImplementedError
