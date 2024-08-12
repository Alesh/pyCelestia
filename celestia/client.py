import typing as t
from contextlib import AbstractAsyncContextManager

from . import models as m
from . import rpc, errors
from .errors import BlobNotFound
from .models import Balance, BlobSubmitResult, Blob

Base64 = m.Base64 | bytes
Namespace = m.Namespace | bytes | str | int
Commitment = m.Commitment | bytes | str

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

    async def account_balance(self, address: str = None) -> Balance:
        """ Retrieves the current balance of the Celestial Coin for the specified address
        or the node's own account if no address is provided. """
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    result = await (api.state.BalanceForAddress(address) if address else api.state.Balance())
            else:
                result = await (self.api.state.BalanceForAddress(address) if address else self.api.state.Balance())
            return Balance(**result)
        except rpc.Error as exc:
            errors.clarifycator(exc)

    async def submit_blob(self, namespace: Namespace, blob: Base64, gas_price: float = -1.0) -> BlobSubmitResult:
        """ Sends a Blob and reports the block height at which it was included on and its commitment.
        """
        namespace = m.Namespace(namespace)
        blob = Blob(namespace, blob)
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    height = await api.blob.Submit([blob], gas_price)
            else:
                height = await self.api.blob.Submit([blob], gas_price)
            return BlobSubmitResult(height, blob.commitment)
        except rpc.Error as exc:
            errors.clarifycator(exc)

    async def get_blob(self, height: int, namespace: Namespace, commitment: Commitment) -> Blob | None:
        """ Retrieves the blob by commitment under the given namespace and height. """
        namespace = m.Namespace(namespace)
        commitment = m.Commitment(commitment)
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    blob = await api.blob.Get(height, namespace, commitment)
            else:
                blob = await self.api.blob.Get(height, namespace, commitment)
            return Blob(**blob)
        except rpc.Error as exc:
            errors.clarifycator(exc, BlobNotFound)

    async def get_blobs(self, height: int, namespace: Namespace, *namespaces: Namespace) -> t.Sequence[Blob]:
        """ Returns all blobs at the given height under the given namespaces. """
        blobs = []
        namespaces = [m.Namespace(namespace) for namespace in (namespace, *namespaces)]
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    blobs = await api.blob.GetAll(height, namespaces)
            else:
                blobs = await self.api.blob.GetAll(height, namespaces)
        except rpc.Error as exc:
            errors.clarifycator(exc, BlobNotFound)
        return tuple(Blob(**blob) for blob in blobs)

    async def get_local_load(self) -> tuple[float, int]:
        """ Returns the percentage of the loading local node and
        the height of the latest block in the blockchain network.
        """
        try:
            if self.api is None:
                async with self._client_factory() as api:
                    local = await api.header.LocalHead()
                    network = await api.header.NetworkHead()
            else:
                local = await self.api.header.LocalHead()
                network = await self.api.header.NetworkHead()
            local = int(local['header']['height'])
            network = int(network['header']['height'])
            return round(local / network, 3), network
        except Exception as exc:
            errors.clarifycator(exc)
