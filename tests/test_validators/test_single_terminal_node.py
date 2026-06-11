import pytest

from retrack.validators.single_terminal_node import SingleTerminalNodeValidator


@pytest.fixture
def validator():
    return SingleTerminalNodeValidator()


def _graph(node_names):
    return {
        "nodes": {
            str(i): {"id": i, "name": name, "data": {}, "inputs": {}, "outputs": {}}
            for i, name in enumerate(node_names)
        }
    }


# --- valid cases ---


def test_accepts_single_output_node(validator):
    is_valid, msg = validator.validate(_graph(["Start", "Output"]))
    assert is_valid is True
    assert msg is None


def test_accepts_multiple_output_nodes_same_type(validator):
    """Conditional branches produce multiple Output nodes — must remain valid."""
    is_valid, msg = validator.validate(_graph(["Start", "Output", "Output", "Output"]))
    assert is_valid is True
    assert msg is None


def test_accepts_single_multiple_outputs_node(validator):
    is_valid, msg = validator.validate(_graph(["Start", "MultipleOutputs"]))
    assert is_valid is True
    assert msg is None


def test_accepts_multiple_multiple_outputs_nodes(validator):
    is_valid, msg = validator.validate(
        _graph(["Start", "MultipleOutputs", "MultipleOutputs"])
    )
    assert is_valid is True
    assert msg is None


def test_accepts_graph_with_no_terminal_node(validator):
    """Validator does not enforce presence — that is handled separately."""
    is_valid, msg = validator.validate(_graph(["Start", "Input"]))
    assert is_valid is True


# --- invalid cases ---


def test_rejects_output_and_multiple_outputs_together(validator):
    is_valid, msg = validator.validate(_graph(["Start", "Output", "MultipleOutputs"]))
    assert is_valid is False
    assert msg is not None


def test_rejects_multiple_outputs_and_output_reversed(validator):
    is_valid, msg = validator.validate(_graph(["MultipleOutputs", "Output"]))
    assert is_valid is False


def test_rejects_mix_with_many_output_nodes(validator):
    """Conditional branches with Output + one MultipleOutputs must be rejected."""
    is_valid, msg = validator.validate(
        _graph(["Start", "Output", "Output", "MultipleOutputs"])
    )
    assert is_valid is False


# --- case insensitivity ---


def test_case_insensitive_output(validator):
    graph = {
        "nodes": {
            "0": {"id": 0, "name": "output", "data": {}, "inputs": {}, "outputs": {}}
        }
    }
    is_valid, _ = validator.validate(graph)
    assert is_valid is True


def test_case_insensitive_multiple_outputs(validator):
    graph = {
        "nodes": {
            "0": {
                "id": 0,
                "name": "multipleoutputs",
                "data": {},
                "inputs": {},
                "outputs": {},
            }
        }
    }
    is_valid, _ = validator.validate(graph)
    assert is_valid is True


def test_empty_graph(validator):
    is_valid, _ = validator.validate({"nodes": {}})
    assert is_valid is True
