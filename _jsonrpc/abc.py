import logging
import typing as t
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

logger = logging.Logger("WS JSON-RPC")


class Transport(ABC):
    on_message: t.Callable[[bytes | str], None]
    on_close: t.Callable[[Exception | None], None]

    @abstractmethod
    async def send(self, message: str) -> None:
        """Send a message to the connection."""

    @property
    @abstractmethod
    def errors_map(self) -> dict[str, t.Type[Exception]]:
        """Return a mapping of RPC error message (part of the message) to error classes to be raised."""


class RPCExecutor(ABC):

    @abstractmethod
    async def call(
        self,
        method: str,
        params: tuple[t.Any, ...] = None,
        deserializer: t.Callable[[t.Any], t.Any] = None,
    ) -> t.Any | None:
        """This method must implement calling an RPC method and returning the result."""

    @abstractmethod
    async def iter(
        self,
        method: str,
        params: tuple[t.Any, ...] = None,
        deserializer: t.Callable[[t.Any], t.Any] = None,
    ) -> AsyncGenerator[t.Any]:
        """This method must implement creating an `RPC` subscription and returning
        an asynchronous iterator that returns the incoming subscription results.
        """


class Wrapper:
    def __init__(self, rpc: RPCExecutor):
        self._rpc = rpc
