import typing as t
from base64 import b64decode, b64encode

from celestia._celestia import types as ext  # noqa


class Base64(bytes):
    """Represents a byte string that supports Base64 encoding and decoding.

    This class ensures that the stored data is always in bytes and provides
    Base64 encoding/decoding when converting to and from strings.
    """

    def __new__(cls, value: str | bytes):
        if isinstance(value, str):
            value = b64decode(value)
        if value is None:
            return None
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return b64encode(self).decode("ascii")

    @classmethod
    def ensure_type(cls, value):
        """Ensures the value is an instance of Base64.

        Args:
            value (str | bytes | Base64): The value to convert.

        Returns:
            Base64: A valid Base64 instance.
        """
        if isinstance(value, cls):
            return value
        return cls(value)


class Namespace(Base64):
    """Represents a Celestia namespace.

    A namespace is a unique identifier for blobs stored on the Celestia network.
    It is used to segregate data based on different applications or use cases.
    """

    def __new__(cls, value: str | bytes):
        value = super().__new__(cls, value)
        value = ext.normalize_namespace(value)
        return super().__new__(cls, value)


class Commitment(Base64):
    """Represents a Celestia blob commitment.

    A commitment is a cryptographic proof that ensures data integrity and allows
    verification of whether a blob has been correctly included in a block.
    """


class TxConfig(t.TypedDict):
    """Represents a transaction configuration for submitting transactions to Celestia.

    Attributes:
        signer_address (str | None): The address of the transaction signer.
        is_gas_price_set (bool | None): Whether a custom gas price is set.
        key_name (str | None): The name of the key used for signing.
        gas_price (float | None): The gas price for the transaction.
        gas (int | None): The amount of gas to use.
        fee_granter_address (str | None): Address of the fee granter (if applicable).
    """

    signer_address: bool | str | None
    is_gas_price_set: bool | None
    key_name: str | None
    gas_price: float | None
    gas: int | None
    fee_granter_address: str | None


class Address(Base64):
    """Represents a address that supports Base64 encoding and decoding.

    This class ensures that the stored address is always in bytes and provides
    Base64 encoding/decoding when converting to and from strings.
    """

    def __new__(cls, value: str | bytes):
        if isinstance(value, str) and value.startswith("celestia"):
            value = ext.address2bytes(value)
        return super().__new__(cls, value)
