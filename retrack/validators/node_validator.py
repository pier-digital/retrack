from typing import Optional
from retrack.validators.base import BaseValidator
import pandas as pd
import io


class IntervalCatV0Validator(BaseValidator):
    def validate(self, graph_data: dict, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate the graph data.

        Returns:
            A tuple (is_valid, error_message). is_valid is True if the graph data is valid, False otherwise.
            error_message contains details about the validation failure, or None if validation passed.
        """
        nodes = graph_data.get("nodes", [])
        interval_cats = [
            node for _, node in nodes.items() if node["name"] == "IntervalCatV0"
        ]

        if not interval_cats:
            return True, None

        for node in interval_cats:
            data = node.get("data", {})
            value = data.get("value", [])
            start_col = data.get("start_interval_column")
            end_col = data.get("end_interval_column")
            node_id = node.get("id", "unknown")

            if not start_col or not end_col or not value:
                continue

            try:
                csv_data = "\n".join(value)
                df = pd.read_csv(io.StringIO(csv_data))

                if start_col not in df.columns or end_col not in df.columns:
                    return (
                        False,
                        f"Missing required columns: {start_col}, {end_col} in node {node_id}",
                    )

                df[start_col] = pd.to_numeric(df[start_col], errors="coerce")
                df[end_col] = pd.to_numeric(df[end_col], errors="coerce")

                if df[start_col].isnull().any() or df[end_col].isnull().any():
                    return (
                        False,
                        f"Invalid numeric values in interval columns in node {node_id}",
                    )

                df = df.sort_values(by=start_col)
                if (df[start_col].values[1:] < df[end_col].values[:-1]).any():
                    return False, f"Overlapping intervals detected in node {node_id}"

            except Exception as e:
                return False, f"Validation error: {str(e)} in node {node_id}"

        return True, None
