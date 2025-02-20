from dataclasses import dataclass

from celestia._celestia import types as ext  # noqa

from celestia.types.common_types import Blob, Base64, Namespace, Commitment


@dataclass
class SubmitBlobResult:
    """ Represents the result of submitting a blob to the Celestia network.

    Attributes:
        height (int): The block height at which the blob was submitted.
        commitments (tuple[Commitment, ...]): Commitments associated with the submitted blob.
    """
    height: int
    commitments: tuple[Commitment, ...]


@dataclass
class SubscriptionBlobResult:
    """ Represents the result of a subscription to blobs in the Celestia network.

    Attributes:
        height (int): The block height of the retrieved blobs.
        blobs (tuple[Blob, ...]): The list of blobs retrieved from the subscription.
    """
    height: int
    blobs: tuple[Blob, ...]


@dataclass
class Proof:
    """ Represents a Merkle proof used for verifying data inclusion in Celestia.

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
    """ Represents an entry in a row proof, used for verifying inclusion in a specific row of a Merkle tree.

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
    """ Represents a proof for a row in a Merkle tree.

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
    """ Represents a proof of commitment in Celestia, verifying that a namespace is correctly included.

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

    def __init__(self, namespace_id, namespace_version, row_proof, subtree_root_proofs, subtree_roots):
        self.namespace_id = Namespace.ensure_type(namespace_id)
        self.namespace_version = int(namespace_version)
        self.row_proof = RowProof(**row_proof)
        self.subtree_root_proofs = tuple(Proof(**subtree_root_proof) for subtree_root_proof in subtree_root_proofs)
        self.subtree_roots = tuple(subtree_root for subtree_root in subtree_roots)

    @staticmethod
    def deserializer(result: dict) -> 'CommitmentProof':
        """ Deserializes a commitment proof from a given result.

        Args:
            result (dict): The dictionary representation of a CommitmentProof.

        Returns:
            A deserialized CommitmentProof object.
        """
        if result is not None:
            return CommitmentProof(**result)
