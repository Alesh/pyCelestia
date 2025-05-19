import asyncio
import json
import sys
import typing as t
import uuid
from asyncio import Future
from collections import deque
from collections.abc import AsyncGenerator
from json import JSONEncoder

from ajsonrpc.core import JSONRPC20Response, JSONRPC20Request

from .abc import RPCExecutor, Transport, logger

if sys.version_info[:2] <= (3, 10):
    from async_timeout import timeout as asyncio_timeout

    asyncio.timeout = asyncio_timeout


class RPC(RPCExecutor):
    """RPC encoder / executor / decoder"""

    def __init__(
        self,
        transport: Transport,
        json_encoder: t.Type[JSONEncoder] | None = None,
        timeout: float = 180,
    ):
        self.timeout = timeout
        self.transport = transport
        self.transport.on_message = self.on_transport_response
        self.transport.on_close = self.on_transport_close
        self._pending = dict()  # type: dict[str, Future]
        self._subscriptions = dict()  # type: dict[str, deque[t.Any]]
        self._json_encoder = json_encoder or JSONEncoder

    def on_transport_response(self, message: str):
        message = json.loads(message)
        if "method" in message:
            subscription_id, item = message["params"]
            subscription = self._subscriptions.get(subscription_id, None)
            if subscription is not None:
                subscription.append(item)
        else:
            response = JSONRPC20Response(result=False)
            response.body = message
            if future := self._pending.get(response.id):
                if response.error is not None:
                    error_body = getattr(response.error, "body", None)
                    error_message = error_body.get("message", None).lower() if error_body else None
                    if found := [
                        key for key in self.transport.errors_map.keys() if key in error_message
                    ]:
                        exc_class = self.transport.errors_map[found[0]]
                        future.set_exception(exc_class(error_message))
                    elif error_message is None or error_body is None:
                        future.set_exception(ConnectionError("RPC failed; undefined error"))
                    else:
                        future.set_exception(
                            ConnectionError(f"RPC failed; {error_message}", response.error)
                        )
                else:
                    future.set_result(response.result)
            else:
                logger.warning("Received message with unexpected ID.")

    def on_transport_close(self, exc: Exception = None):
        if exc:
            e = ConnectionError(f"RPC failed; transport closed by error {exc}")
            exc = e.with_traceback(exc.__traceback__)

        for future in self._pending.values():
            if exc:
                future.set_exception(exc)
            else:
                future.set_exception(ConnectionError("RPC failed; transport closed"))

        for id in tuple(self._subscriptions.keys()):
            subscription = self._subscriptions.pop(id)
            if exc:
                subscription.append(exc)

    async def call(
        self,
        method: str,
        params: tuple[t.Any, ...] = None,
        deserializer: t.Callable[[t.Any], t.Any] = None,
    ) -> t.Any | None:
        params = params or ()
        deserializer = deserializer or (lambda a: a)
        id = str(uuid.uuid4())
        request = JSONRPC20Request(method, params, id)
        await self.transport.send(json.dumps(request.body, cls=self._json_encoder))
        future = self._pending[id] = Future()
        future.add_done_callback(lambda _: self._pending.pop(id, None))
        async with asyncio.timeout(self.timeout):
            result = await future
            return deserializer(result)

    async def iter(
        self,
        method: str,
        params: tuple[t.Any, ...] = None,
        deserializer: t.Callable[[t.Any], t.Any] = None,
    ) -> AsyncGenerator[t.Any]:
        deserializer = deserializer or (lambda a: a)
        subscription_id = await self.call(method, params)
        try:
            subscription = self._subscriptions[subscription_id] = deque()
            while subscription_id in self._subscriptions:
                if len(subscription):
                    item = subscription.popleft()
                    if isinstance(item, Exception):
                        raise item
                    yield deserializer(item)
                else:
                    await asyncio.sleep(0.1)
        finally:
            self._subscriptions.pop(subscription_id, None)
