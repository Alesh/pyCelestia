import typing as t
from contextlib import AbstractAsyncContextManager

from . import rpc
from ._celestia import default_gas_price
from .models import Balance, BlobSubmitResult, Namespace, Blob, Commitment, Base64


class Client(AbstractAsyncContextManager):
    """ Python client for working with the Celestia DA network.
    """

    def __init__(self, auth_token: str, /, **httpx_opts: t.Any):
        self._client_factory = lambda: rpc.Client(auth_token, **httpx_opts)
        self._api = self._rpc_client = None

    async def __aenter__(self) -> t.Self:
        self._rpc_client = self._client_factory()
        self._api = await self._rpc_client.__aenter__()
        return self

    async def __aexit__(self, *exc_info) -> None:
        self._rpc_client.__aexit__(*exc_info)
        self.api = None

    async def account_address(self) -> str:
        """ Retrieves the address of the node's account/signer. """
        if self._api is None:
            async with self._client_factory() as api:
                return await api.state.AccountAddress()
        return await self._api.state.AccountAddress()

    async def account_balance(self) -> Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer. """
        if self._api is None:
            async with self._client_factory() as api:
                return Balance(**(await api.state.Balance()))
        return Balance(**(await self._api.state.Balance()))

    async def blob_submit(self, namespace: Namespace | str | int, blob: Base64 | bytes) -> BlobSubmitResult:
        """ Sends a Blob and reports the block height at which it was included on and its commitment.
        """
        gas_price = default_gas_price()
        blob = Blob(namespace, blob)
        if self._api is None:
            async with self._client_factory() as api:
                height = await api.blob.Submit([blob], gas_price)
        else:
            height = await self._api.blob.Submit([blob], gas_price)
        return BlobSubmitResult(height, blob.commitment)
