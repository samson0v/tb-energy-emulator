from abc import abstractmethod
from typing import Any


class Storage:
    def __init__(self, config):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def set_value(self, value: Any) -> None:
        pass

    @abstractmethod
    def get_value(self, key: str) -> Any:
        pass
