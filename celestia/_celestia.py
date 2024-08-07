def default_gas_price() -> float:
    """ Retrieves the default gas price. """
    raise NotImplementedError


def make_commitment(namespace: bytes, data: bytes, share_version: int) -> bytes:
    """ Generate the share commitment from the given blob data. """
    raise NotImplementedError
