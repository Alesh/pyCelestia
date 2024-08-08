import asyncio
import typing as t

import pytest
import pytest_asyncio

from celestia import Client, rpc
from celestia.models import Balance, Blob, Namespace
from celestia.utils.scripts import show_token, stop_node, start_node, first_container_id


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
        bsr = await client.submit_blob(0x100500, b'Hello, Celestia!')
        assert bsr.height
        assert isinstance(bsr.commitment, bytes)

    async with Client(auth_token) as client:
        blob = await client.get_blob(bsr.height, 0x100500, bsr.commitment)
        assert blob.commitment == bsr.commitment
        assert blob.data == b'Hello, Celestia!'

    async with Client(auth_token) as client:
        blobs = await client.get_blobs(bsr.height, 0x100500)
        assert len(blobs) == 1
        assert blobs[0].commitment == bsr.commitment
        assert blobs[0].data == b'Hello, Celestia!'


@pytest.mark.asyncio
async def test_send_blobs_api(auth_token):
    assert auth_token
    default_gas_price = -1.0
    blobs = [
        Blob(0x100500, b'Hello, Celestia!'),
        Blob(0x100500, b'Hello, Alesh!'),
        Blob(0x100501, b'Hello, Word!'),
    ]
    async with Client(auth_token) as client:
        height = await client.api.blob.Submit(blobs, default_gas_price)

    async with Client(auth_token) as client:
        result = await client.get_blobs(height, 0x100500, 0x100501)
        assert len(result) == 3
        assert tuple(sorted(blob.data for blob in result)) == (b'Hello, Alesh!', b'Hello, Celestia!', b'Hello, Word!')

    async with Client(auth_token) as client:
        result = await client.api.blob.GetProof(height, Namespace(0x100500), result[0].commitment)
        assert result


@pytest.mark.asyncio
async def test_get_blob_empty(auth_token):
    assert auth_token
    async with Client(auth_token) as client:
        blob = await client.get_blob(1, 0x100500, b'XXX')
        assert blob is None
    async with Client(auth_token) as client:
        blobs = await client.get_blobs(1, 0x100500)
        assert isinstance(blobs, t.Iterable) and len(blobs) == 0


@pytest.mark.asyncio
async def test_other(auth_token):
    assert auth_token
    async with Client(auth_token) as client:
        result = await client.api.p2p.Info()
        assert result