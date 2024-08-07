import asyncio

import pytest
import pytest_asyncio

from celestia import Client, rpc
from celestia.models import Balance
from celestia.utils import show_token, stop_node, start_node, first_container_id


@pytest.fixture(scope='session')
def container_id():
    if not first_container_id():
        stop_node()
        start_node()
        yield first_container_id()
        stop_node()
    else:
        yield first_container_id()


@pytest_asyncio.fixture()
async def auth_token(container_id):
    assert container_id
    cnt = 5
    auth_token = show_token()
    while cnt:
        try:
            async with rpc.Client(auth_token) as api:
                assert await api.state.AccountAddress()
                assert await api.state.Balance()
                return auth_token
        except:
            if cnt == 0:
                raise
            await asyncio.sleep(6 - cnt)
            cnt -= 1


@pytest.mark.asyncio
async def test_rpc_client(auth_token):
    assert auth_token
    async with rpc.Client(auth_token) as api:
        result = await api.state.AccountAddress()
        assert result
        result = Balance(**(await api.state.Balance()))
        assert result.value


@pytest.mark.asyncio
async def test_client(auth_token):
    assert auth_token
    client = Client(auth_token)
    address = await client.account_address()
    assert address and len(address) == 47 and address.startswith('celestia')
    balance = await client.account_balance()
    assert balance.value


@pytest.mark.asyncio
async def test_cm_client(auth_token):
    assert auth_token
    async with Client(auth_token) as client:
        address = await client.account_address()
        assert address and len(address) == 47 and address.startswith('celestia')
        balance = await client.account_balance()
        assert balance.value


@pytest.mark.asyncio
async def test_send_blob(auth_token):
    assert auth_token
    async with Client(auth_token) as client:
        balance = await client.account_balance()
        assert balance.value
        bsr = await client.blob_submit(0x100500, b'Hello, Celestia!')
        assert bsr.height
        assert isinstance(bsr.commitment, bytes)
