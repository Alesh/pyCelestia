import typing as t
from contextlib import AbstractAsyncContextManager

from . import rpc
from .models import Balance, BlobSubmitResult, Namespace, Blob, Commitment, Base64

try:
    from .__version__ import version as __version__
except ImportError:
    pass


class Client(AbstractAsyncContextManager):
    """ Python client for working with the Celestia DA network.
    """

    def __init__(self, auth_token: str, /, **httpx_opts: t.Any):
        self._client_factory = lambda: rpc.Client(auth_token, **httpx_opts)
        self.__api = self._rpc_client = None

    async def __aenter__(self) -> 'Client':
        self._rpc_client = self._client_factory()
        self.__api = await self._rpc_client.__aenter__()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self._rpc_client.__aexit__(*exc_info)
        self.__api = None

    @property
    def api(self) -> rpc.API | None:
        """ Node API entry point"""
        return self.__api

    async def account_address(self) -> str:
        """ Retrieves the address of the node's account/signer. """
        if self.api is None:
            async with self._client_factory() as api:
                return await api.state.AccountAddress()
        return await self.api.state.AccountAddress()

    async def account_balance(self) -> Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer. """
        if self.api is None:
            async with self._client_factory() as api:
                return Balance(**(await api.state.Balance()))
        return Balance(**(await self.api.state.Balance()))

    async def submit_blob(self, namespace: Namespace | bytes | str | int,
                          blob: Base64 | bytes, gas_price: float = -1.0) -> BlobSubmitResult:
        """ Sends a Blob and reports the block height at which it was included on and its commitment.
        """
        blob = Blob(namespace, blob)
        if self.api is None:
            async with self._client_factory() as api:
                height = await api.blob.Submit([blob], gas_price)
        else:
            height = await self.api.blob.Submit([blob], gas_price)
        return BlobSubmitResult(height, blob.commitment)

    async def get_blob(self, height: int, namespace: Namespace | bytes | str | int,
                       commitment: Commitment | bytes | str) -> Blob | None:
        """ Retrieves the blob by commitment under the given namespace and height. """
        namespace = Namespace(namespace)
        commitment = Commitment(commitment)
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    blob = await api.blob.Get(height, namespace, commitment)
            else:
                blob = await self.api.blob.Get(height, namespace, commitment)
            return Blob(**blob)
        except rpc.Error as exc:
            if exc.code != -32001:
                raise exc

    async def get_blobs(self, height: int, namespace: Namespace | bytes | str | int,
                        *namespaces: Namespace | bytes | str | int) -> t.Sequence[Blob]:
        """ Returns all blobs at the given height under the given namespaces. """
        blobs = []
        namespaces = [Namespace(namespace) for namespace in (namespace, *namespaces)]
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    blobs = await api.blob.GetAll(height, namespaces)
            else:
                blobs = await self.api.blob.GetAll(height, namespaces)
        except rpc.Error as exc:
            if exc.code != -32001:
                raise exc
        return tuple(Blob(**blob) for blob in blobs)
