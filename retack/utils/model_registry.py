import typing

import pydantic


class ModelRegistry:
    """A registry for models.

    This registry keeps track of all models that are registered with it.
    It is used to provide a mapping from model names to model classes.
    """

    def __init__(self, case_sensitive: bool = False):
        self._registry = {}
        self._case_sensitive = case_sensitive

    def register(self, name: str, model_cls: typing.Type[pydantic.BaseModel]):
        """Register a model.

        Args:
            name: The name of the model.
            model_cls: The model class.
        """
        if not self._case_sensitive:
            name = name.lower()

        if name in self._registry:
            raise ValueError(f"Model {name} is already registered.")

        self._registry[name] = model_cls

    def get(
        self, name: str, default: typing.Any = None
    ) -> typing.Type[pydantic.BaseModel]:
        """Get a model class.

        Args:
            name: The name of the model.
            default: The default value to return if the model is not registered.

        Returns:
            The model class.
        """
        if not self._case_sensitive:
            name = name.lower()

        return self._registry.get(name, default)

    def __contains__(self, name: str) -> bool:
        """Check if a model is registered."""
        if not self._case_sensitive:
            name = name.lower()

        return name in self._registry
