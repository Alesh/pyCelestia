import asyncio

from celestia.node_api import Client


async def test_graceful_close_subscribing(node_provider):
    result = []
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])
    height_deserializer = lambda data: int(data["header"]["height"])

    async with client.connect(auth_token) as api:
        start_height = await api.header.local_head(deserializer=height_deserializer)

    async def subscriber():
        try:
            async with client.connect(auth_token) as api:
                async with asyncio.timeout(30):
                    async for height in api.header.subscribe(deserializer=height_deserializer):
                        result.append(height)
        except asyncio.CancelledError:
            pass

    subscriber_task = asyncio.create_task(subscriber())

    async with asyncio.timeout(30):
        while True:
            if len(result) == 3:
                subscriber_task.cancel()
                await subscriber_task  # This is important!
                break
            await asyncio.sleep(0.1)

    assert start_height + 3 == result[-1]
    assert len(result) == 3
