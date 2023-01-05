from retack.models.inputs import InputModel
from retack.utils.model_registry import ModelRegistry

model_registry = ModelRegistry()

model_registry.register("Input", InputModel)

__all__ = ["model_registry"]
