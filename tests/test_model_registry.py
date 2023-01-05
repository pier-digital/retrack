import pytest

from retack.utils.model_registry import ModelRegistry


def test_create_model_registry():
    registry = ModelRegistry()
    assert registry._registry == {}


def test_register_model():
    registry = ModelRegistry()
    registry.register("test", str)
    assert registry._registry == {"test": str}


def test_get_model():
    registry = ModelRegistry()
    registry.register("test", str)
    assert registry.get("test") == str


def test_get_model_not_found():
    registry = ModelRegistry()
    registry.register("test", str)
    assert registry.get("test2") is None


def test_contains_model():
    registry = ModelRegistry()
    registry.register("test", str)
    assert "test" in registry


def test_model_already_registered():
    registry = ModelRegistry()
    registry.register("test", str)
    with pytest.raises(ValueError):
        registry.register("test", str)
