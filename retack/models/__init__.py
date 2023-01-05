from retack.models.inputs import InputModel
from retack.models.start import StartModel
from retack.utils.model_registry import ModelRegistry

model_registry = ModelRegistry()

model_registry.register("Input", InputModel)
model_registry.register("Start", StartModel)

__all__ = ["model_registry"]
