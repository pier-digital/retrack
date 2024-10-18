import typing


class Registry:
    """A simple registry for storing value."""

    def __init__(self, case_sensitive: bool = False):
        self._memory = {}
        self._case_sensitive = case_sensitive

    def register(self, key: str, value: typing.Any, overwrite: bool = False):
        """Register an entry."""
        if not self._case_sensitive:
            key = key.lower()

        if key in self._memory and not overwrite:
            raise ValueError(f"{key} is already registered.")

        self._memory[key] = value

    def unregister(self, key: str):
        """Unregister an entry."""
        if not self._case_sensitive:
            key = key.lower()

        self._memory.pop(key, None)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Get a registered entry."""
        if not self._case_sensitive:
            key = key.lower()

        return self._memory.get(key, default)

    @property
    def keys(self) -> typing.List[str]:
        """Return the registry keys."""
        return list(self._memory.keys())

    @property
    def values(self) -> typing.List[typing.Any]:
        """Return the registry values."""
        return list(self._memory.values())

    @property
    def memory(self) -> typing.Dict[str, typing.Any]:
        """Return the registry memory."""
        return self._memory

    def __itter__(self):
        return iter(self._memory)

    def __contains__(self, key: str) -> bool:
        """Check if an entry is registered."""
        if not self._case_sensitive:
            key = key.lower()

        return key in self._memory
