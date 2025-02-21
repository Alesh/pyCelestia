from collections.abc import AsyncIterator
from functools import wraps
from typing import Callable

from celestia.types.header import ExtendedHeader, State
from ._RPC import Wrapper


def handle_header_error(func):
    """ Decorator to handle blob-related errors."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionError as e:
            if 'header: not found' in e.args[1].body['message'].lower():
                return None
            raise

    return wrapper


class HeaderClient(Wrapper):
    """ Client for interacting with Celestia's Header API."""

    @handle_header_error
    async def get_by_hash(self, header_hash: str, *, deserializer: Callable | None = None) -> ExtendedHeader | None:
        """ Returns the header of the given hash from the node's header store.

        Args:
            header_hash (str): The hash of the header to retrieve.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Returns:
            ExtendedHeader | None: The retrieved header if found, otherwise None.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        return await self._rpc.call("header.GetByHash", (header_hash,), deserializer)

    async def get_by_height(self, height: int, *, deserializer: Callable | None = None) -> ExtendedHeader:
        """ Returns the ExtendedHeader at the given height if it is currently available.

        Args:
            height (int): The height of the header.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Returns:
            ExtendedHeader: The retrieved header.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        return await self._rpc.call("header.GetByHeight", (int(height),), deserializer)

    async def get_range_by_height(self, range_from: ExtendedHeader, range_to: int, *,
                                  deserializer: Callable | None = None) -> list[ExtendedHeader]:
        """ Returns the given range (from:to) of ExtendedHeaders from the node's header store
        and verifies that the returned headers are adjacent to each other.

        Args:
            range_from (ExtendedHeader): The starting header.
            range_to (int): The height of the last header in the range.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[ExtendedHeader]: A list of retrieved headers.
        """

        def deserializer_(result):
            if result is not None:
                return [ExtendedHeader(**kwargs) for kwargs in result]

        deserializer = deserializer if deserializer is not None else deserializer_

        return await self._rpc.call("header.GetRangeByHeight", (range_from, int(range_to)), deserializer)

    async def local_head(self, *, deserializer: Callable | None = None) -> ExtendedHeader:
        """ Returns the ExtendedHeader of the chain head.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Returns:
            ExtendedHeader: The latest known header of the local node.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        return await self._rpc.call("header.LocalHead", (), deserializer)

    async def network_head(self, *, deserializer: Callable | None = None) -> ExtendedHeader:
        """ Provides the Syncer's view of the current network head.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Returns:
            ExtendedHeader: The latest known header of the network.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        return await self._rpc.call("header.NetworkHead", (), deserializer)

    async def subscribe(self, *, deserializer: Callable | None = None) -> AsyncIterator[ExtendedHeader | None]:
        """ Subscribes to recent ExtendedHeaders from the network.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Yields:
            ExtendedHeader | None: The latest headers as they become available.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        async for subs_header_result in self._rpc.iter("header.Subscribe", (), deserializer):
            if subs_header_result is not None:
                yield subs_header_result

    async def sync_state(self, *, deserializer: Callable | None = None) -> State:
        """ Returns the current state of the header Syncer.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.State.deserializer`.

        Returns:
           State: The current synchronization state.
        """

        deserializer = deserializer if deserializer is not None else State.deserializer

        return await self._rpc.call("header.SyncState", (), deserializer)

    async def sync_wait(self) -> None:
        """ Blocks until the header Syncer is synced to network head.

        Returns:
            None
        """
        return await self._rpc.call("header.SyncWait")

    async def wait_for_height(self, height: int, *, deserializer: Callable | None = None) -> ExtendedHeader:
        """ Blocks until the header at the given height has been processed
        by the store or context deadline is exceeded.

        Args:
            height (int): The height of the header to wait for.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.header.ExtendedHeader.deserializer`.

        Returns:
            ExtendedHeader: The retrieved header once available.
        """

        deserializer = deserializer if deserializer is not None else ExtendedHeader.deserializer

        return await self._rpc.call("header.WaitForHeight", (height,), deserializer)
