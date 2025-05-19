from dataclasses import dataclass
from typing import Optional

from celestia._celestia import types as ext  # noqa

from celestia.types.common import Commitment, Namespace, Base64, Address


@dataclass
class Blob:
    """Represents a Celestia blob.

    A blob is a chunk of data stored on Celestia. Each blob is associated with
    a namespace and a cryptographic commitment to ensure data integrity.

    Attributes:
        namespace (Namespace): The namespace under which the blob is stored.
        data (Base64): The actual blob data.
        commitment (Commitment): The cryptographic commitment for the blob.
        share_version (int): The version of the share encoding used.
        index (int | None): The index of the blob in the block (optional).
        signer (Base64 | None): The signer (author) of the blob (optional).
    """

    namespace: Namespace
    data: Base64
    commitment: Commitment
    share_version: int
    index: int | None = None
    signer: Address | None = None

    def __init__(
        self,
        namespace: Namespace | str | bytes,
        data: Base64 | str | bytes,
        *,
        commitment: Commitment | str | bytes | None = None,
        share_version: int | None = None,
        index: int | None = None,
        signer: Address | str | bytes | None = None,
    ) -> None:
        share_version = (
            (1 if signer is not None else 0) if share_version is None else share_version
        )
        self.namespace = Namespace.ensure_type(namespace)
        self.data = Base64.ensure_type(data)
        self.signer = Address.ensure_type(signer) if signer is not None else None
        kwargs = ext.normalize_blob(self.namespace, self.data, self.signer)
        if commitment is not None:
            commitment = Commitment.ensure_type(commitment)
            if commitment != kwargs["commitment"]:
                raise ValueError("Wrong commitment")
        self.commitment = Commitment.ensure_type(kwargs["commitment"])
        if share_version is not None and share_version != kwargs["share_version"]:
            raise ValueError(f"Wrong share version; should be {kwargs['share_version']} ")
        self.share_version = kwargs["share_version"]
        if index is not None and index < 0:
            raise ValueError("Wrong index")
        self.index = index

    @staticmethod
    def deserializer(result: dict) -> Optional["Blob"]:
        """Deserializes a dictionary into a Blob object.

        Args:
            result: The dictionary representation of a Blob.

        Returns:
            A deserialized Blob object.
        """
        if result is not None:
            return Blob(**result)
        return None


@dataclass
class SubmitBlobResult:
    """Represents the result of submitting a blob to the Celestia network.

    Attributes:
        height (int): The block height at which the blob was submitted.
        commitments (tuple[Commitment, ...]): Commitments associated with the submitted blob.
    """

    height: int
    commitments: tuple[Commitment, ...]


@dataclass
class SubscriptionBlobResult:
    """Represents the result of a subscription to blobs in the Celestia network.

    Attributes:
        height (int): The block height of the retrieved blobs.
        blobs (tuple[Blob, ...]): The list of blobs retrieved from the subscription.
    """

    height: int
    blobs: tuple[Blob, ...]


@dataclass
class Proof:
    """Represents a Merkle proof used for verifying data inclusion in Celestia.

    Attributes:
        end (int): The end index of the proof range.
        nodes (tuple[Base64, ...]): The nodes forming the Merkle proof.
        start (int | None): The start index of the proof range (optional).
        is_max_namespace_ignored (bool | None): Flag indicating if max namespace check is ignored (optional).
    """

    end: int
    nodes: tuple[Base64, ...]
    start: int | None
    is_max_namespace_ignored: bool | None

    def __init__(self, nodes, end, is_max_namespace_ignored=None, start=None):
        self.start = start
        self.nodes = tuple(node for node in nodes)
        self.end = end
        self.is_max_namespace_ignored = is_max_namespace_ignored


@dataclass
class RowProofEntry:
    """Represents an entry in a row proof, used for verifying inclusion in a specific row of a Merkle tree.

    Attributes:
        index (int | None): The index of the leaf in the row.
        total (int): The total number of leaves in the row.
        leaf_hash (Base64): The hash of the leaf.
        aunts (tuple[Base64, ...]): The sibling hashes used in the proof.
    """

    index: int | None
    total: int
    leaf_hash: Base64
    aunts: tuple[Base64, ...]

    def __init__(self, leaf_hash, aunts, total, index=None):
        self.leaf_hash = leaf_hash
        self.aunts = tuple(aunt for aunt in aunts)
        self.total = total
        self.index = index


@dataclass
class RowProof:
    """Represents a proof for a row in a Merkle tree.

    Attributes:
        start_row (int | None): The starting row index of the proof.
        end_row (int | None): The ending row index of the proof.
        row_roots (tuple[Base64, ...]): The root hashes of the rows.
        proofs (tuple[RowProofEntry, ...]): The proof entries for the row.
    """

    start_row: int | None
    end_row: int | None
    row_roots: tuple[Base64, ...]
    proofs: tuple[RowProofEntry, ...]

    def __init__(self, row_roots, proofs, end_row=None, start_row=None):
        self.row_roots = tuple(row_root for row_root in row_roots)
        self.proofs = tuple(RowProofEntry(**proof) for proof in proofs)
        self.end_row = end_row
        self.start_row = start_row


@dataclass
class CommitmentProof:
    """Represents a proof of commitment in Celestia, verifying that a namespace is correctly included.

    Attributes:
        namespace_id (Namespace): The namespace identifier.
        namespace_version (int): The version of the namespace.
        row_proof (RowProof): The proof for the rows containing the namespace.
        subtree_root_proofs (tuple[Proof, ...]): Proofs for verifying subtree roots.
        subtree_roots (tuple[Base64, ...]): The roots of the subtrees.
    """

    namespace_id: Namespace
    namespace_version: int
    row_proof: RowProof
    subtree_root_proofs: tuple[Proof, ...]
    subtree_roots: tuple[Base64, ...]

    def __init__(
        self, namespace_id, namespace_version, row_proof, subtree_root_proofs, subtree_roots
    ):
        self.namespace_id = Namespace.ensure_type(namespace_id)
        self.namespace_version = int(namespace_version)
        self.row_proof = RowProof(**row_proof)
        self.subtree_root_proofs = tuple(
            Proof(**subtree_root_proof) for subtree_root_proof in subtree_root_proofs
        )
        self.subtree_roots = tuple(subtree_root for subtree_root in subtree_roots)

    @staticmethod
    def deserializer(result: dict) -> Optional["CommitmentProof"]:
        """Deserializes a commitment proof from a given result.

        Args:
            result (dict): The dictionary representation of a CommitmentProof.

        Returns:
            A deserialized CommitmentProof object.
        """
        if result is not None:
            return CommitmentProof(**result)
        return None
