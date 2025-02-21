from typing import Callable

from celestia.types import Namespace
from celestia.types.header import ExtendedHeader
from celestia.types.share import ExtendedDataSquare, NamespaceData, SampleCoords, GetRangeResult
from ._RPC import Wrapper


class ShareClient(Wrapper):
    """ Client for interacting with Celestia's Share API."""

    async def get_eds(self, height: int, *, deserializer: Callable | None = None) -> ExtendedDataSquare:
        """ Gets the full EDS identified by the given extended header.

        Args:
            height (int): The block height.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.share.ExtendedDataSquare.deserializer`.

        Returns:
            ExtendedDataSquare: The retrieved EDS object.
        """

        deserializer = deserializer if deserializer is not None else ExtendedDataSquare.deserializer

        return await self._rpc.call("share.GetEDS", (height,), deserializer)

    async def get_namespace_data(self, height: int, namespace: Namespace, *,
                                 deserializer: Callable | None = None) -> list[NamespaceData]:
        """ Gets all shares from an EDS within the given namespace. Shares are returned
        in a row-by-row order if the namespace spans multiple rows.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace identifier.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[NamespaceData]: A list of NamespaceData objects or [] if not found.
        """

        def deserializer_(result):
            if result is not None:
                return [NamespaceData(**data) for data in result]
            else:
                return []

        deserializer = deserializer if deserializer is not None else deserializer_

        return await self._rpc.call("share.GetNamespaceData", (height, Namespace(namespace)), deserializer)

    async def get_range(self, height: int, start: int, end: int, *,
                        deserializer: Callable | None = None) -> GetRangeResult:
        """ Gets a list of shares and their corresponding proof.

        Args:
            height (int): The block height.
            start (int): The starting index.
            end (int): The ending index.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.share.GetRangeResult.deserializer`.

        Returns:
            GetRangeResult: The retrieved range result containing shares and proof.
        """

        deserializer = deserializer if deserializer is not None else GetRangeResult.deserializer

        return await self._rpc.call("share.GetRange", (height, start, end), deserializer)

    async def get_samples(self, header: ExtendedHeader, indices: list[SampleCoords]) -> list[str]:
        """ Gets sample for given indices.

        Args:
            header (ExtendedHeader): The extended header.
            indices (list[SampleCoords]): A list of sample coordinates.

        Returns:
            list[str]: A list of retrieved samples or [] if not found.
        """
        return await self._rpc.call("share.GetSamples", (header, indices,),
                                    lambda result: result if result is not None else [])

    async def get_share(self, height: int, row: int, col: int) -> str:
        """ Gets a Share by coordinates in EDS.

        Args:
            height (int): The block height.
            row (int): The row index.
            col (int): The column index.

        Returns:
            str: The retrieved share.
        """
        return await self._rpc.call("share.GetShare", (height, row, col,))

    async def get_available(self, height: int) -> bool:
        """ Subjectively validates if Shares committed to the given ExtendedHeader are available on the Network.

        Args:
            height (int): The block height.

        Returns:
            bool: True if shares are available, False otherwise.
        """
        return await self._rpc.call("share.SharesAvailable", (height,))
