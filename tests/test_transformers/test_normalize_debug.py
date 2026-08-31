from retrack.utils.transformers import normalize_execution_for_debug_iter


def _make_node(node_type, inputs, data=None):
    return {
        "id": "node-1",
        "name": node_type,
        "type": node_type,
        "inputs": inputs,
        "outputs": [],
        "default": None,
        "data": data or [],
    }


def _normalize(nodes_at_index):
    return list(normalize_execution_for_debug_iter([nodes_at_index]))


# ---------------------------------------------------------------------------
# node Output
# ---------------------------------------------------------------------------


def test_output_single_value():
    node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "n0",
                "target_name": "input_value",
                "value": 3028,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "basic"}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [
        {"name": "output", "value": 3028, "message": "basic"},
        {"name": "message", "value": "basic", "message": "basic"},
    ]


def test_output_message_none():
    node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "n0",
                "target_name": "input_value",
                "value": 1.5,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": None}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [{"name": "output", "value": 1.5, "message": None}]


def test_output_filters_none_value():
    node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "n0",
                "target_name": "input_value",
                "value": None,
                "source_name": "output",
            }
        ],
        data=[],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == []


def test_output_filters_nan_value():
    node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "n0",
                "target_name": "input_value",
                "value": float("nan"),
                "source_name": "output",
            }
        ],
        data=[],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == []


def test_output_without_value_does_not_emit_message():
    node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "n0",
                "target_name": "input_value",
                "value": None,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "not executed"}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == []


def test_only_executed_output_node_emits_message():
    executed = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "a",
                "target_name": "input_value",
                "value": 10,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "taken"}],
    )
    skipped = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "b",
                "target_name": "input_value",
                "value": None,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "not taken"}],
    )
    result = _normalize([executed, skipped])
    assert result[0]["outputs"] == [
        {"name": "output", "value": 10, "message": "taken"},
        {"name": "message", "value": "taken", "message": "taken"},
    ]


def test_output_empty_inputs():
    node = _make_node("Output", inputs=[], data=[{"name": "message", "value": "x"}])
    result = _normalize([node])
    assert result[0]["outputs"] == []


# ---------------------------------------------------------------------------
# node MultipleOutputs
# ---------------------------------------------------------------------------


def test_multiple_outputs_expands_all_keys():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {
                "node_id": "a",
                "target_name": "basic_7",
                "value": 3028,
                "source_name": "output",
            },
            {
                "node_id": "b",
                "target_name": "basic_15",
                "value": 7194,
                "source_name": "output",
            },
            {
                "node_id": "c",
                "target_name": "basic_30",
                "value": 15720,
                "source_name": "output",
            },
        ],
        data=[{"name": "message", "value": "cobertura"}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [
        {"name": "basic_7", "value": 3028, "message": "cobertura"},
        {"name": "basic_15", "value": 7194, "message": "cobertura"},
        {"name": "basic_30", "value": 15720, "message": "cobertura"},
        {"name": "message", "value": "cobertura", "message": "cobertura"},
    ]


def test_multiple_outputs_replicates_message_on_all_entries():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {"node_id": "a", "target_name": "k1", "value": 1, "source_name": "output"},
            {"node_id": "b", "target_name": "k2", "value": 2, "source_name": "output"},
        ],
        data=[{"name": "message", "value": "msg"}],
    )
    result = _normalize([node])
    messages = [e["message"] for e in result[0]["outputs"]]
    assert messages == ["msg", "msg", "msg"]
    assert [e["name"] for e in result[0]["outputs"]] == ["k1", "k2", "message"]


def test_multiple_outputs_message_none():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {"node_id": "a", "target_name": "k1", "value": 10, "source_name": "output"},
        ],
        data=[{"name": "message", "value": None}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [{"name": "k1", "value": 10, "message": None}]


def test_multiple_outputs_filters_none_value():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {
                "node_id": "a",
                "target_name": "k1",
                "value": 100,
                "source_name": "output",
            },
            {
                "node_id": "b",
                "target_name": "k2",
                "value": None,
                "source_name": "output",
            },
            {
                "node_id": "c",
                "target_name": "k3",
                "value": 200,
                "source_name": "output",
            },
        ],
        data=[],
    )
    result = _normalize([node])
    assert [e["name"] for e in result[0]["outputs"]] == ["k1", "k3"]


def test_multiple_outputs_filters_nan_value():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {
                "node_id": "a",
                "target_name": "k1",
                "value": float("nan"),
                "source_name": "output",
            },
            {"node_id": "b", "target_name": "k2", "value": 42, "source_name": "output"},
        ],
        data=[],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [{"name": "k2", "value": 42, "message": None}]


def test_multiple_outputs_single_key():
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {
                "node_id": "a",
                "target_name": "only_key",
                "value": 7,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "solo"}],
    )
    result = _normalize([node])
    assert result[0]["outputs"] == [
        {"name": "only_key", "value": 7, "message": "solo"},
        {"name": "message", "value": "solo", "message": "solo"},
    ]


def test_multiple_outputs_preserves_order():
    keys = ["z", "a", "m"]
    node = _make_node(
        "MultipleOutputs",
        inputs=[
            {"node_id": str(i), "target_name": k, "value": i, "source_name": "output"}
            for i, k in enumerate(keys)
        ],
        data=[],
    )
    result = _normalize([node])
    assert [e["name"] for e in result[0]["outputs"]] == keys


def test_multiple_outputs_empty_inputs():
    node = _make_node("MultipleOutputs", inputs=[], data=[])
    result = _normalize([node])
    assert result[0]["outputs"] == []


# ---------------------------------------------------------------------------
# backward compatibility
# ---------------------------------------------------------------------------


def test_non_terminal_nodes_ignored():
    other = _make_node(
        "Check",
        inputs=[
            {"node_id": "x", "target_name": "v", "value": 99, "source_name": "output"}
        ],
    )
    result = _normalize([other])
    assert result[0]["outputs"] == []


def test_output_and_non_terminal_together():
    output_node = _make_node(
        "Output",
        inputs=[
            {
                "node_id": "a",
                "target_name": "input_value",
                "value": 5,
                "source_name": "output",
            }
        ],
        data=[{"name": "message", "value": "ok"}],
    )
    other = _make_node("Math", inputs=[])
    result = _normalize([output_node, other])
    assert result[0]["outputs"] == [
        {"name": "output", "value": 5, "message": "ok"},
        {"name": "message", "value": "ok", "message": "ok"},
    ]
