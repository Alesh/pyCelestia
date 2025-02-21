from typing import Callable

from celestia.types.p2p import BandwidthStats, Connectedness, AddrInfo, Reachability, ResourceManagerStat
from ._RPC import Wrapper


class P2PClient(Wrapper):
    """ Client for interacting with Celestia's P2P API."""

    async def bandwidth_for_peer(self, peer_id: str, *, deserializer: Callable | None = None) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics associated with the given peer.ID.
        The metrics returned include all traffic sent / received for the peer, regardless of protocol.

        Args:
            peer_id (str): The ID of the peer.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.BandwidthStats.deserializer`.

        Returns:
            BandwidthStats: Bandwidth statistics for the given peer.
        """

        deserializer = deserializer if deserializer is not None else BandwidthStats.deserializer

        return await self._rpc.call("p2p.BandwidthForPeer", (peer_id,), deserializer)

    async def bandwidth_for_protocol(self, protocol_id: str, *, deserializer: Callable | None = None) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics associated with the given protocol.ID.

        Args:
            protocol_id (str): The protocol ID.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.BandwidthStats.deserializer`.

        Returns:
            BandwidthStats: Bandwidth statistics for the given protocol.
        """

        deserializer = deserializer if deserializer is not None else BandwidthStats.deserializer

        return await self._rpc.call("p2p.BandwidthForProtocol", (protocol_id,), deserializer)

    async def bandwidth_stats(self, *, deserializer: Callable | None = None) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics for all data sent/received by the local peer,
        regardless of protocol or remote peer IDs.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.BandwidthStats.deserializer`.

        Returns:
            BandwidthStats: Overall bandwidth statistics.
        """

        deserializer = deserializer if deserializer is not None else BandwidthStats.deserializer

        return await self._rpc.call("p2p.BandwidthStats", (), deserializer)

    async def block_peer(self, peer_id: str) -> None:
        """ Adds a peer to the set of blocked peers and closes any existing connection to that peer.

        Args:
            peer_id (str): The ID of the peer to block.
        """
        await self._rpc.call("p2p.BlockPeer", (peer_id,))

    async def close_peer(self, peer_id: str) -> None:
        """ Closes the connection to a given peer.

        Args:
            peer_id (str): The ID of the peer to disconnect from.
        """
        await self._rpc.call("p2p.ClosePeer", (peer_id,))

    async def connect(self, address: AddrInfo) -> None:
        """ Ensures there is a connection between this host and the peer with given peer.

        Args:
            address (AddrInfo): Address information of the peer.
        """
        await self._rpc.call("p2p.Connect", (address,))

    async def connectedness(self, peer_id: str) -> Connectedness:
        """ Returns a state signaling connection capabilities.

        Args:
            peer_id (str): The ID of the peer.

        Returns:
            Connectedness: Connection status with the peer.
        """
        return await self._rpc.call("p2p.Connectedness", (peer_id,))

    async def info(self, *, deserializer: Callable | None = None) -> AddrInfo:
        """ Returns address information about the host.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.AddrInfo.deserializer`.

        Returns:
            AddrInfo: Address information of the local peer.
        """

        deserializer = deserializer if deserializer is not None else AddrInfo.deserializer

        return await self._rpc.call("p2p.Info", (), deserializer)

    async def is_protected(self, peer_id: str, tag: str) -> bool:
        """ Returns whether the given peer is protected.

        Args:
            peer_id (str): The ID of the peer.
            tag (str): Protection tag.

        Returns:
            bool: True if the peer is protected, False otherwise.
        """
        return await self._rpc.call("p2p.IsProtected", (peer_id, tag))

    async def list_blocked_peers(self) -> list[str]:
        """ Returns a list of blocked peers.

        Returns:
            list[str]: A list of blocked peer IDs.
        """
        return await self._rpc.call("p2p.ListBlockedPeers")

    async def nat_status(self) -> Reachability:
        """ Returns the current NAT status.

        Returns:
            Reachability: NAT reachability status.
        """
        return await self._rpc.call("p2p.NATStatus")

    async def peer_info(self, peer_id: str, *, deserializer: Callable | None = None) -> AddrInfo:
        """ Returns a small slice of information Peerstore has on the given peer.

        Args:
            peer_id (str): The ID of the peer.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.AddrInfo.deserializer`.

        Returns:
            AddrInfo: Address information of the peer.
        """

        deserializer = deserializer if deserializer is not None else AddrInfo.deserializer

        return await self._rpc.call("p2p.PeerInfo", (peer_id,), deserializer)

    async def peers(self) -> list[str]:
        """ Returns connected peers.

        Returns:
            list[str]: List of connected peer IDs.
        """
        return await self._rpc.call("p2p.Peers")

    async def protect(self, peer_id: str, tag: str) -> None:
        """ Adds a peer to the list of peers who have a bidirectional peering agreement
        that they are protected from being trimmed, dropped or negatively scored.

        Args:
            peer_id (str): The ID of the peer.
            tag (str): Protection tag.
        """
        await self._rpc.call("p2p.Protect", (peer_id, tag))

    async def pub_sub_peers(self, topic: str) -> list[str]:
        """ Returns the peer IDs of the peers joined on the given topic.

        Args:
            topic (str): The PubSub topic to query.

        Returns:
            list[str]: A list of peer IDs that are joined on the specified topic.
        """
        return await self._rpc.call("p2p.PubSubPeers", (topic,))

    async def pub_sub_topics(self) -> list[str] | None:
        """ Reports current PubSubTopics the node participates in.

        Returns:
            list[str] | None: A list of topic names if available, otherwise None.
        """
        return await self._rpc.call("p2p.PubSubTopics")

    async def resource_state(self, *, deserializer: Callable | None = None) -> ResourceManagerStat:
        """ Returns the state of the resource manager.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.p2p.ResourceManagerStat.deserializer`.

        Returns:
            ResourceManagerStat: Resource manager state.
        """

        deserializer = deserializer if deserializer is not None else ResourceManagerStat.deserializer

        return await self._rpc.call("p2p.ResourceState", (), deserializer)

    async def unblock_peer(self, peer_id: str) -> None:
        """ Removes a peer from the set of blocked peers.

        Args:
            peer_id (str): The ID of the peer to unblock.
        """
        await self._rpc.call("p2p.UnblockPeer", (peer_id,))

    async def unprotect(self, peer_id: str, tag: str) -> bool:
        """ Removes a peer from the list of peers who have a bidirectional peering agreement that
        they are protected from being trimmed, dropped or negatively scored, returning a bool
        representing whether the given peer is protected or not.

        Args:
            peer_id (str): The ID of the peer.
            tag (str): Protection tag.

        Returns:
            bool: True if the peer remains protected, False otherwise.
        """
        return await self._rpc.call("p2p.Unprotect", (peer_id, tag))
