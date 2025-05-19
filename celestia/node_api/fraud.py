from collections.abc import AsyncIterator

from _jsonrpc import Wrapper


class FraudClient(Wrapper):
    """Client for interacting with Celestia's Fraud API."""

    async def get(self, proof_type: str) -> list[dict[str, str]]:
        """Fetches fraud proofs from the disk by its type.

        Args:
            proof_type (str): The type of fraud proof to retrieve.

        Returns:
            list[dict[str, str]]: A list of fraud proofs.
        """
        return await self._rpc.call("fraud.Get", (proof_type,))

    async def subscribe(self, proof_type: str) -> AsyncIterator[dict[str, str]]:
        """Allows to subscribe on a Proof pub sub topic by its type.

        Args:
            proof_type (str): The type of fraud proof to subscribe to.

        Yields:
            dict[str, str]: A dictionary containing fraud proof data.
        """
        return self._rpc.iter("fraud.Subscribe", (proof_type,))
