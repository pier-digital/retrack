import typing


class Registry:
    """A simple registry for storing data."""

    def __init__(self, case_sensitive: bool = False):
        self._data = {}
        self._case_sensitive = case_sensitive

    def register(self, name: str, data: typing.Any, overwrite: bool = False):
        """Register an entry."""
        if not self._case_sensitive:
            name = name.lower()

        if name in self._data and not overwrite:
            raise ValueError(f"{name} is already registered.")

        self._data[name] = data

    def unregister(self, name: str):
        """Unregister an entry."""
        if not self._case_sensitive:
            name = name.lower()

        self._data.pop(name, None)

    def get(self, name: str, default: typing.Any = None) -> typing.Any:
        """Get a registered entry."""
        if not self._case_sensitive:
            name = name.lower()

        return self._data.get(name, default)

    @property
    def data(self) -> typing.Dict[str, typing.Any]:
        """Return the registry data."""
        return self._data

    def __itter__(self):
        return iter(self._data)

    def __contains__(self, name: str) -> bool:
        """Check if an entry is registered."""
        if not self._case_sensitive:
            name = name.lower()

        return name in self._data
