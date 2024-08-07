import asyncio

import pytest
import pytest_asyncio

from celestia.models import Balance
from celestia.rpc import Client
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
            async with Client(auth_token) as api:
                assert await api.state.AccountAddress()
                assert await api.state.Balance()
                return auth_token
        except:
            if cnt == 0:
                raise
            await asyncio.sleep(6 - cnt)
            cnt -= 1


@pytest.mark.asyncio
async def test_client(auth_token):
    assert auth_token
    async with Client(auth_token) as api:
        result = await api.state.AccountAddress()
        assert result
        result = Balance(**(await api.state.Balance()))
        assert result.value
