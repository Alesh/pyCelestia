from dataclasses import asdict

import pytest

from celestia.node_api import Client
from celestia.node_api.p2p import Connectedness, Reachability


@pytest.mark.asyncio
async def test_p2p(node_provider):
    bridge1, auth_token1 = await node_provider("bridge-0")
    bridge2, auth_token2 = await node_provider("bridge-1")
    bridge3, auth_token3 = await node_provider("bridge-2")
    client1 = Client(port=bridge1.port["26658/tcp"])
    client2 = Client(port=bridge2.port["26658/tcp"])
    client3 = Client(port=bridge3.port["26658/tcp"])

    async with client1.connect(auth_token1) as api:
        info1 = await api.p2p.info()

    async with client2.connect(auth_token2) as api:
        info2 = await api.p2p.info()

    async with client3.connect(auth_token3) as api:
        info3 = await api.p2p.info()

        assert info1.id != info2.id != info3.id

        assert Connectedness.CONNECTED.value == await api.p2p.connectedness(info1.id)
        assert Connectedness.CONNECTED.value == await api.p2p.connectedness(info2.id)

        await api.p2p.close_peer(info1.id)
        assert Connectedness.NOT_CONNECTED.value == await api.p2p.connectedness(info1.id)
        assert info1.id not in await api.p2p.peers()
        await api.p2p.connect(info1)
        assert Connectedness.CONNECTED.value == await api.p2p.connectedness(info1.id)
        assert info1.id in await api.p2p.peers()

        await api.p2p.block_peer(info2.id)
        assert Connectedness.NOT_CONNECTED.value == await api.p2p.connectedness(info2.id)
        assert info2.id in await api.p2p.list_blocked_peers()
        await api.p2p.unblock_peer(info2.id)
        await api.p2p.connect(info2)
        assert Connectedness.CONNECTED.value == await api.p2p.connectedness(info2.id)
        assert info2.id not in await api.p2p.list_blocked_peers()

        one_peer_stats = await api.p2p.bandwidth_for_peer(info1.id)
        assert not all(value == 0 for value in asdict(one_peer_stats).values())
        bad_peer_stats = await api.p2p.bandwidth_for_peer(
            "12D3KooWEhKP6kFF3Ptz14PeJkBXT4RNF8Dbc6LVa4gMbBVeajkQ"
        )
        assert all(value == 0 for value in asdict(bad_peer_stats).values())
        all_peers_stats = await api.p2p.bandwidth_stats()
        assert not all(value == 0 for value in asdict(all_peers_stats).values())

        res_man_stat = await api.p2p.resource_state()

        for keys in res_man_stat.protocols.keys():
            protocol_stats = await api.p2p.bandwidth_for_protocol(keys)
            assert not all(value == 0 for value in asdict(protocol_stats).values())

        bad_protocol_stats = await api.p2p.bandwidth_for_protocol("/qwe/asd/zxc")
        assert all(value == 0 for value in asdict(bad_protocol_stats).values())

        assert not await api.p2p.is_protected(info1.id, "Test tag")
        await api.p2p.protect(info1.id, "Test tag")
        assert await api.p2p.is_protected(info1.id, "Test tag")
        assert not await api.p2p.is_protected(info1.id, "Bad test tag")
        await api.p2p.unprotect(info1.id, "Test tag")
        assert not await api.p2p.is_protected(info1.id, "Test tag")

        assert Reachability.Unknown.value == await api.p2p.nat_status()

        topic = await api.p2p.pub_sub_topics()
        assert len(await api.p2p.pub_sub_peers(topic[0])) != 0
        assert await api.p2p.pub_sub_peers("Bad test topic") is None

        with pytest.raises(ValueError):
            await api.p2p.connect(info3)
        with pytest.raises(ValueError):
            await api.p2p.block_peer(info2.id)
            await api.p2p.connect(info2)
        await api.p2p.unblock_peer(info2.id)
