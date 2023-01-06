import typing

from retack.engine.payload_manager import PayloadManager
from retack.parser import Parser


class Runner:
    def __init__(self, parser: Parser):
        self._parser = parser
        self._payload_manager = PayloadManager(
            self._parser.get_element_by_name("Input")
        )

    @property
    def payload_manager(self) -> PayloadManager:
        return self._payload_manager

    def __call__(self, payload: typing.Union[dict, list]):
        return self.payload_manager.validate(payload)
