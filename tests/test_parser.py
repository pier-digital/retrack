import pytest

from retack.parser import Parser


@pytest.mark.parametrize(
    "input_data,expected_output_data",
    [
        (
            {
                "nodes": {
                    "1": {
                        "id": 3,
                        "data": {"name": "age"},
                        "inputs": {
                            "input_void": {
                                "connections": [
                                    {"node": 0, "output": "output_void", "data": {}}
                                ]
                            }
                        },
                        "outputs": {
                            "output_0": {
                                "connections": [
                                    {"node": 5, "input": "input_0", "data": {}}
                                ]
                            }
                        },
                        "name": "Input",
                    }
                }
            },
            {
                "1": {
                    "id": "1",
                    "data": {"name": "age", "default": None},
                    "inputs": {
                        "input_void": {
                            "connections": [{"node": "0", "output": "output_void"}]
                        }
                    },
                    "outputs": {
                        "output_0": {"connections": [{"node": "5", "input": "input_0"}]}
                    },
                }
            },
        )
    ],
)
def test_parser_extract(input_data, expected_output_data):
    parser = Parser(input_data)
    assert parser.data == expected_output_data
    assert parser.tokens == {"Input": ["1"]}


def test_parser_with_unknown_node():
    with pytest.raises(ValueError):
        Parser({"nodes": {"1": {"name": "Unknown"}}}, unknown_node_error=True)


def test_parser_invalid_input_data():
    with pytest.raises(TypeError):
        Parser("invalid data")


def test_parser_no_nodes():
    with pytest.raises(ValueError):
        Parser({})


def test_parser_invalid_nodes():
    with pytest.raises(TypeError):
        Parser({"nodes": "invalid nodes"})


def test_parser_node_no_name():
    with pytest.raises(ValueError):
        Parser({"nodes": {"1": {}}})


def test_parser_node_invalid_name():
    with pytest.raises(TypeError):
        Parser({"nodes": {"1": {"name": 1}}})
