import asyncio
import typing as t
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from json import JSONEncoder
from urllib.parse import urlparse

from websockets import Headers
from websockets.asyncio.client import connect, ClientConnection

from .abc import Transport as AbcTransport, Wrapper
from .executor import RPC


class Client:
    """WS JSON-RPC Client"""

    def __init__(self, url: str, **options: t.Any):
        pr = urlparse(url)
        if pr.scheme not in ("ws", "wss"):
            raise ValueError("Unsupported URL scheme, must be ws or wss")
        self.options = dict(options, url=url)

    def connect(
        self,
        errors_map: dict[str, t.Type[Exception]] = None,
        additional_headers: Headers | t.Mapping[str, str] | t.Iterable[tuple[str, str]] = None,
        json_encoder: t.Type[JSONEncoder] | None = None,
        response_timeout: float = 180,
    ) -> AbstractAsyncContextManager[RPC]:
        url = self.options["url"]
        errors_map_ = errors_map or {}

        async def listener(connection: ClientConnection, handlers: AbcTransport):
            try:
                async for message in connection:
                    handlers.on_message(message)
            except asyncio.CancelledError:
                handlers.on_close(None)
            except Exception as exc:
                handlers.on_close(exc)

        @asynccontextmanager
        async def connect_context():
            try:
                listener_task = None
                async with connect(url, additional_headers=additional_headers) as connection:

                    class Transport(AbcTransport):
                        errors_map = dict(**errors_map_)

                        async def send(self, message: str):
                            await connection.send(message)

                    transport = Transport()
                    rpc = RPC(transport, json_encoder, response_timeout)
                    listener_task = asyncio.create_task(listener(connection, transport))
                    yield rpc
            finally:
                if listener_task and not listener_task.done():
                    listener_task.cancel()
                    await listener_task

        return connect_context()
