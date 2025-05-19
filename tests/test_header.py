import asyncio

import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_header(node_provider):
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])

    async with client.connect(auth_token) as api:
        local_head = await api.header.local_head()
        network_head = await api.header.network_head()
        local_height = local_head.header.height
        local_hash = local_head.commit.block_id.hash
        assert local_height <= network_head.header.height

        head = await api.header.get_by_hash(
            "4D3818BC5D3BE8E529C953C8654BD4243A2CD28BD1599DBF0ED4DD44C24F6D33"
        )
        assert head is None
        head = await api.header.get_by_hash(local_hash)
        assert local_head == head

        head = await api.header.get_by_height(local_height)
        assert local_head == head

        heads = await api.header.get_range_by_height(
            await api.header.get_by_height(int(local_height) - 5), local_height
        )
        assert len(heads) == 4

        state1 = await api.header.sync_state()

        await api.header.wait_for_height(state1.height + 1)

        state2 = await api.header.sync_state()
        assert state1.height <= state2.height


@pytest.mark.asyncio
async def test_header_exceptions(node_provider):
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])
    async with client.connect(auth_token) as api:
        local_head = await api.header.local_head()
        local_height = local_head.header.height

        with pytest.raises(ValueError):
            await api.header.get_by_height(18446744073709551615)
        with pytest.raises(ValueError):
            await api.header.get_by_height(0)
        with pytest.raises(ValueError):
            await api.header.get_by_height(-1)

        with pytest.raises(ValueError):
            await api.header.get_range_by_height(
                await api.header.get_by_height(local_height), int(local_height) - 5
            )

        with pytest.raises(ValueError):
            await api.header.wait_for_height(0)
        with pytest.raises(ValueError):
            await api.header.wait_for_height(-1)


@pytest.mark.asyncio
async def test_header_subscribe(node_provider):
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])
    result = []

    async with client.connect(auth_token) as api:
        async with asyncio.timeout(30):
            async for header in api.header.subscribe():
                result.append(header)
                if len(result) == 3:
                    break
    assert len(result) == 3
