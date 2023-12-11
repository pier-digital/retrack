import pandas as pd


class ExecutionException(Exception):
    """Exception raised when an error occurs during execution of a command."""

    @classmethod
    def from_metadata(cls, metadata, node_id: str):
        return cls(
            f"Error executing node {node_id} from rule {metadata.name} version {metadata.version}"
        )


class ValidationException(Exception):
    """Exception raised when an error occurs during validation of a command."""

    @classmethod
    def from_metadata(cls, metadata, payload_df: pd.DataFrame):
        return cls(
            f"Error validating rule {metadata.name} version {metadata.version} with payload {payload_df}"
        )


class InvalidVersionException(Exception):
    """Exception raised when an invalid version is found."""

    pass
