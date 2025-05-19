from dataclasses import dataclass

from celestia.types.blob import RowProof, Proof
from celestia.types.common import Base64, Namespace


@dataclass
class SampleCoords:
    """A class representing coordinates for a sample, specifically the row and column.

    Attributes:
        row (int): The row index of the sample.
        col (int): The column index of the sample.
    """

    row: int
    col: int


@dataclass
class ShareProof:
    """A class representing a share proof, which consists of a namespace ID,
    namespace version, row proof, data, and share proofs.

    Attributes:
        namespace_id (Namespace): The namespace identifier.
        namespace_version (int): The version of the namespace.
        row_proof (RowProof): The proof related to the row.
        data (tuple[Base64, ...]): The data associated with the share proof.
        share_proofs (tuple[Proof, ...]): Additional share proofs.
    """

    namespace_id: Namespace
    namespace_version: int
    row_proof: RowProof
    data: tuple[Base64, ...]
    share_proofs: tuple[Proof, ...]

    def __init__(
        self,
        namespace_id: Namespace,
        namespace_version: int,
        row_proof: dict,
        data: tuple[Base64, ...],
        share_proofs: list[dict],
    ):
        self.namespace_id = Namespace.ensure_type(namespace_id)
        self.namespace_version = int(namespace_version)
        self.row_proof = RowProof(**row_proof)
        self.data = tuple(data_unit for data_unit in data)
        self.share_proofs = tuple(Proof(**share_proof) for share_proof in share_proofs)


@dataclass
class RawShare:
    """A class representing a raw share"""

    data: Base64
    is_parity: bool = False


@dataclass
class RawSample:
    """A class representing a raw sample."""

    share: RawShare
    proof: Proof

    def __init__(self, share: RawShare | dict, proof: Proof | dict):
        self.share = share if isinstance(share, RawShare) else RawShare(**share)
        self.proof = proof if isinstance(proof, Proof) else Proof(**proof)


@dataclass
class GetRangeResult:
    """
    A class representing the result of a range retrieval, including shares and proof.

    Attributes:
        shares (tuple[Base64, ...]): The shares related to the range.
        proof (ShareProof): The proof associated with the range retrieval.
    """

    shares: tuple[Base64, ...]
    proof: ShareProof

    def __init__(self, Shares: list[Base64], Proof: dict):
        self.shares = tuple(share for share in Shares)
        self.proof = ShareProof(**Proof)

    @staticmethod
    def deserializer(result: dict) -> "GetRangeResult":
        """Deserialize a result dictionary into a GetRangeResult object.

        Args:
            result (dict): The dictionary representation of a GetRangeResult.

        Returns:
            GetRangeResult: The deserialized GetRangeResult object.
        """
        if result is not None:
            return GetRangeResult(**result)


@dataclass
class ExtendedDataSquare:
    """A class representing an extended data square, including the data square and codec.

    Attributes:
        data_square (tuple[Base64, ...]): The data square.
        codec (str): The codec used for the data.
    """

    data_square: tuple[Base64, ...]
    codec: str

    @staticmethod
    def deserializer(result: dict) -> "ExtendedDataSquare":
        """Deserialize a result dictionary into an ExtendedDataSquare object.

        Args:
            result (dict): The dictionary representation of a ExtendedDataSquare.

        Returns:
            ExtendedDataSquare: The deserialized ExtendedDataSquare object.
        """
        if result is not None:
            return ExtendedDataSquare(**result)


@dataclass
class NamespaceData:
    """A class representing namespace data, consisting of shares and proof.

    Attributes:
        shares (tuple[Base64, ...]): The shares related to the namespace.
        proof (Proof): The proof associated with the namespace data.
    """

    shares: tuple[Base64, ...]
    proof: Proof

    def __init__(self, shares: list[Base64], proof: dict):
        self.shares = tuple(share for share in shares)
        self.proof = Proof(**proof)

    @staticmethod
    def deserializer(result: dict) -> "NamespaceData":
        """Deserialize a result dictionary into a NamespaceData object.

        Args:
            result (dict): The dictionary representation of a NamespaceData.

        Returns:
            NamespaceData: The deserialized NamespaceData object.
        """
        if result is not None:
            return NamespaceData(**result)
