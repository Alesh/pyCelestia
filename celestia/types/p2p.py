from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class ResourceManagerStat:
    """Represents the statistics of a resource manager, including system, transient,
    services, protocols, and peers.

    Attributes:
        system (dict): System data.
        transient (dict): Transient data.
        services (dict): Service data.
        protocols (dict): Protocol data.
        peers (dict): Peer data.
    """

    system: dict[str, Any]
    transient: dict[str, Any]
    services: dict[str, Any]
    protocols: dict[str, Any]
    peers: dict[str, Any]

    def __init__(self, System, Transient, Services, Protocols, Peers):
        self.system = System
        self.transient = Transient
        self.services = Services
        self.protocols = Protocols
        self.peers = Peers

    @staticmethod
    def deserializer(result: dict) -> "ResourceManagerStat":
        """Deserialize a dictionary into a ResourceManagerStat instance.

        Args:
            result (dict): The dictionary representation of a ResourceManagerStat.

        Returns:
            ResourceManagerStat: A deserialized ResourceManagerStat object.
        """
        if result is not None:
            return ResourceManagerStat(**result)


@dataclass
class BandwidthStats:
    """Represents the statistics related to bandwidth, including total inbound/outbound
    traffic and rates for both directions.

    Attributes:
        total_in (int): Total inbound bandwidth.
        total_out (int): Total outbound bandwidth.
        rate_in (float): Inbound traffic rate.
        rate_out (float): Outbound traffic rate.
    """

    total_in: int
    total_out: int
    rate_in: float
    rate_out: float

    def __init__(self, TotalIn, TotalOut, RateIn, RateOut):
        self.total_in = TotalIn
        self.total_out = TotalOut
        self.rate_in = RateIn
        self.rate_out = RateOut

    @staticmethod
    def deserializer(result: dict) -> "BandwidthStats":
        """Deserialize a dictionary into a BandwidthStats instance.

        Args:
            result (dict):  The dictionary representation of a BandwidthStats.

        Returns:
            BandwidthStats: A deserialized BandwidthStats object.
        """
        if result is not None:
            return BandwidthStats(**result)


@dataclass
class AddrInfo:
    """Represents the address information with an identifier and associated addresses.

    Attributes:
        id (str): The unique identifier for the address.
        addrs (list): A list of addresses associated with the identifier.
    """

    id: str
    addrs: list[str]

    def __init__(self, ID, Addrs):
        self.id = ID
        self.addrs = Addrs

    @staticmethod
    def deserializer(result: dict) -> "AddrInfo":
        """Deserialize a dictionary into an AddrInfo instance.

        Args:
           result (dict): The dictionary representation of a AddrInfo.

        Returns:
           AddrInfo: A deserialized AddrInfo object.
        """
        if result is not None:
            return AddrInfo(**result)


class Connectedness(Enum):
    """Enum representing the connection status.

    Attributes:
        NOT_CONNECTED: Represents a disconnected state.
        CONNECTED: Represents a connected state.
    """

    NOT_CONNECTED = 0
    CONNECTED = 1


class Reachability(Enum):
    """Enum representing the reachability state of an address.

    Attributes:
       Unknown: Unknown reachability state.
       Public: The address is publicly reachable.
       Private: The address is privately reachable.
    """

    Unknown = 0
    Public = 1
    Private = 2
