import typing as t

from celestia.rpc import Error


class BlobNotFound(Error):
    """ Raised when a blob cannot be found. """


class WrongBlockHeight(Error):
    """ Raised when a block height is not correct. """


class InsufficientFee(Error):
    """ Raised when a transaction is attempted with insufficient funds. """


def clarifycator(exc: Exception, *expected: t.Type[Exception]):
    msg = str(exc)
    if isinstance(exc, Error):
        try:
            if exc.code == -32001:
                if 'blob: not found' in msg:
                    raise BlobNotFound(exc.code, msg) from exc
                elif 'header: given height' in msg or 'header/store: height must' in msg:
                    raise WrongBlockHeight(exc.code, msg) from exc
                elif 'insufficient fee' in msg:
                    raise InsufficientFee(exc.code, msg) from exc
            if exc.code == -32700:
                raise ValueError("Some parameters are wrong") from exc
        except Error as exc:
            if isinstance(exc, expected):
                return
            raise exc
    raise exc
