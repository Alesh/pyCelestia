from typing import Callable

from celestia.types.das import SamplingStats
from ._RPC import Wrapper


class DasClient(Wrapper):
    """ Client for interacting with Celestia's Das API."""

    async def sampling_stats(self, *, deserializer: Callable | None = None) -> SamplingStats:
        """ Returns the current statistics over the DA sampling process.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.das.SamplingStats.deserializer`.

        Returns:
            SamplingStats: The current sampling statistics.
        """

        deserializer = deserializer if deserializer is not None else SamplingStats.deserializer

        return await self._rpc.call("das.SamplingStats", (), deserializer)

    async def wait_catch_up(self) -> None:
        """ Blocks until DASer finishes catching up to the network head.

        Returns:
            None
        """
        return await self._rpc.call("das.WaitCatchUp")
