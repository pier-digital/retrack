import pytest

from retack.utils.registry import Registry


def test_create_registry():
    registry = Registry()
    assert registry.data == {}


def test_register_model():
    registry = Registry()
    registry.register("test", str)
    assert registry.data == {"test": str}


def test_get_model():
    registry = Registry()
    registry.register("test", str)
    assert registry.get("test") == str


def test_get_model_not_found():
    registry = Registry()
    registry.register("test", str)
    assert registry.get("test2") is None


def test_contains_model():
    registry = Registry()
    registry.register("test", str)
    assert "test" in registry


def test_model_already_registered():
    registry = Registry()
    registry.register("test", str)
    with pytest.raises(ValueError):
        registry.register("test", str)
