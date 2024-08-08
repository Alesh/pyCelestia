from celestia import BlobSubmitResult
from celestia.models import Blob, Namespace


def test_BlobSubmitResult():
    raw = {
        "height": 252607,
        "commitment": "0MFhYKQUi2BU+U1jxPzG7QY2BVV1lb3kiU+zAK7nUiY="
    }
    bsr = BlobSubmitResult(**raw)
    assert bsr.height == 252607
    assert isinstance(bsr.commitment, bytes)


def test_Blob():
    raw = {
        "namespace": "AAAAAAAAAAAAAAAAAAAAAAAAAAECAwQFBgcICRA=",
        "data": "VGhpcyBpcyBhbiBleGFtcGxlIG9mIHNvbWUgYmxvYiBkYXRh",
        "commitment": "AD5EzbG0/EMvpw0p8NIjMVnoCP4Bv6K+V6gjmwdXUKU=",
        "share_version": 0,
        "index": -1
    }
    blob = Blob(**raw)
    assert blob.namespace == Namespace(0x01020304050607080910)
    assert blob.data == b'This is an example of some blob data'
    assert isinstance(blob.commitment, bytes)


def test_big_Blob():
    data = b'0123456789ABCDEF' * 0xFFFF
    blob = Blob(0x01020304050607080910, data)
    assert isinstance(blob.commitment, bytes)
