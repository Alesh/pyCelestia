import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_das(node_provider):
    light, auth_token = await node_provider("light-0")
    client = Client(port=light.port["26658/tcp"])

    async with client.connect(auth_token) as api:
        await api.das.wait_catch_up()
        assert (await api.das.sampling_stats()).catch_up_done
