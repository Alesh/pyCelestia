import typing as t
import uuid
from dataclasses import asdict, is_dataclass
from http.client import HTTPException

from ajsonrpc.core import JSONRPC20Request, JSONRPC20Response, JSONRPC20Error
from httpx import AsyncClient, Headers


class Error(HTTPException):
    """ Base class for exceptions in this module.
    """


class _ReqBuilder:
    def __init__(self,
                 resolver: t.Callable[[str, tuple[t.Any, ...]], t.Awaitable[t.Any]],
                 items: tuple[str, ...] = ()):
        self.__resolver = resolver
        self.__items = items

    def __call__(self, *args) -> t.Any:
        method_name = '.'.join(self.__items)
        return self.__resolver(method_name, args)

    def __getattr__(self, name: str):
        return _ReqBuilder(self.__resolver, self.__items + (name,))


class Client:
    """ Celestia DA client
    """
    BASE_URL = 'http://localhost:26658/'

    def __init__(self, auth_token: str, *, base_url: str = None, timeout: float = 90, **opts: t.Any):
        headers = Headers({'Authorization': f'Bearer {auth_token}'})
        self.opts = dict(opts, headers=headers, base_url=(base_url or Client.BASE_URL), timeout=timeout)

    async def __aenter__(self):
        async_client = AsyncClient(**self.opts)

        async def resolver(method_name, args):
            params = {}
            args = [asdict(arg) if is_dataclass(args) else arg for arg in args]
            req = JSONRPC20Request(method_name, args, id=str(uuid.uuid4()))
            resp = await async_client.post('/', json=req.body)
            try:
                params = resp.json()
                assert params.pop('jsonrpc') == '2.0'
            except Exception as exc:
                raise Error(500, str(exc))
            if resp.status_code >= 400:
                if 'error' in params:
                    rpc_error = JSONRPC20Error(**params['error'])
                    raise Error(rpc_error.code, rpc_error.message)
                raise Error(resp.status_code, resp.text)
            resp = JSONRPC20Response(**params)
            return resp.result

        return _ReqBuilder(resolver)

    async def __aexit__(self, *exec_info):
        pass
