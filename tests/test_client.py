import pytest

from celestia.utils import start_node, show_token


@pytest.fixture(scope='session')
def auth_token():
    result = show_token()
    if not result:
        start_node()
        result = show_token()
    return result


@pytest.mark.asyncio
async def test_client(auth_token):
    assert auth_token
    # async with Client(auth_token) as api:
    #     address = await api.state.AccountAddress()
    #     balance = await api.state.Balance()
    #     assert address and balance.amount
