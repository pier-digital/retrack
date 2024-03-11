import pandas as pd
import traceback
from retrack.engine.schemas import (
    ErrorSchema,
    DetailSchema,
    ExceptionSchema,
    ExecutionMetadata,
    RuleMetadata,
    ExecutionSchema,
)


def create_exception_schema(raised_exception: Exception) -> ExceptionSchema:
    traceback_str = None
    try:
        traceback_str = traceback.format_exception(raised_exception)
    except Exception:
        pass

    raised_message = str(raised_exception)
    if hasattr(raised_exception, "error"):
        raised_message = raised_exception.error.model_dump()

    return ExceptionSchema(
        msg=raised_message,
        exception_type=type(raised_exception).__name__,
        traceback=traceback_str,
    )


class ExecutionException(Exception):
    """Exception raised when an error occurs during execution of a command."""

    def __init__(
        self,
        rule_metadata: RuleMetadata,
        execution_data: ExecutionSchema,
        node_id: int,
        raised_exception: Exception,
        msg: str = None,
    ):
        msg = (
            msg
            or f"Error executing node {node_id} from rule {rule_metadata.name} version {rule_metadata.version}"
        )

        self.error = ErrorSchema(
            title="Execution error",
            status="500",
            detail=DetailSchema(
                msg=msg,
                type="ExecutionException",
                exception=create_exception_schema(raised_exception),
            ),
            metadata=ExecutionMetadata(
                name=rule_metadata.name,
                version=rule_metadata.version,
                node_id=node_id,
                execution=execution_data,
            ),
        )

        super().__init__(self.error.model_dump())


class ValidationException(Exception):
    """Exception raised when an error occurs during validation of a command."""

    def __init__(
        self,
        rule_metadata: RuleMetadata,
        payload_df: pd.DataFrame,
        raised_exception: Exception,
        msg: str = None,
    ):
        msg = (
            msg
            or f"Error validating payload for rule {rule_metadata.name} version {rule_metadata.version}"
        )

        self.error = ErrorSchema(
            title="Validation error",
            status="400",
            detail=DetailSchema(
                msg=msg,
                type="ValidationException",
                exception=create_exception_schema(raised_exception),
            ),
            metadata=ExecutionMetadata(
                name=rule_metadata.name,
                version=rule_metadata.version,
                node_id=None,
                execution=ExecutionSchema(payload=str(payload_df)),
            ),
        )

        super().__init__(self.error.model_dump())


class InvalidVersionException(Exception):
    """Exception raised when an invalid version is found."""

    def __init__(
        self, rule_metadata: RuleMetadata, raised_exception: Exception, msg: str = None
    ):
        msg = (
            msg
            or f"Invalid version for rule {rule_metadata.name} version {rule_metadata.version}"
        )

        self.error = ErrorSchema(
            title="Invalid version",
            status="400",
            detail=DetailSchema(
                msg=msg,
                type="InvalidVersionException",
                exception=create_exception_schema(raised_exception),
            ),
            metadata=ExecutionMetadata(
                name=rule_metadata.name,
                version=rule_metadata.version,
                node_id=None,
                execution=None,
            ),
        )

        super().__init__(self.error.model_dump())
