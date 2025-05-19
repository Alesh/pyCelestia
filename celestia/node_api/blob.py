from collections.abc import AsyncIterator
from dataclasses import asdict
from functools import wraps
from typing import Callable

from celestia._celestia import types  # noqa

from _jsonrpc import Wrapper
from celestia.types import Namespace, TxConfig, Commitment, Unpack
from celestia.types.blob import (
    Blob,
    SubmitBlobResult,
    SubscriptionBlobResult,
    Proof,
    CommitmentProof,
)


def handle_blob_error(func):
    """Decorator to handle blob-related errors."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionError as e:
            if "blob: not found" in e.args[1].body["message"].lower():
                return None
            raise

    return wrapper


class BlobClient(Wrapper):
    """Client for interacting with Celestia's Blob API."""

    @handle_blob_error
    async def get(
        self,
        height: int,
        namespace: Namespace,
        commitment: Commitment,
        *,
        deserializer: Callable | None = None,
    ) -> Blob | None:
        """Retrieves the blob by commitment under the given namespace and height.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the blob.
            commitment (Commitment): The commitment of the blob.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.common_types.Blob.deserializer`.

        Returns:
            Blob | None: The retrieved blob, or None if not found.
        """

        deserializer = deserializer if deserializer is not None else Blob.deserializer

        return await self._rpc.call(
            "blob.Get", (height, Namespace(namespace), Commitment(commitment)), deserializer
        )

    async def get_all(
        self,
        height: int,
        namespace: Namespace,
        *namespaces: Namespace,
        deserializer: Callable | None = None,
    ) -> list[Blob] | None:
        """Returns all blobs under the given namespaces at the given height. If all blobs were
        found without any errors, the user will receive a list of blobs. If the BlobService couldn't
        find any blobs under the requested namespaces, the user will receive an empty list of blobs
        along with an empty error. If some of the requested namespaces were not found, the user will receive
        all the found blobs and an empty error. If there were internal errors during some of the requests, the
        user will receive all found blobs along with a combined error message. All blobs will preserve the order
        of the namespaces that were requested.

        Args:
            height (int): The block height.
            namespace (Namespace): The primary namespace of the blobs.
            namespaces (Namespace): Additional namespaces to query for blobs.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[Blob]: The list of blobs or [] if not found.
        """

        def deserializer_(result) -> list["Blob"]:
            if result is not None:
                return [Blob(**kwargs) for kwargs in result]
            else:
                return []

        deserializer = deserializer if deserializer is not None else deserializer_
        namespaces = tuple(Namespace(namespace) for namespace in (namespace, *namespaces))

        return await self._rpc.call("blob.GetAll", (height, namespaces), deserializer)

    async def submit(
        self,
        blob: Blob,
        *blobs: Blob,
        deserializer: Callable | None = None,
        **options: Unpack[TxConfig],
    ) -> SubmitBlobResult:
        """Sends Blobs and reports the height in which they were included. Allows sending
        multiple Blobs atomically synchronously. Uses default wallet registered on the Node.

        Args:
            blob (Blob): The main blob to submit.
            blobs (Blob): Additional blobs to submit.
            deserializer (Callable | None): Custom deserializer. Defaults to None.
            options (TxConfig): Additional configuration options.

        Returns:
            SubmitBlobResult: The result of the submission, including the height.

        Notes:
            If there is a `signer_address` in the options and its value is `True` or matches your current address,
            then your current address will be used for all blobs as the `signer`. Note that in this case, all blobs
            will be changed to have `share_version`" equal to 1, and their `commitment` will also be changed.
        """
        blobs_ = [blob, *blobs]

        def deserializer_(height):
            if height is not None:
                return SubmitBlobResult(height, tuple(blob.commitment for blob in blobs_))
            return None

        deserializer = deserializer if deserializer is not None else deserializer_
        if signer_address := options.get("signer_address"):
            signer_address_ = await self._rpc.call("state.AccountAddress")
            if signer_address is True:
                options["signer_address"] = signer_address_
            elif signer_address != signer_address_:
                raise ValueError(f"`signer_address` does not match the current account address")
            blobs_.clear()
            for blob in (blob, *blobs):
                if blob.signer is not None and blob.signer != signer_address_:
                    raise ValueError(
                        f"`signer_address` of blob does not match the current account address"
                    )
                else:
                    blob = Blob(
                        **dict(
                            asdict(blob), signer=signer_address_, commitment=None, share_version=1
                        )
                    )
                blobs_.append(blob)
        return await self._rpc.call("blob.Submit", (blobs_, options), deserializer)

    @handle_blob_error
    async def get_commitment_proof(
        self,
        height: int,
        namespace: Namespace,
        commitment: Commitment,
        *,
        deserializer: Callable | None = None,
    ) -> CommitmentProof | None:
        """Generates a commitment proof for a share commitment.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the commitment.
            commitment (Commitment): The commitment to generate proof for.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.blob.CommitmentProof.deserializer`.

        Returns:
            CommitmentProof | None: The commitment proof, or None if not found.
        """

        deserializer = deserializer if deserializer is not None else CommitmentProof.deserializer

        return await self._rpc.call(
            "blob.GetCommitmentProof",
            (height, Namespace(namespace), Commitment(commitment)),
            deserializer,
        )

    async def get_proof(
        self,
        height: int,
        namespace: Namespace,
        commitment: Commitment,
        *,
        deserializer: Callable | None = None,
    ) -> list[Proof] | None:
        """Retrieves proofs in the given namespaces at the given height by commitment.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the proof.
            commitment (Commitment): The commitment to generate the proof for.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[Proof]: A list of proofs or [] if not found.
        """

        def deserializer_(result) -> list["Proof"]:
            if result is not None:
                return [Proof(**kwargs) for kwargs in result]

        deserializer = deserializer if deserializer is not None else deserializer_
        try:
            return await self._rpc.call(
                "blob.GetProof",
                (height, Namespace(namespace), Commitment(commitment)),
                deserializer,
            )
        except ConnectionError as e:
            if "blob: not found" in e.args[1].body["message"].lower():
                return []
            raise

    async def included(
        self, height: int, namespace: Namespace, proof: Proof, commitment: Commitment
    ) -> bool:
        """Checks whether a blob's given commitment(Merkle subtree root) is
        included at given height and under the namespace.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the blob.
            proof (Proof): The proof to check.
            commitment (Commitment): The commitment to check inclusion for.

        Returns:
            bool: True if included, False otherwise.
        """

        return await self._rpc.call(
            "blob.Included", (height, Namespace(namespace), proof, Commitment(commitment))
        )

    async def subscribe(
        self, namespace: Namespace, *, deserializer: Callable | None = None
    ) -> AsyncIterator[SubscriptionBlobResult | None]:
        """Subscribe to published blobs from the given namespace as they are included.

        Args:
            namespace (Namespace): The namespace to subscribe to.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Yields:
            SubscriptionBlobResult: A result with the blob information.

        """

        def deserializer_(result):
            height = result["Height"]
            blobs = result.get("Blobs")
            if blobs is not None:
                return SubscriptionBlobResult(height, tuple(Blob(**kwargs) for kwargs in blobs))

        deserializer = deserializer if deserializer is not None else deserializer_

        async for subs_blob_result in self._rpc.iter(
            "blob.Subscribe", (Namespace(namespace),), deserializer
        ):
            if subs_blob_result is not None:
                yield subs_blob_result
