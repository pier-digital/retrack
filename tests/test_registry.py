import pytest

from retrack.utils.registry import Registry


def test_create_registry():
    registry = Registry()
    assert registry.data == {}


def test_register_model():
    registry = Registry()
    registry.register("test", "example")
    assert registry.data == {"test": "example"}


def test_get_model():
    registry = Registry()
    registry.register("test", "example")
    assert registry.get("test") == "example"


def test_get_model_not_found():
    registry = Registry()
    registry.register("test", "example")
    assert registry.get("test2") is None


def test_contains_model():
    registry = Registry()
    registry.register("test", "example")
    assert "test" in registry


def test_model_already_registered():
    registry = Registry()
    registry.register("test", "example")
    with pytest.raises(ValueError):
        registry.register("test", "example")
