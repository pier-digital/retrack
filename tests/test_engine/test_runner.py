import json

import pytest

from retrack import Parser, Runner


@pytest.fixture
def age_negative_json() -> dict:
    with open("tests/resources/age-negative.json", "r") as f:
        return json.load(f)


def test_age_negative(age_negative_json):
    parser = Parser(age_negative_json)
    runner = Runner(parser)
    in_values = [10, -10, 18, 19, 100]
    out_values = runner([{"age": val} for val in in_values])

    assert out_values == [
        {"message": "underage", "output": False},
        {"message": "invalid age", "output": False},
        {"message": "valid age", "output": True},
        {"message": "valid age", "output": True},
        {"message": "valid age", "output": True},
    ]
