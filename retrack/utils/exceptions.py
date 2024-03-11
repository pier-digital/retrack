import pandas as pd
import traceback
from retrack.engine.schemas import (
    ErrorSchema,
    DetailSchema,
    ExceptionSchema,
    ExecutionMetadata,
)


class ExecutionException(Exception):
    """Exception raised when an error occurs during execution of a command."""

    def __init__(self, rule_metadata, node_id, e, execution):
        self.error = ErrorSchema(
            title="Execution error",
            status="500",
            detail=DetailSchema(
                msg=f"Error executing node {node_id} from rule {rule_metadata.name} version {rule_metadata.version}",
                type="ExecutionException",
                exception=ExceptionSchema(
                    msg=str(e),
                    exception_type=type(e).__name__,
                    traceback=traceback.format_exception(e),
                ),
            ),
            metadata=ExecutionMetadata(
                name=rule_metadata.name,
                version=rule_metadata.version,
                node_id=node_id,
                execution=execution.to_dict(),
            ),
        )

        super().__init__(self.error.model_dump())  # TODO: padronizar mensagens de erros


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
