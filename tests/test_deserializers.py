import pytest
from pydantic import BaseModel

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_deserializers(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])

    class CustomBalanceModel(BaseModel):
        amount: int
        denom: str

    async with client.connect(auth_token) as api:
        last_height = await api.header.local_head(deserializer=lambda data: int(data['header']['height']))
        assert isinstance(last_height, int)

        balance = await api.state.balance(deserializer=CustomBalanceModel.model_validate)
        assert isinstance(balance.amount, int)
        assert balance.amount

        with pytest.raises(TypeError):
            await api.state.balance(CustomBalanceModel.model_validate)
