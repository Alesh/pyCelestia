import json
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from dataclasses import is_dataclass, asdict
from urllib.parse import urlparse

import _jsonrpc
from _jsonrpc import RPC
from celestia.types import Base64
from .blob import BlobClient
from .das import DasClient
from .fraud import FraudClient
from .header import HeaderClient
from .p2p import P2PClient
from .share import ShareClient
from .state import StateClient


class NodeAPI:
    """Celestia node API"""

    def __init__(self, rpc: RPC):
        self._rpc = rpc

    @property
    def state(self):
        return StateClient(self._rpc)

    @property
    def blob(self):
        return BlobClient(self._rpc)

    @property
    def header(self):
        return HeaderClient(self._rpc)

    @property
    def p2p(self):
        return P2PClient(self._rpc)

    @property
    def das(self):
        return DasClient(self._rpc)

    @property
    def fraud(self):
        return FraudClient(self._rpc)

    @property
    def share(self):
        return ShareClient(self._rpc)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, Base64):
            return str(obj)
        return super().default(obj)


class Client(_jsonrpc.Client):
    """Celestia Node API client"""

    def __init__(
        self,
        url: str = None,
        /,
        *,
        auth_token: str = None,
        host: str = "localhost",
        port: int = 26658,
    ):
        pr = urlparse(url or f"ws://{host}:{port}")
        if pr.scheme not in ("ws", "wss"):
            raise ValueError("Unsupported URL scheme, must be ws or wss")
        url = f"{pr.scheme}://{pr.hostname}:{pr.port or port}"
        super().__init__(url, auth_token=auth_token)
        self.errors_map = dict(
            (rpc_err, ValueError)
            for rpc_err in [
                "unmarshaling params",
                "equal to 0",
                "given height is from the future",
                "invalid range",
                "height must be bigger than zero",
                "dial to self attempted",
                "gater disallows connection to peer",
                "notfound desc = delegation with delegator",
                "unknown desc = failed to execute message; message index: 0: invalid shares amount:",
                "cannot redelegate to the same validator",
                "too many unbonding delegation entries for (delegator, validator) tuple",
                "redelegation not found for delegator address",
                "too many redelegation entries for (delegator, src-validator, dst-validator)",
                "datastore: key not found",
                "reserved namespace",
                "invalid namespace length",
                "invalid data size",
                "blob size mismatch",
                "unsupported share version",
                "zero blob size",
                "no blobs",
                "invalid blob signer",
                "invalid namespace type",
            ]
        )

    def connect(
        self, auth_token: str = None, /, response_timeout: float = 180, **_
    ) -> AbstractAsyncContextManager[NodeAPI]:
        """Creates and return connection context manager."""
        headers = []
        if auth_token := auth_token or self.options.get("auth_token"):
            headers.append(("Authorization", f"Bearer {auth_token}"))

        @asynccontextmanager
        async def connect_context():
            async with super(Client, self).connect(
                additional_headers=headers,
                errors_map=self.errors_map,
                response_timeout=response_timeout,
                json_encoder=JSONEncoder,
            ) as rpc:
                yield NodeAPI(rpc)

        return connect_context()
